import json
import os
import re
from datetime import datetime, timezone

date_format = "%Y-%m-%d %H:%M:%S %Z"
manifest_filename = "{manifest_filename}"


class Manifest:
    def __init__(
        self, instance_uuid, path_override: str = None, name_override: str = None
    ):
        self.instance_uuid = instance_uuid

        self.filename = name_override or manifest_filename

        path = path_override or __file__
        if "." in path:
            path = os.path.split(path)[0]
        self.basepath = path

        self.runner_mode = False  # set True by runners, disables printing

    def now(self) -> str:
        return datetime.strftime(datetime.now(timezone.utc), date_format)

    def to_timestamp(self, timestring: str) -> int:
        if "UTC" in timestring:
            timestring = timestring.replace("UTC", "+0000")

        try:
            dt = datetime.strptime(timestring, date_format)
        except ValueError:
            try:
                dt = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                dt = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S")

        return int(dt.timestamp())

    @property
    def path(self):
        return os.path.join(self.basepath, self.filename)

    def get_data(self, path: str = None) -> list:
        if path is None:
            path = self.path
        if not os.path.exists(path):
            return []
        with open(path) as o:
            data = o.readlines()
        return data

    def write(self, string: str):
        string = f"{self.now()} [{self.instance_uuid}] {string.strip()}\n"
        with open(self.path, "a+") as o:
            o.write(string)

    def get(self, uuid: str) -> list:
        """Gets all lines that correspond to uuid"""
        # we need to "recreate" the log from the parsed output,
        # since parse_log handles multiline entries
        log = []
        for entry in self.parse_log()["log"].get(uuid, []):
            # the timestamp here is always from a UTC string
            dt = datetime.fromtimestamp(entry[0]).astimezone(timezone.utc)
            timestring = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            log.append(f"{timestring} [uuid_a] {entry[1]}")

        return log

    def parse_log(
        self, path: str = None, string: str = None, cutoff: int = None
    ) -> dict:
        """
        Convert the log into a dict of {uuid: [time, log]}

        Args:
            path: Override filepath
            string: Override file read with string input
            cutoff: Only consider events after this timestamp
        """
        if string is not None:
            data = string.split("\n")
        else:
            data = self.get_data(path)

        def add_to_output(output: dict, uuid: str, timestamp: int, cache: list) -> None:
            if len(cache) == 0:
                return
            content = "\n".join(cache)

            add_to = "log"
            # first split off stdout/stderr section using maxsplit=1
            # then take the last section with [-1]
            # this leaves an additional single space that should be dropped with [1:]
            # strip is dangerous, since it drops _all_ whitespace
            if content.startswith("[stdout]"):
                add_to = "stdout"
                content = content.rsplit("[stdout]", maxsplit=1)[-1][1:]
            elif content.startswith("[stderr]"):
                add_to = "stderr"
                content = content.rsplit("[stderr]", maxsplit=1)[-1][1:]

            try:
                output[add_to][uuid].append((timestamp, content.rstrip()))
            except KeyError:
                output[add_to][uuid] = [(timestamp, content.rstrip())]

        date_regex = re.compile(r"\d{4}-\d{2}-\d{2}")

        cache = []
        output = {"log": {}, "stdout": {}, "stderr": {}}

        uuid = None
        ts = 0
        for line in data:
            if re.match(date_regex, line):
                add_to_output(output, uuid, ts, cache)
                cache = []

                ts = self.to_timestamp(line[: line.index("[")].strip())

                if cutoff is not None and cutoff > ts:
                    continue

                uuid_index = line.index("]")

                uuid = line[25:uuid_index]
                # fmt: off
                content = line[uuid_index + 2:]
                # fmt: on

                cache.append(content.strip())

            else:  # continuation of a previous line, store it for later
                cache.append(line.strip())

        if len(cache) != 0:
            add_to_output(output, uuid, ts, cache)

        return output

    def last_time(self, state: str) -> dict:
        """Takes parsed log, returning the last time state appeared for each uuid"""
        data = self.parse_log()["log"]
        output = {}
        for uuid, log in data.items():
            if uuid not in output:
                output[uuid] = None
            for line in log:
                if line[1].strip().lower() == state.lower():
                    output[uuid] = line[0]

        if not self.runner_mode:
            print(json.dumps(output))
        return output


# DATASET_CONTENT #

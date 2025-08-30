import json
import hashlib
from typing import Any

from remotemanager.utils.format_iterable import format_iterable


def generate_uuid(string: Any) -> str:
    """
    Generates a UUID string from an input

    Args:
        string:
            input string
    Returns:
        (str) UUID
    """
    if not isinstance(string, str):
        try:
            string = json.dumps(string)
        except TypeError:
            string = format_iterable(string)  # slower, but reliable
    h = hashlib.sha256()
    h.update(bytes(string, "utf-8"))

    return str(h.hexdigest())


class UUIDMixin:
    """
    Stub class to add the ability for descendants to generate and store a uuid
    """

    _uuid = NotImplemented

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def short_uuid(self) -> str:
        return self.uuid[:8]

    def generate_uuid(self, input: Any) -> str:
        """
        Generates a uuid from the input, then assigns it to the _uuid property

        Returns:
            str:
                the uuid
        """
        uuid = generate_uuid(string=input)

        self._uuid = uuid

        return uuid

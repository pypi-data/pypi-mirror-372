"""Verbosity enables deeper verbose levels than True and False"""

from typing import Optional, Union

from remotemanager.storage.sendablemixin import SendableMixin


_default_level = 1


class Verbosity(SendableMixin):
    """
    Class to store verbosity information

    Initialise with Verbosity(level), where level is the integer level

    Printing can be requested with Verbose.print(msg, level)

    If the verbose level is set above `level`, the message will be printed

    args:
        level (int, bool, Verbosity):
            level above which to print
    """

    __slots__ = ["_level"]

    def __init__(self, level: Union[None, int, bool, "Verbosity"] = None):
        # create the _level property
        self._level = _default_level
        # use the property setter to set the level, since it sanitises the input
        self.level = level

    def __repr__(self) -> str:
        return f"Verbosity({self.level})"

    def __bool__(self) -> bool:
        return self.level != 0

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, level: Optional[Union[int, bool, "Verbosity"]]) -> None:
        if level is None:
            level = _default_level
        # see if the level passed is already a Verbose instance
        elif isinstance(level, Verbosity):
            level = level.value
        elif isinstance(level, bool):
            level = int(level)

        self._level = level

    def _prepare_other_for_comparison(self, other: object) -> Union[int, None]:
        """
        Convert the other verbosity to an int, if possible

        Args:
            other (object): The other verbosity to compare with

        Returns:
            (int, None): The level of the other verbosity, otherwise None
        """
        if isinstance(other, self.__class__):
            return other.level
        if isinstance(other, int):
            return other

    def __eq__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return False
        return self.level == other

    def __ne__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return True
        return self.level != other

    def __lt__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return False
        return self.level < other

    def __le__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return False
        return self.level <= other

    def __gt__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return False
        return self.level > other

    def __ge__(self, other: object) -> bool:
        other = self._prepare_other_for_comparison(other)
        if other is None:
            return False
        return self.level >= other

    @property
    def value(self) -> int:
        """Alias for self.level"""
        return self.level

    def print(self, message: str, level: int, end: str = "\n"):
        """
        Request that a message be printed. Compares against the set
        verbosity level before printing.

        Args:
            message (str):
                message to print
            level (int):
                If this number is higher priority than (lower numeric value)
                (or equal to) the set limit, print
            end (str):
                print(..., end= ...) hook
        """
        # print(f'request {message[:24]} @ {atlevel}')
        if self.level == 0 or level == 0:
            return
        if self.level >= level:
            print(message, end=end)


class VerboseMixin:
    _verbose = Verbosity(1)

    @property
    def verbose(self) -> Verbosity:
        """Verbose property"""
        if self._verbose is None:
            self._verbose = Verbosity(1)

        if not isinstance(self._verbose, Verbosity):
            self._verbose = Verbosity(self._verbose)
        return self._verbose

    @verbose.setter
    def verbose(self, value: Union[None, int, bool, Verbosity]) -> None:
        """Verbosity setter"""
        self._verbose = Verbosity(value)

    def validate_verbose(self, verbose: Union[None, int, bool, Verbosity]) -> Verbosity:
        """
        Allow for defaulting verbose

        replaces the boilerplate:
        if verbose is None:
            verbose = self._verbose
        else:
            verbose = Verbosity(verbose)

        with a single call:
        verbose = self.validate_verbose(verbose)
        """
        if verbose is None:
            if self._verbose is None:
                self._verbose = Verbosity(1)
            return self._verbose
        return Verbosity(verbose)

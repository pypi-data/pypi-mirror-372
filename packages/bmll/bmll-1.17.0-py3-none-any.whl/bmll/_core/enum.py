""" Enum base class
"""

import enum
import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum as StringEnum
else:
    class StringEnum(str, enum.Enum):
        pass


__all__ = (
    'StrEnum',
    'Area',
)


class StrEnumMeta(enum.EnumMeta):
    """
    Override the default Enum str representation of the Enum such that we return the Enum keys.
    """

    def __str__(self):
        return f'{super().__str__()} [{", ".join([str(i) for i in self])}]'

    def __contains__(self, item):
        return item in [x for x in self]


class StrEnum(StringEnum, metaclass=StrEnumMeta):
    """Enum with String Values."""

    @classmethod
    def parse(cls, string):
        """for a given string return the correct value"""
        try:
            return getattr(cls, string.upper())
        except AttributeError:
            raise ValueError(f'{string} invalid, must be one of {list(cls)}')


class BasicArea(StrEnum):
    USER = user = 'user'
    ORGANISATION = organisation = 'organisation'


class Area(StrEnum):
    """Areas available for storage."""
    USER = user = 'user'
    ORGANISATION = organisation = 'organisation'
    SUPPORT = support = 'support'
    SFTP = sftp = 'sftp'

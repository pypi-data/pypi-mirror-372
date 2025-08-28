""" Triggers for running scheduled jobs on availability.
"""

import abc
import itertools
from typing import TypedDict, List

from typeguard import typechecked

from bmll.reference import available_markets


__all__ = (
    'L3Availability',
    'CronTrigger',
)


class MicDict(TypedDict):
    mic: List[str]


class L3AvailabilityDictType(TypedDict):
    l3: MicDict


class CronTriggerDictType(TypedDict):
    cron: str


class AvailabilityTriggerDictType(TypedDict):
    availability: L3AvailabilityDictType


def _get_valid_mics():
    """ Return a set of the currently available MICs (as defined by the
        Data Feed's reference service's /available_markets endpoint).
    """
    available_mics = available_markets()["MIC"]
    mics = frozenset(available_mics)
    return mics


class BaseTrigger(abc.ABC):
    """ A base class for implementing triggers, a non-schedule object to describe
        a set of criteria for triggering a job.
    """
    @abc.abstractmethod
    def _jsonify(self) -> dict:
        """ Serialise a BaseTrigger subclass instance for transport.
        """

    @classmethod
    @abc.abstractmethod
    def _from_json(cls, serialised: dict) -> 'BaseTrigger':
        """ Instantiate a BaseTrigger subclass from a JSON object
        """


@typechecked
class L3Availability(BaseTrigger):
    """ Encapsulates a data availability trigger for L3 LOB data based upon MIC.

        Parameters
        ----------
        mics: sequence of str
            The MICs to be checked for readiness for triggering a cluster.

        Raises
        ------
        ValueError
            If any MIC is not valid (checked against :any:`bmll2.reference.available_markets`), or
            if no MICs are provided.

        Examples
        --------
        >>> # Instantiate from a long list
        >>> triggers = L3Availability(*my_long_list)  # doctest: +SKIP
        >>>
        >>> # XLON only
        >>> triggers = L3Availability("XLON")
        >>>
        >>> # XLON and XPAR only
        >>> triggers = L3Availability("XLON", "XPAR")
        >>>
        >>> # Check to see if XLON is in the trigger
        >>> "XLON" in triggers
        True
        >>>
        >>> # Check to see if BOTC is not in the trigger
        >>> "BOTC" in triggers
        False
    """
    def __init__(self, *mics) -> None:
        super().__init__()
        self.mics = mics

    def __contains__(self, mic: str) -> bool:
        return mic in self._mics

    def __repr__(self) -> str:
        max_mics = 6
        reduced_mics = itertools.islice(self._mics, max_mics)
        further_mics = ", ..." if max_mics < len(self._mics) else ""

        return (
            f'{self.__class__.__name__}({", ".join(reduced_mics)}{further_mics})'
        )

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.mics == other.mics

    def __iter__(self):
        return iter(self._mics)

    @property
    def mics(self) -> frozenset:
        """ Return the MICS currently set for this availability trigger.
        """
        return self._mics

    @mics.setter
    def mics(self, new_mics) -> None:
        """ Sets the MICs for this availability trigger.
        """
        if not new_mics:
            raise ValueError("No MICs provided for the availability trigger.")

        valid_mics = _get_valid_mics()
        unique_new_mics = frozenset(new_mics)

        if not unique_new_mics <= valid_mics:
            unknown_mics = ', '.join(unique_new_mics - valid_mics)
            msg = f"The following MICs are unknown and cannot be used in an availabilty trigger: {unknown_mics}"
            raise ValueError(msg)

        self._mics = unique_new_mics

    def _jsonify(self) -> L3AvailabilityDictType:
        """ Serialise for transport.
        """
        return {
            'l3': {
                'mic': sorted(self._mics)
            }
        }

    @classmethod
    def _from_json(cls, serialised: L3AvailabilityDictType) -> 'L3Availability':
        """ Instantiate a BaseTrigger subclass from a string
        """
        mics = sorted(serialised['l3']['mic'])
        return L3Availability(*mics)


@typechecked
class CronTrigger(BaseTrigger):

    def __init__(self, cron: str) -> None:
        """Requires cron express, example: '0 12 * * ?'"""
        super().__init__()
        self.cron = cron

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(cron={self._cron!r})'

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.cron == other.cron

    @property
    def cron(self):
        return self._cron

    @cron.setter
    def cron(self, val: str) -> None:
        if not val:
            raise ValueError("No, or an empty, cron expression was provided for the cron trigger.")

        self._cron = val

    def _jsonify(self) -> 'CronTriggerDictType':
        """ Serialise for transport.
        """
        return {
            'cron': self.cron
        }

    @classmethod
    def _from_json(cls, serialised: CronTriggerDictType) -> 'CronTrigger':
        """ Instantiate a BaseTrigger subclass from a string
        """
        return CronTrigger(serialised['cron'])

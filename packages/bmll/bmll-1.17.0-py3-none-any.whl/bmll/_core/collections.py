""" Helper objects for working with collections of BMLL objects.
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import TypeVar, Generic, List, Iterator, Dict

__all__ = (
    'BMLLCollection',
)

T = TypeVar('T')


class BMLLCollection(ABC, Generic[T]):
    """Base class to represent a collection of BMLL objects."""

    def __init__(self, bmll_object_list: List[T]):
        super().__init__()
        self._elements: Dict[str, T] = OrderedDict([(item.id, item) for item in bmll_object_list])  # type: ignore
        self._ids = list(self._elements.keys())
        self._values = list(self._elements.values())
        self._empty = not self._ids
        self._size = len(self._ids)

    @property
    def ids(self):
        """str: IDs of the collection items"""
        return self._ids

    @property
    def empty(self):
        """bool: Does the collection contain any elements"""
        return self._empty

    @property
    def size(self):
        """int: Size of the collection"""
        return self._size

    def __repr__(self):
        # TODO: bulk query this so don't have to do {Cluster, Job}.active
        # TODO: (which may call _fetch_status if not in final state) for each Cluster/Job)
        # TODO: will have to change tests as result of this
        return '{}({})'.format(self.__class__.__name__, [item for item in self._elements.values()])

    def __contains__(self, identifier: T):
        return identifier in self._elements

    def __getitem__(self, identifier) -> T:
        if isinstance(identifier, str):
            return self._elements[identifier]
        else:
            return self._values[identifier]

    def __iter__(self) -> Iterator[T]:
        return iter(self._elements.values())

    def __len__(self):
        return len(self._elements)

    def get(self, identifier):
        """Get item by id or return None if it does not exist."""
        try:
            return self.__getitem__(identifier)
        except KeyError:
            return None

    @abstractmethod
    def describe(self):
        """ Abstract method to describe the collection.
        """

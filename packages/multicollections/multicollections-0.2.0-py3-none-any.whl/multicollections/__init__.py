"""Fully generic `MultiDict` class."""

from __future__ import annotations

import sys
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )
else:
    from typing import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )

from .abc import MutableMultiMapping, with_default

_K = TypeVar("_K")
_V = TypeVar("_V")


class MultiDict(MutableMultiMapping[_K, _V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    def __init__(
        self, iterable: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (), **kwargs: _V
    ) -> None:
        """Create a MultiDict."""
        self._items: list[tuple[_K, _V]] = []
        self._key_indices: dict[_K, list[int]] = {}
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._add_item(key, value)
        else:
            for key, value in iterable:
                self._add_item(key, value)
        for key, value in kwargs.items():
            self._add_item(key, value)

    def _add_item(self, key: _K, value: _V) -> None:
        """Add an item and update the key index."""
        index = len(self._items)
        self._items.append((key, value))
        if key not in self._key_indices:
            self._key_indices[key] = []
        self._key_indices[key].append(index)

    @with_default
    def getall(self, key: _K) -> list[_V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self._items[i][1] for i in self._key_indices.get(key, [])]
        if not ret:
            raise KeyError(key)
        return ret

    def __setitem__(self, key: _K, value: _V) -> None:
        """Set the value for a key.

        Replaces the first value for a key if it exists; otherwise, it adds a new item.
        Any other items with the same key are removed.
        """
        if key in self._key_indices:
            # Key exists, replace first occurrence and remove others
            indices = self._key_indices[key]
            first_index = indices[0]

            # Update the first occurrence
            self._items[first_index] = (key, value)

            if len(indices) > 1:
                # Remove duplicates efficiently by marking items as None and filtering
                for idx in indices[1:]:
                    self._items[idx] = None

                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            # Key doesn't exist, add it
            self._add_item(key, value)

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    def add(self, key: _K, value: _V) -> None:
        """Add a new value for a key."""
        self._add_item(key, value)

    @with_default
    def popone(self, key: _K) -> _V:
        """Remove and return the first value for a key."""
        if key not in self._key_indices:
            raise KeyError(key)

        indices = self._key_indices[key]
        first_index = indices[0]
        value = self._items[first_index][1]

        # Mark the first item for removal
        self._items[first_index] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return value

    def __delitem__(self, key: _K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        if key not in self._key_indices:
            raise KeyError(key)

        # Mark items for removal
        indices_to_remove = self._key_indices[key]
        for idx in indices_to_remove:
            self._items[idx] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)

    def __repr__(self) -> str:
        """Return a string representation of the MultiDict."""
        return f"{self.__class__.__name__}({list(self._items)!r})"

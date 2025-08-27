"""Fully generic `MultiDict` class."""

from __future__ import annotations

import sys
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        ItemsView,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        Sequence,
        ValuesView,
    )
else:
    from typing import (
        ItemsView,
        Iterable,
        Iterator,
        Mapping,
        MutableMapping,
        Sequence,
        ValuesView,
    )

K = TypeVar("K")
V = TypeVar("V")


class MultiDict(MutableMapping[K, V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    class ValuesView(ValuesView[V]):  # noqa: D106
        def __init__(self, mapping: MultiDict[K, V]) -> None:  # noqa: D107
            super().__init__(mapping)

        def __iter__(self) -> Iterator[V]:  # noqa: D105
            return (v for _, v in self._mapping._items)  # noqa: SLF001

        def __len__(self) -> int:  # noqa: D105
            return len(self._mapping._items)  # noqa: SLF001

    class ItemsView(ItemsView[K, V]):  # noqa: D106
        def __init__(self, mapping: MultiDict[K, V]) -> None:  # noqa: D107
            self._mapping = mapping

        def __iter__(self) -> Iterator[tuple[K, V]]:  # noqa: D105
            return iter(self._mapping._items)  # noqa: SLF001

        def __len__(self) -> int:  # noqa: D105
            return len(self._mapping._items)  # noqa: SLF001

    def __init__(
        self, iterable: Mapping[K, V] | Iterable[Sequence[K | V]] = (), **kwargs: V
    ) -> None:
        """Create a MultiDict."""
        self._items: list[tuple[K, V]] = []
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._items.append((key, value))
        else:
            for key, value in iterable:
                self._items.append((key, value))
        for key, value in kwargs.items():
            self._items.append((key, value))

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        for k, v in self._items:
            if k == key:
                return v
        raise KeyError(key)

    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        Replaces the first value for a key if it exists; otherwise, it adds a new item.
        Any other items with the same key are removed.
        """
        replaced: int | None = None
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                replaced = i
                break

        if replaced is not None:
            # Key existed, remove any duplicates
            self._items = [
                (k, v)
                for i, (k, v) in enumerate(self._items)
                if i == replaced or k != key
            ]
        else:
            # Key didn't exist, add it
            self._items.append((key, value))

    def add(self, key: K, value: V) -> None:
        """Add a value for a key."""
        self._items.append((key, value))

    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        new_items = [(k, v) for k, v in self._items if k != key]
        if len(new_items) == len(self._items):
            raise KeyError(key)
        self._items = new_items

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the MultiDict."""
        return self.ValuesView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items in the MultiDict."""
        return self.ItemsView(self)

    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)

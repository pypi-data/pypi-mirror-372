"""Abstract base classes for multi-mapping collections."""

from __future__ import annotations

import itertools
import sys
from abc import abstractmethod
from collections import defaultdict
from typing import Generic, TypeVar, overload

if sys.version_info >= (3, 9):
    from collections.abc import (
        Collection,
        Iterable,
        Iterator,
        Mapping,
        MappingView,
        MutableMapping,
        Sequence,
    )
else:
    from typing import (
        Collection,
        Iterable,
        Iterator,
        Mapping,
        MappingView,
        MutableMapping,
        Sequence,
    )

K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")


class MultiMappingView(MappingView, Collection):
    """Base class for MultiMapping views."""

    def __init__(self, mapping: MultiMapping[K, V]) -> None:
        """Initialize the view with the given mapping."""
        super().__init__(mapping)


class KeysView(MultiMappingView):
    """View for the keys in a MultiMapping."""

    def __contains__(self, key: K) -> bool:
        """Check if the key is in the mapping."""
        return key in self._mapping

    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys."""
        return iter(self._mapping)


class ItemsView(MultiMappingView):
    """View for the items (key-value pairs) in a MultiMapping."""

    def __contains__(self, item: tuple[K, V]) -> bool:
        """Check if the item is in the mapping."""
        key, value = item
        try:
            return value in self._mapping.getall(key)
        except KeyError:
            return False

    def __iter__(self) -> Iterator[tuple[K, V]]:
        """Return an iterator over the items (key-value pairs)."""
        counts = defaultdict(int)
        for k in self._mapping:
            yield (k, self._mapping.getall(k)[counts[k]])
            counts[k] += 1


class ValuesView(MultiMappingView):
    """View for the values in a MultiMapping."""

    def __contains__(self, value: V) -> bool:
        """Check if the value is in the mapping."""
        return any(value in self._mapping.getall(key) for key in set(self._mapping))

    def __iter__(self) -> Iterator[V]:
        """Return an iterator over the values."""
        yield from (v for _, v in self._mapping.items())


class _NoDefault:
    pass


_NO_DEFAULT = _NoDefault()


class MultiMapping(Mapping[K, V], Generic[K, V]):
    """Abstract base class for multi-mapping collections.

    A multi-mapping is a mapping that can hold multiple values for the same key.
    This class provides a read-only interface to such collections.
    """

    @abstractmethod
    def _getall(self, key: K) -> list[V]:
        """Get all values for a key.

        Returns an empty list if no values are found.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __iter__(self) -> Iterator[K]:
        """Return an iterator over the keys.

        Keys with multiple values will be yielded multiple times.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def __len__(self) -> int:
        """Return the total number of items (key-value pairs)."""
        raise NotImplementedError  # pragma: no cover

    @overload
    def getone(self, key: K) -> V: ...

    @overload
    def getone(self, key: K, default: D) -> V | D: ...

    def getone(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            return self.getall(key)[0]
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default  # ty: ignore[invalid-return-type]

    def __getitem__(self, key: K) -> V:
        """Get the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.getone(key)

    @overload
    def getall(self, key: K) -> list[V]: ...

    @overload
    def getall(self, key: K, default: D) -> list[V] | D: ...

    def getall(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> list[V] | D:
        """Get all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            ret = self._getall(key)
        except KeyError as e:  # pragma: no cover
            msg = "_getall must return an empty list instead of raising KeyError"
            raise RuntimeError(msg) from e
        if not ret:
            if default is _NO_DEFAULT:
                raise KeyError(key)
            return default  # ty: ignore[invalid-return-type]
        return ret

    def keys(self) -> KeysView[K]:
        """Return a view of the keys in the MultiMapping."""
        return KeysView(self)

    def items(self) -> ItemsView[K, V]:
        """Return a view of the items (key-value pairs) in the MultiMapping."""
        return ItemsView(self)

    def values(self) -> ValuesView[V]:
        """Return a view of the values in the MultiMapping."""
        return ValuesView(self)


class MutableMultiMapping(MultiMapping[K, V], MutableMapping[K, V]):
    """Abstract base class for mutable multi-mapping collections.

    A mutable multi-mapping extends MultiMapping with methods to modify the collection.
    """

    @abstractmethod
    def __setitem__(self, key: K, value: V) -> None:
        """Set the value for a key.

        If the key does not exist, it is added with the specified value.

        If the key already exists, the first item is assigned the new value,
        and any other items with the same key are removed.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def add(self, key: K, value: V) -> None:
        """Add a new value for a key."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def _popone(self, key: K) -> V:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found.
        """
        raise NotImplementedError  # pragma: no cover

    @overload
    def popone(self, key: K) -> V: ...

    @overload
    def popone(self, key: K, default: D) -> V | D: ...

    def popone(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Remove and return the first value for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            return self._popone(key)
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default  # type: ignore[invalid-return-type]

    @overload
    def popall(self, key: K) -> list[V]: ...

    @overload
    def popall(self, key: K, default: D) -> list[V] | D: ...

    def popall(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> list[V] | D:
        """Remove and return all values for a key as a list.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        try:
            return [self.popone(key) for _ in range(len(self.getall(key)))]
        except KeyError:
            if default is _NO_DEFAULT:
                raise
            return default  # type: ignore[invalid-return-type]

    @overload
    def pop(self, key: K) -> V: ...

    @overload
    def pop(self, key: K, default: D) -> V | D: ...

    def pop(self, key: K, default: D | _NoDefault = _NO_DEFAULT) -> V | D:
        """Same as `popone`."""
        if default is _NO_DEFAULT:
            return self.popone(key)
        return self.popone(key, default)

    def popitem(self) -> tuple[K, V]:
        """Remove and return a (key, value) pair."""
        key = next(iter(self))
        value = self.popone(key)
        return key, value

    def __delitem__(self, key: K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        return self.popall(key)

    def clear(self) -> None:
        """Remove all items from the multi-mapping."""
        for key in set(self.keys()):
            self.popall(key)

    def extend(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Extend the multi-mapping with items from another object."""
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            self.add(key, value)

    def merge(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be replaced.
        """
        existing_keys = set(self.keys())
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            if key not in existing_keys:
                self.add(key, value)

    def update(
        self,
        other: Mapping[K, V] | Iterable[Sequence[K | V]] = (),
        **kwargs: V,
    ) -> None:
        """Update the multi-mapping with items from another object.

        This replaces existing values for keys found in the other object.
        """
        existing_keys = set(self.keys())
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        for key, value in items:
            if key in existing_keys:
                self[key] = value
                existing_keys.remove(key)
            else:
                self.add(key, value)

"""Basic tests for multicollections.MultiDict.

This module provides comprehensive tests for multicollections.MultiDict behavior.
"""

import pytest
from multicollections import MultiDict


class TestMultiDictBasic:
    """Basic functionality tests for MultiDict."""

    def test_empty_creation(self) -> None:
        """Test creating an empty MultiDict."""
        md = MultiDict()
        assert len(md) == 0
        assert list(md) == []
        assert list(md.items()) == []
        assert list(md.values()) == []

    def test_creation_from_pairs(self) -> None:
        """Test creating MultiDict from list of pairs."""
        pairs = [("a", 1), ("b", 2), ("a", 3)]
        md = MultiDict(pairs)

        assert len(md) == 3
        assert md["a"] == 1  # First value for duplicate key
        assert md["b"] == 2
        assert list(md.items()) == pairs
        assert list(md) == ["a", "b", "a"]
        assert list(md.values()) == [1, 2, 3]

    def test_creation_from_dict(self) -> None:
        """Test creating MultiDict from regular dict."""
        d = {"x": 10, "y": 20, "z": 30}
        md = MultiDict(d)

        assert len(md) == 3
        for key, value in d.items():
            assert md[key] == value

        # Order is preserved (dict insertion order is preserved in Python 3.7+)
        assert set(md.items()) == set(d.items())

    def test_creation_with_kwargs(self) -> None:
        """Test creating MultiDict with keyword arguments."""
        md = MultiDict(a=1, b=2, c=3)

        assert len(md) == 3
        assert md["a"] == 1
        assert md["b"] == 2
        assert md["c"] == 3

    def test_creation_mixed(self) -> None:
        """Test creating MultiDict with both iterable and kwargs."""
        pairs = [("a", 1), ("b", 2)]
        md = MultiDict(pairs, c=3, d=4)

        assert len(md) == 4
        assert md["a"] == 1
        assert md["b"] == 2
        assert md["c"] == 3
        assert md["d"] == 4

    def test_getitem(self) -> None:
        """Test __getitem__ behavior."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3)])

        assert md["a"] == 1  # First value
        assert md["b"] == 2

        with pytest.raises(KeyError):
            _ = md["missing"]

    def test_setitem_new_key(self) -> None:
        """Test __setitem__ with new key."""
        md = MultiDict()
        md["new"] = "value"

        assert len(md) == 1
        assert md["new"] == "value"
        assert list(md.items()) == [("new", "value")]

    def test_setitem_existing_key(self) -> None:
        """Test __setitem__ with existing key."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
        md["a"] = 99

        # Should replace and remove all duplicates
        assert len(md) == 2
        assert md["a"] == 99
        assert list(md.items()) == [("a", 99), ("b", 2)]

    def test_add_method(self) -> None:
        """Test add() method."""
        md = MultiDict()
        md.add("key", "value1")
        md.add("key", "value2")
        md.add("other", "value3")

        assert len(md) == 3
        assert md["key"] == "value1"  # First value
        assert md["other"] == "value3"
        assert list(md.items()) == [
            ("key", "value1"),
            ("key", "value2"),
            ("other", "value3"),
        ]

    def test_delitem(self) -> None:
        """Test __delitem__ behavior."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3), ("c", 4)])
        del md["a"]  # Should remove all 'a' items

        assert len(md) == 2
        assert list(md.items()) == [("b", 2), ("c", 4)]

        with pytest.raises(KeyError):
            del md["missing"]

    def test_iteration(self) -> None:
        """Test iteration over keys."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
        keys = list(md)

        assert keys == ["a", "b", "a"]

        # Test that iteration yields duplicate keys
        key_count = {}
        for key in md:
            key_count[key] = key_count.get(key, 0) + 1

        assert key_count == {"a": 2, "b": 1}

    def test_values_view(self) -> None:
        """Test values() view."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
        values = md.values()

        assert len(values) == 3
        assert list(values) == [1, 2, 3]

    def test_items_view(self) -> None:
        """Test items() view."""
        md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
        items = md.items()

        assert len(items) == 3
        assert list(items) == [("a", 1), ("b", 2), ("a", 3)]

    def test_len(self) -> None:
        """Test len() behavior."""
        md = MultiDict()
        assert len(md) == 0

        md.add("a", 1)
        assert len(md) == 1

        md.add("a", 2)  # Duplicate key
        assert len(md) == 2

        md["b"] = 3
        assert len(md) == 3

        del md["a"]  # Removes both 'a' items
        assert len(md) == 1


class TestMultiDictEdgeCases:
    """Test edge cases and various data scenarios."""

    def test_various_data_scenarios(self) -> None:
        """Test basic operations with various data sets."""
        test_cases = [
            [],
            [("a", 1)],
            [("a", 1), ("b", 2)],
            [("a", 1), ("b", 2), ("a", 3)],
            [("x", "hello"), ("y", "world"), ("x", "foo"), ("z", "bar")],
        ]

        for data in test_cases:
            md = MultiDict(data)

            # Test basic properties
            assert len(md) == len(data)
            assert list(md.items()) == data

            # Test that we can get all keys
            for key, expected_value in data:
                if data and md[key] != expected_value:
                    # Should be the first occurrence
                    first_value = next(value for k, value in data if k == key)
                    assert md[key] == first_value
                    break

    def test_setitem_scenarios(self) -> None:
        """Test __setitem__ in various scenarios."""
        test_cases = [
            ([], "new", "value"),
            ([("a", 1)], "b", 2),
            ([("a", 1), ("b", 2)], "a", 99),  # Replace existing
            ([("a", 1), ("b", 2), ("a", 3)], "a", 88),  # Replace with duplicates
        ]

        for initial_data, key, value in test_cases:
            md = MultiDict(initial_data)
            md[key] = value

            assert md[key] == value

            # If key existed before, there should be exactly one occurrence now
            key_count = sum(1 for k, v in md.items() if k == key)
            assert key_count == 1


class TestMultiDictInterface:
    """Test interface compatibility."""

    def test_multidict_interface(self) -> None:
        """Test that our MultiDict has expected interface."""
        md = MultiDict()

        # Check that basic methods exist and are callable
        assert hasattr(md, "add")
        assert callable(md.add)
        assert hasattr(md, "items")
        assert callable(md.items)
        assert hasattr(md, "values")
        assert callable(md.values)

        # Check magic methods
        assert hasattr(md, "__getitem__")
        assert hasattr(md, "__setitem__")
        assert hasattr(md, "__delitem__")
        assert hasattr(md, "__iter__")
        assert hasattr(md, "__len__")

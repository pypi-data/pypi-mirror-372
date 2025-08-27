"""Compatibility tests for multicollections.MultiDict behavior.

This test module compares the behavior of multicollections.MultiDict
with multidict.MultiDict for implemented functionality.
"""

import multidict
import pytest
from multicollections import MultiDict


class TestMultiDictCompatibility:
    """Test compatibility between our MultiDict and multidict.MultiDict."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.test_data = [
            ("key1", "value1"),
            ("key2", "value2"),
            ("key1", "value3"),
            ("key3", "value4"),
        ]
        self.test_dict = {"a": 1, "b": 2, "c": 3}
        self.test_kwargs = {"x": 10, "y": 20}

    def test_basic_construction_empty(self) -> None:
        """Test creating empty MultiDict instances."""
        our_md = MultiDict()
        their_md = multidict.MultiDict()

        assert len(our_md) == len(their_md)
        assert list(our_md) == list(their_md)

    def test_construction_from_pairs(self) -> None:
        """Test creating MultiDict from pairs."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        assert len(our_md) == len(their_md)
        assert list(our_md.items()) == list(their_md.items())
        assert list(our_md) == list(their_md)

        # Test that first value is returned for duplicate keys
        assert our_md["key1"] == their_md["key1"]

    def test_construction_from_dict(self) -> None:
        """Test creating MultiDict from regular dict."""
        our_md = MultiDict(self.test_dict)
        their_md = multidict.MultiDict(self.test_dict)

        assert len(our_md) == len(their_md)
        assert set(our_md.items()) == set(their_md.items())

        # Check all key-value pairs match
        for key in self.test_dict:
            assert our_md[key] == their_md[key]

    def test_construction_with_kwargs(self) -> None:
        """Test creating MultiDict with keyword arguments."""
        our_md = MultiDict(**self.test_kwargs)
        their_md = multidict.MultiDict(**self.test_kwargs)

        assert len(our_md) == len(their_md)

        for key in self.test_kwargs:
            assert our_md[key] == their_md[key]

    def test_getitem_behavior(self) -> None:
        """Test __getitem__ behavior."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        # Test getting existing keys
        assert our_md["key1"] == their_md["key1"]
        assert our_md["key2"] == their_md["key2"]
        assert our_md["key3"] == their_md["key3"]

        # Test KeyError for missing keys
        with pytest.raises(KeyError):
            _ = our_md["missing"]
        with pytest.raises(KeyError):
            _ = their_md["missing"]

    def test_setitem_behavior(self) -> None:
        """Test __setitem__ behavior."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        # Test setting new key
        our_md["new_key"] = "new_value"
        their_md["new_key"] = "new_value"
        assert our_md["new_key"] == their_md["new_key"]

        # Test replacing existing key (should remove all duplicates)
        our_md["key1"] = "replaced"
        their_md["key1"] = "replaced"
        assert our_md["key1"] == their_md["key1"]

        # Check that all duplicate values are gone
        our_items = list(our_md.items())
        their_items = list(their_md.items())

        our_key1_count = sum(1 for k, v in our_items if k == "key1")
        their_key1_count = sum(1 for k, v in their_items if k == "key1")

        assert our_key1_count == their_key1_count
        assert our_key1_count == 1

    def test_add_behavior(self) -> None:
        """Test add() method behavior."""
        our_md = MultiDict()
        their_md = multidict.MultiDict()

        # Add some values
        our_md.add("key1", "value1")
        our_md.add("key1", "value2")
        our_md.add("key2", "value3")

        their_md.add("key1", "value1")
        their_md.add("key1", "value2")
        their_md.add("key2", "value3")

        assert list(our_md.items()) == list(their_md.items())
        assert our_md["key1"] == their_md["key1"]  # First value

    def test_delitem_behavior(self) -> None:
        """Test __delitem__ behavior."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        # Delete a key that appears multiple times
        del our_md["key1"]
        del their_md["key1"]

        assert list(our_md.items()) == list(their_md.items())

        # Test KeyError for missing key
        with pytest.raises(KeyError):
            del our_md["missing"]
        with pytest.raises(KeyError):
            del their_md["missing"]

    def test_iteration_behavior(self) -> None:
        """Test iteration behavior."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        # Test key iteration
        assert list(our_md) == list(their_md)

        # Test items iteration
        assert list(our_md.items()) == list(their_md.items())

        # Test values iteration
        assert list(our_md.values()) == list(their_md.values())

    def test_len_behavior(self) -> None:
        """Test len() behavior."""
        our_md = MultiDict(self.test_data)
        their_md = multidict.MultiDict(self.test_data)

        assert len(our_md) == len(their_md)

        # Test with empty
        our_empty = MultiDict()
        their_empty = multidict.MultiDict()
        assert len(our_empty) == len(their_empty)

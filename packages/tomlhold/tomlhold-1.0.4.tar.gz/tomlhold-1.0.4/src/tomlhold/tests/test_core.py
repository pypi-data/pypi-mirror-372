import unittest
from typing import *

from tomlhold.core import Holder


class TestHolder(unittest.TestCase):

    def setUp(self: Self) -> None:
        "This method is called before each test case to set up a new instance of the Holder class."
        self.initial_data = {
            "key1": "value1",
            "key2": "value2",
            "nested": {"nested_key1": "nested_value1"},
        }
        self.holder = Holder()
        self.holder.data = self.initial_data

    def test_get_item(self: Self) -> None:
        "This testmethod tests if we can get an item by key."
        self.assertEqual(self.holder["key1"], "value1")
        self.assertEqual(self.holder["nested"]["nested_key1"], "nested_value1")

    def test_set_item(self: Self) -> None:
        "This testmethod tests if we can set an item by key."
        self.holder["key3"] = "value3"
        self.assertEqual(self.holder["key3"], "value3")

    def test_delete_item(self: Self) -> None:
        "This testmethod tests if we can delete an item by key."
        del self.holder["key1"]
        self.assertNotIn("key1", self.holder)

    def test_key_in_holder(self: Self) -> None:
        "This testmethod tests if we can check if a key is in the Holder."
        self.assertIn("key1", self.holder)
        self.assertNotIn("key3", self.holder)

    def test_len(self: Self) -> None:
        "This testmethod tests if len function returns the correct length."
        self.assertEqual(len(self.holder), len(self.initial_data))
        self.holder["key3"] = "value3"
        self.assertEqual(len(self.holder), len(self.initial_data) + 1)

    def test_update(self: Self) -> None:
        "This testmethod tests if the update method works correctly."
        new_data: dict = {"key3": "value3", "key4": "value4"}
        self.holder.update(new_data)
        self.assertEqual(self.holder["key3"], "value3")
        self.assertEqual(self.holder["key4"], "value4")

    def test_iteration(self: Self) -> None:
        "This testmethod tests if iteration over keys works."
        key: Any
        keys: list = list(self.holder)
        self.assertListEqual(keys, list(self.initial_data.keys()))

    def test_copy(self: Self) -> None:
        "This testmethod tests if copy works correctly."
        holder_copy: Holder = self.holder.copy()
        self.assertEqual(holder_copy, self.holder)

    def test_equality(self: Self) -> None:
        "This testmethod tests equality of two Holder instances."
        holder2: Holder = Holder(self.initial_data)
        self.assertEqual(self.holder, holder2)
        holder2["key3"] = "value3"
        self.assertNotEqual(self.holder, holder2)

    def test_clear(self: Self) -> None:
        "This testmethod tests if clear method works."
        self.holder.clear()
        self.assertEqual(len(self.holder), 0)

    def test_initialization_with_toml(self: Self) -> None:
        "This testmethod tests if the Holder initializes correctly with TOML data."
        toml_data: str = """
        [section]
        key1 = "value1"
        key2 = "value2"
        [section.nested]
        nested_key1 = "nested_value1"
        """
        holder: Holder = Holder.loads(toml_data)
        self.assertEqual(holder["section", "key1"], "value1")
        self.assertEqual(holder["section"]["nested"]["nested_key1"], "nested_value1")

    def test_invalid_key_access(self: Self) -> None:
        "This testmethod tests if accessing a non-existent key raises KeyError."
        with self.assertRaises(KeyError):
            _: Any = self.holder["non_existent_key"]

    def test_pop(self: Self) -> None:
        "This testmethod tests if pop works correctly."
        value: Any = self.holder.pop("key1")
        self.assertEqual(value, "value1")
        self.assertNotIn("key1", self.holder)

    def test_popitem(self: Self) -> None:
        "This testmethod tests if popitem works correctly."
        key: Any
        value: Any
        key, value = self.holder.popitem()
        self.assertIn(key, self.initial_data)
        self.assertEqual(value, self.initial_data[key])

    def test_keys_values_items(self: Self) -> None:
        "This testmethod tests keys(), values(), and items() methods."
        self.assertListEqual(list(self.holder.keys()), list(self.initial_data.keys()))
        self.assertListEqual(
            list(self.holder.values()), list(self.initial_data.values())
        )
        self.assertListEqual(list(self.holder.items()), list(self.initial_data.items()))


if __name__ == "__main__":
    unittest.main()

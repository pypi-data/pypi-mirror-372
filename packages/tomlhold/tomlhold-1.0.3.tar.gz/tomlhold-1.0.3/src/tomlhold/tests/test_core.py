import unittest

from tomlhold.core import Holder


class TestHolder(unittest.TestCase):

    def setUp(self):
        """
        This method is called before each test case to set up a new instance of the Holder class.
        """
        self.initial_data = {
            "key1": "value1",
            "key2": "value2",
            "nested": {"nested_key1": "nested_value1"},
        }
        self.holder = Holder()
        self.holder.data = self.initial_data

    def test_get_item(self):
        """Test if we can get an item by key."""
        self.assertEqual(self.holder["key1"], "value1")
        self.assertEqual(self.holder["nested"]["nested_key1"], "nested_value1")

    def test_set_item(self):
        """Test if we can set an item by key."""
        self.holder["key3"] = "value3"
        self.assertEqual(self.holder["key3"], "value3")

    def test_delete_item(self):
        """Test if we can delete an item by key."""
        del self.holder["key1"]
        self.assertNotIn("key1", self.holder)

    def test_key_in_holder(self):
        """Test if we can check if a key is in the Holder."""
        self.assertIn("key1", self.holder)
        self.assertNotIn("key3", self.holder)

    def test_len(self):
        """Test if len function returns the correct length."""
        self.assertEqual(len(self.holder), len(self.initial_data))
        self.holder["key3"] = "value3"
        self.assertEqual(len(self.holder), len(self.initial_data) + 1)

    def test_update(self):
        """Test if the update method works correctly."""
        new_data = {"key3": "value3", "key4": "value4"}
        self.holder.update(new_data)
        self.assertEqual(self.holder["key3"], "value3")
        self.assertEqual(self.holder["key4"], "value4")

    def test_iteration(self):
        """Test if iteration over keys works."""
        keys = [key for key in self.holder]
        self.assertListEqual(keys, list(self.initial_data.keys()))

    def test_copy(self):
        """Test if copy works correctly."""
        holder_copy = self.holder.copy()
        self.assertEqual(holder_copy, self.holder)

    def test_equality(self):
        """Test equality of two Holder instances."""
        holder2 = Holder(self.initial_data)
        self.assertEqual(self.holder, holder2)
        holder2["key3"] = "value3"
        self.assertNotEqual(self.holder, holder2)

    def test_clear(self):
        """Test if clear method works."""
        self.holder.clear()
        self.assertEqual(len(self.holder), 0)

    def test_initialization_with_toml(self):
        """Test if the Holder initializes correctly with TOML data."""
        toml_data = """
        [section]
        key1 = "value1"
        key2 = "value2"
        [section.nested]
        nested_key1 = "nested_value1"
        """
        holder = Holder.loads(toml_data)
        self.assertEqual(holder["section", "key1"], "value1")
        self.assertEqual(holder["section"]["nested"]["nested_key1"], "nested_value1")

    def test_invalid_key_access(self):
        """Test if accessing a non-existent key raises KeyError."""
        with self.assertRaises(KeyError):
            _ = self.holder["non_existent_key"]

    def test_pop(self):
        """Test if pop works correctly."""
        value = self.holder.pop("key1")
        self.assertEqual(value, "value1")
        self.assertNotIn("key1", self.holder)

    def test_popitem(self):
        """Test if popitem works correctly."""
        key, value = self.holder.popitem()
        self.assertIn(key, self.initial_data)
        self.assertEqual(value, self.initial_data[key])

    def test_keys_values_items(self):
        """Test keys(), values(), and items() methods."""
        self.assertListEqual(list(self.holder.keys()), list(self.initial_data.keys()))
        self.assertListEqual(
            list(self.holder.values()), list(self.initial_data.values())
        )
        self.assertListEqual(list(self.holder.items()), list(self.initial_data.items()))


if __name__ == "__main__":
    unittest.main()

import datetime
import unittest

from tomlhold.core import Holder


class TestHolderCombined(unittest.TestCase):

    def setUp(self):
        """
        This method is called before each test case to set up a new instance of the Holder class.
        """
        self.holder = Holder()

    def test_string(self):
        """Test storing and retrieving strings with multi-index support."""
        self.holder["section", "string_key"] = "Hello, World!"
        self.assertEqual(self.holder["section", "string_key"], "Hello, World!")

    def test_integer(self):
        """Test storing and retrieving integers with multi-index support."""
        self.holder["section", "integer_key"] = 42
        self.assertEqual(self.holder["section", "integer_key"], 42)

    def test_float(self):
        """Test storing and retrieving floats with multi-index support."""
        self.holder["section", "float_key"] = 3.14159
        self.assertEqual(self.holder["section", "float_key"], 3.14159)

    def test_boolean(self):
        """Test storing and retrieving booleans with multi-index support."""
        self.holder["section", "boolean_key_true"] = True
        self.holder["section", "boolean_key_false"] = False
        self.assertTrue(self.holder["section", "boolean_key_true"])
        self.assertFalse(self.holder["section", "boolean_key_false"])

    def test_array(self):
        """Test storing and retrieving arrays with multi-index support."""
        array_data = [1, 2, 3, "four", True]
        self.holder["section", "array_key"] = array_data
        self.assertListEqual(self.holder["section", "array_key"], array_data)

    def test_datetime(self):
        """Test storing and retrieving datetime objects with multi-index support."""
        datetime_value = datetime.datetime(2023, 10, 22, 14, 45, 0)
        self.holder["section", "datetime_key"] = datetime_value
        self.assertEqual(self.holder["section", "datetime_key"], datetime_value)

    def test_date(self):
        """Test storing and retrieving date objects with multi-index support."""
        date_value = datetime.date(2023, 10, 22)
        self.holder["section", "date_key"] = date_value
        self.assertEqual(self.holder["section", "date_key"], date_value)

    def test_time(self):
        """Test storing and retrieving time objects with multi-index support."""
        time_value = datetime.time(14, 45, 0)
        self.holder["section", "time_key"] = time_value
        self.assertEqual(self.holder["section", "time_key"], time_value)

    def test_nested_tables(self):
        """Test nested tables (dictionaries) with multi-index access."""
        nested_data = {
            "key1": "value1",
            "key2": {
                "nested_key1": "nested_value1",
                "nested_key2": {"deep_key": "deep_value"},
            },
        }
        self.holder["nested_table"] = nested_data
        self.assertEqual(
            self.holder["nested_table", "key2", "nested_key1"], "nested_value1"
        )
        self.assertEqual(
            self.holder["nested_table", "key2", "nested_key2", "deep_key"], "deep_value"
        )

    def test_mixed_array(self):
        """Test storing and retrieving mixed-type arrays with multi-index support."""
        mixed_array = [1, "two", 3.0, True, {"nested_key": "nested_value"}]
        self.holder["section", "mixed_array_key"] = mixed_array
        self.assertEqual(self.holder["section", "mixed_array_key"], mixed_array)

    def test_empty_table(self):
        """Test handling of empty tables (dictionaries) with multi-index support."""
        self.holder["section", "empty_table"] = {}
        self.assertEqual(self.holder["section", "empty_table"], {})

    def test_multiline_string(self):
        """Test storing and retrieving multiline strings with multi-index support."""
        multiline_string = """This is a
multiline string
with several lines."""
        self.holder["section", "multiline_string_key"] = multiline_string
        self.assertEqual(
            self.holder["section", "multiline_string_key"], multiline_string
        )

    def test_update_with_multiple_data_types(self):
        """Test updating the Holder with multiple data types at once."""
        update_data = {
            "string": "test_string",
            "integer": 100,
            "float": 9.81,
            "boolean": False,
            "datetime": datetime.datetime(2023, 1, 1, 0, 0, 0),
            "array": [1, 2, 3],
        }
        self.holder.update(update_data)
        self.assertEqual(self.holder["string"], "test_string")
        self.assertEqual(self.holder["integer"], 100)
        self.assertEqual(self.holder["float"], 9.81)
        self.assertFalse(self.holder["boolean"])
        self.assertEqual(
            self.holder["datetime"], datetime.datetime(2023, 1, 1, 0, 0, 0)
        )
        self.assertListEqual(self.holder["array"], [1, 2, 3])

    def test_dictlike_operations(self):
        """Test that the Holder supports dict-like operations."""
        self.holder["key1"] = "value1"
        self.holder["key2"] = "value2"

        # Test __getitem__ and __setitem__
        self.assertEqual(self.holder["key1"], "value1")
        self.holder["key1"] = "new_value"
        self.assertEqual(self.holder["key1"], "new_value")

        # Test __delitem__
        del self.holder["key1"]
        self.assertNotIn("key1", self.holder)

        # Test __contains__
        self.assertIn("key2", self.holder)
        self.assertNotIn("key1", self.holder)

        # Test len()
        self.assertEqual(len(self.holder), 1)

        # Test keys(), values(), items()
        self.assertListEqual(list(self.holder.keys()), ["key2"])
        self.assertListEqual(list(self.holder.values()), ["value2"])
        self.assertListEqual(list(self.holder.items()), [("key2", "value2")])

    def test_multiindex_access(self):
        """Test accessing and updating data using multi-indices."""
        self.holder.setdefault("a", "42", "foo", default="bar")
        self.assertEqual(self.holder["a", "42", "foo"], "bar")

        self.holder.setdefault("x", "99", "y", "z", default="deep_value")
        self.assertEqual(self.holder["x", "99", "y", "z"], "deep_value")

        self.holder["a", "42", "foo"] = "new_bar"
        self.assertEqual(self.holder["a", "42", "foo"], "new_bar")

    def test_holder_as_toml_string(self):
        """Test if Holder can be serialized back into TOML format correctly."""
        toml_data = """
        key1 = "value1"
        key2 = 42
        float_key = 3.14
        boolean_key = true
        array_key = [1, 2, 3, "four"]
        """
        holder = Holder.loads(toml_data)
        toml_string = holder.dumps()
        self.assertIn('key1 = "value1"', toml_string)
        self.assertIn("key2 = 42", toml_string)
        self.assertIn("float_key = 3.14", toml_string)
        self.assertIn("boolean_key = true", toml_string)


if __name__ == "__main__":
    unittest.main()

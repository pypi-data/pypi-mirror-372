import io
import os
import unittest
from typing import *

from texthold.core import Holder


class TestHolder(unittest.TestCase):

    def setUp(self: Self) -> None:
        """Initialize a Holder instance for testing."""
        self.holder = Holder(["Hello", "World"])

    def test_data_property_getter(self: Self) -> None:
        """Test the data property getter."""
        self.assertEqual(self.holder.data, ["Hello", "World"])

    def test_data_property_setter(self: Self) -> None:
        """Test the data property setter."""
        self.holder.data = ["New", "Data"]
        self.assertEqual(self.holder.data, ["New", "Data"])

    def test_data_property_setter_multiline(self: Self) -> None:
        """Test setting multiline strings."""
        self.holder.data = ["First\nSecond", "Third"]
        self.assertEqual(self.holder.data, ["First", "Second", "Third"])

    def test_data_property_deleter(self: Self) -> None:
        """Test deleting the data property."""
        del self.holder.data
        self.assertEqual(self.holder.data, [])

    def test_dumps(self: Self) -> None:
        """Test the dumps method."""
        self.assertEqual(self.holder.dumps(), "Hello\nWorld\n")

    def test_dump(self: Self) -> None:
        """Test the dump method with a binary stream."""
        stream: io.BytesIO = io.BytesIO()
        self.holder.dump(stream)
        self.assertEqual(stream.getvalue().decode(), "Hello\nWorld\n")

    def test_load(self: Self) -> None:
        """Test the load method from a binary stream."""
        stream: io.BytesIO = io.BytesIO(b"Test\nLoad\n")
        loaded_holder: Holder = Holder.load(stream)
        self.assertEqual(loaded_holder.data, ["Test", "Load"])

    def test_loads(self: Self) -> None:
        """Test the loads method."""
        loaded_holder: Holder = Holder.loads("Test\nLoad\n")
        self.assertEqual(loaded_holder.data, ["Test", "Load"])

    def test_dumpintofile_and_loadfromfile(self: Self) -> None:
        """Test dumping to and loading from a file."""
        filename: str = "test_holder.txt"
        self.holder.dumpintofile(filename)
        loaded_holder: Holder = Holder.loadfromfile(filename)
        self.assertEqual(loaded_holder.data, self.holder.data)
        os.remove(filename)

    def test_empty_initialization(self: Self) -> None:
        """Test initializing Holder with no data."""
        empty_holder: Holder = Holder([])
        self.assertEqual(empty_holder.data, [])

    def test_mixed_type_input(self: Self) -> None:
        """Test initializing Holder with mixed-type input."""
        mixed_holder: Holder = Holder(["String", 123, 45.67])
        self.assertEqual(mixed_holder.data, ["String", "123", "45.67"])

    def test_multiline_string_input(self: Self) -> None:
        """Test initializing Holder with multiline strings."""
        multiline_holder: Holder = Holder(["Line1\nLine2", "Line3"])
        self.assertEqual(multiline_holder.data, ["Line1", "Line2", "Line3"])


if __name__ == "__main__":
    unittest.main()

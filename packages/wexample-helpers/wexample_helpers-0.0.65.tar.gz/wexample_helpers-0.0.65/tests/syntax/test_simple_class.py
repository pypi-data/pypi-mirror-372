from __future__ import annotations

import unittest

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.common.debug.debug_dump_class import DebugDumpClass
from wexample_helpers.testing.classes.simple_class import SimpleClass


class TestSimpleObject(unittest.TestCase):
    def test_simple_object(self) -> None:
        # Test instance creation with default values
        obj1 = SimpleClass()
        self.assertIsInstance(obj1, SimpleClass)
        self.assertEqual(obj1.name, "default")

        # Test instance creation with custom values
        obj2 = SimpleClass(name="test")
        self.assertIsInstance(obj2, SimpleClass)
        self.assertEqual(obj2.name, "test")

        # Test debug dump of class structure
        class_dumper = DebugDumpClass(SimpleClass)
        class_dumper.collect_data()
        class_data = class_dumper.data

        # Verify class structure
        self.assertEqual(class_data["type"], "class")
        self.assertEqual(class_data["name"], "SimpleClass")

        # Test debug dump of instance
        instance_dumper = DebugDump(obj2)
        instance_dumper.collect_data()
        instance_data = instance_dumper.data

        # Verify instance data
        self.assertTrue("instance_of" in instance_data)
        self.assertEqual(instance_data["instance_of"], "SimpleClass")
        self.assertTrue("attributes" in instance_data)
        attrs = instance_data["attributes"]
        self.assertTrue("name" in attrs)
        self.assertEqual(attrs["name"]["value"], "'test'")

        # Print debug outputs for visual verification
        class_dumper.print()
        instance_dumper.print()

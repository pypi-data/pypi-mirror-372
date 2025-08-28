from __future__ import annotations

import unittest

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.common.debug.debug_dump_class import DebugDumpClass
from wexample_helpers.testing.classes.first_parent import FirstParent
from wexample_helpers.testing.classes.multiple_child import MultipleChild
from wexample_helpers.testing.classes.second_parent import SecondParent


class TestMultipleInheritance(unittest.TestCase):
    def test_multiple_inheritance(self) -> None:
        # Test instance creation with default values
        child = MultipleChild()
        self.assertIsInstance(child, MultipleChild)
        self.assertIsInstance(child, FirstParent)
        self.assertIsInstance(child, SecondParent)
        self.assertEqual(child.child_value, "default_child")
        self.assertEqual(child.first_value, "inherited_first")
        self.assertEqual(child.second_value, "inherited_second")

        # Test instance creation with custom values
        custom_child = MultipleChild(
            child_value="custom_child",
            first_value="custom_first",
            second_value="custom_second",
        )
        self.assertEqual(custom_child.child_value, "custom_child")
        self.assertEqual(custom_child.first_value, "custom_first")
        self.assertEqual(custom_child.second_value, "custom_second")

        # Test methods inheritance
        self.assertTrue("First parent method" in custom_child.first_method())
        self.assertTrue("Second parent method" in custom_child.second_method())
        self.assertTrue("Child method" in custom_child.child_method())
        self.assertTrue("custom_first" in custom_child.first_method())
        self.assertTrue("custom_second" in custom_child.second_method())

        # Test debug dump of class structure
        class_dumper = DebugDumpClass(MultipleChild)
        class_dumper.collect_data()
        class_data = class_dumper.data

        # Verify class structure
        self.assertEqual(class_data["type"], "class")
        self.assertEqual(class_data["name"], "MultipleChild")
        self.assertTrue("bases" in class_data)

        # Verify both parent classes in bases
        bases = [base["name"] for base in class_data["bases"]]
        self.assertIn("FirstParent", bases)
        self.assertIn("SecondParent", bases)

        # Test debug dump of instance
        instance_dumper = DebugDump(custom_child)
        instance_dumper.collect_data()
        instance_data = instance_dumper.data

        # Verify instance data
        self.assertEqual(instance_data["instance_of"], "MultipleChild")
        self.assertTrue("attributes" in instance_data)
        attrs = instance_data["attributes"]
        self.assertTrue("child_value" in attrs)
        self.assertTrue("first_value" in attrs)
        self.assertTrue("second_value" in attrs)

        # Print debug outputs for visual verification
        class_dumper.print()
        instance_dumper.print()

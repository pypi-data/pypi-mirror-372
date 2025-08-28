from __future__ import annotations

import unittest

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.common.debug.debug_dump_class import DebugDumpClass
from wexample_helpers.testing.classes.child_class import ChildClass
from wexample_helpers.testing.classes.parent_class import ParentClass


class TestInheritance(unittest.TestCase):
    def test_inheritance(self) -> None:
        # Test instance creation
        parent = ParentClass(parent_value="custom_parent")
        child = ChildClass(child_value="custom_child", parent_value="inherited_parent")

        # Test parent instance creation
        self.assertIsInstance(parent, ParentClass)
        self.assertEqual(parent.parent_value, "custom_parent")

        # Test child instance creation and inheritance
        self.assertIsInstance(child, ChildClass)
        self.assertIsInstance(child, ParentClass)  # Should also be instance of parent
        self.assertEqual(child.child_value, "custom_child")
        self.assertEqual(child.parent_value, "inherited_parent")

        # Test debug dump of child class structure
        class_dumper = DebugDumpClass(ChildClass)
        class_dumper.collect_data()
        class_data = class_dumper.data

        # Verify class data structure
        self.assertEqual(class_data["type"], "class")
        self.assertEqual(class_data["name"], "ChildClass")
        self.assertTrue("bases" in class_data)

        # Verify parent class in bases
        parent_data = class_data["bases"][0]
        self.assertEqual(parent_data["name"], "ParentClass")

        # Test debug dump of child instance
        instance_dumper = DebugDump(child)
        instance_dumper.collect_data()
        instance_data = instance_dumper.data

        # Verify instance data
        self.assertTrue("instance_of" in instance_data)
        self.assertEqual(instance_data["instance_of"], "ChildClass")
        self.assertTrue("attributes" in instance_data)

        # Print debug outputs for visual verification
        class_dumper.print()
        instance_dumper.print()

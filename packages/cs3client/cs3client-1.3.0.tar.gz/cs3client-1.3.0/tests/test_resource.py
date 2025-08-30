"""
test_resource.py

Tests that the resource class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 26/07/2024
"""

import unittest
import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr

from cs3client.cs3resource import Resource


class TestResource(unittest.TestCase):

    def test_absolute_path(self):
        res = Resource.from_file_ref_and_endpoint("/path/to/file")
        self.assertEqual(res._abs_path, "/path/to/file")
        self.assertIsNone(res._rel_path)
        self.assertIsNone(res._parent_id)
        self.assertIsNone(res._opaque_id)
        self.assertIsNone(res._space_id)
        self.assertIsNone(res._storage_id)
        ref = res.ref
        self.assertEqual(ref.path, "/path/to/file")

    def test_relative_path(self):
        res = Resource.from_file_ref_and_endpoint("parent_id/path/to/file", "storage$space")
        self.assertIsNone(res._abs_path)
        self.assertEqual(res._rel_path, "/path/to/file")
        self.assertEqual(res._parent_id, "parent_id")
        self.assertIsNone(res._opaque_id)
        self.assertEqual(res._space_id, "space")
        self.assertEqual(res._storage_id, "storage")
        ref = res.ref
        self.assertEqual(ref.resource_id.storage_id, "storage")
        self.assertEqual(ref.resource_id.space_id, "space")
        self.assertEqual(ref.resource_id.opaque_id, "parent_id")
        self.assertEqual(ref.path, "./path/to/file")

    def test_opaque_fileid(self):
        res = Resource.from_file_ref_and_endpoint("opaque_id", "storage$space")
        self.assertIsNone(res._abs_path)
        self.assertIsNone(res._rel_path)
        self.assertIsNone(res._parent_id)
        self.assertEqual(res._opaque_id, "opaque_id")
        self.assertEqual(res._space_id, "space")
        self.assertEqual(res._storage_id, "storage")
        ref = res.ref
        self.assertEqual(ref.resource_id.storage_id, "storage")
        self.assertEqual(ref.resource_id.space_id, "space")
        self.assertEqual(ref.resource_id.opaque_id, "opaque_id")
        self.assertEqual(ref.path, ".")

    def test_recreate_endpoint_and_file_absolute_path(self):
        res = Resource.from_file_ref_and_endpoint("/path/to/file")
        recreated = res.recreate_endpoint_and_file()
        self.assertEqual(recreated["file"], "/path/to/file")
        self.assertEqual(recreated["endpoint"], None)

    def test_recreate_endpoint_and_file_relative_path(self):
        res = Resource.from_file_ref_and_endpoint("parent_id/path/to/file", "storage$space")
        recreated = res.recreate_endpoint_and_file()
        self.assertEqual(recreated["file"], "parent_id/path/to/file")
        self.assertEqual(recreated["endpoint"], "storage$space")

    def test_recreate_endpoint_and_file_opaque_fileid(self):
        res = Resource.from_file_ref_and_endpoint("opaque_id", "storage$space")
        recreated = res.recreate_endpoint_and_file()
        self.assertEqual(recreated["file"], "opaque_id")
        self.assertEqual(recreated["endpoint"], "storage$space")

    def test_from_cs3_ref_absolute_path(self):
        ref = cs3spr.Reference(path="/path/to/file")
        res = Resource.from_cs3_ref(ref)
        self.assertEqual(res._abs_path, "/path/to/file")
        self.assertIsNone(res._rel_path)
        self.assertIsNone(res._parent_id)
        self.assertIsNone(res._opaque_id)
        self.assertIsNone(res._space_id)
        self.assertIsNone(res._storage_id)

    def test_from_cs3_ref_relative_path(self):
        ref = cs3spr.Reference(
            resource_id=cs3spr.ResourceId(storage_id="storage", space_id="space", opaque_id="parent_id"),
            path="./path/to/file",
        )
        res = Resource.from_cs3_ref(ref)
        self.assertIsNone(res._abs_path)
        self.assertEqual(res._rel_path, "/path/to/file")
        self.assertEqual(res._parent_id, "parent_id")
        self.assertIsNone(res._opaque_id)
        self.assertEqual(res._space_id, "space")
        self.assertEqual(res._storage_id, "storage")

    def test_from_cs3_ref_opaque_fileid(self):
        ref = cs3spr.Reference(
            resource_id=cs3spr.ResourceId(storage_id="storage", space_id="space", opaque_id="opaque_id"),
            path=".",
        )
        res = Resource.from_cs3_ref(ref)
        self.assertIsNone(res._abs_path)
        self.assertIsNone(res._rel_path)
        self.assertIsNone(res._parent_id)
        self.assertEqual(res._opaque_id, "opaque_id")
        self.assertEqual(res._space_id, "space")
        self.assertEqual(res._storage_id, "storage")

    def test_invalid_file_reference_in_ref(self):
        res = Resource.from_file_ref_and_endpoint("/path/to/file")
        res._abs_path = None  # Manually invalidate the absolute path
        with self.assertRaises(ValueError) as context:
            _ = res.ref
        self.assertEqual(str(context.exception), "Invalid Resource")

    def test_invalid_file_reference_in_recreate_endpoint_and_file(self):
        res = Resource.from_file_ref_and_endpoint("/path/to/file")
        res._abs_path = None  # Manually invalidate the absolute path
        with self.assertRaises(ValueError) as context:
            _ = res.recreate_endpoint_and_file()
        self.assertEqual(str(context.exception), "Invalid Resource")

    def test_from_cs3_ref_invalid_reference(self):
        ref = cs3spr.Reference()  # Create an empty reference
        with self.assertRaises(ValueError) as context:
            resource = Resource.from_cs3_ref(ref)
            print(resource)
        self.assertEqual(str(context.exception), "Invalid CS3 reference")

    def test_equality(self):
        res1 = Resource.from_file_ref_and_endpoint("/path/to/file")
        res2 = Resource.from_file_ref_and_endpoint("/path/to/file")
        res3 = Resource.from_file_ref_and_endpoint("parent_id/path/to/file", "storage$space")
        self.assertEqual(res1, res2)
        self.assertNotEqual(res1, res3)

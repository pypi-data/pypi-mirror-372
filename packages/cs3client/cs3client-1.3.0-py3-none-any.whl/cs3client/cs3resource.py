"""
cs3resource.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 19/08/2024
"""

import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr
from typing import Union


class Resource:
    """Class to handle CS3 resources, the class can be initialized with an absolute path,
    a relative path or an opaque fileid as the "file" parameter (required).

    Absolute path example: `/path/to/file`
    Relative path example: `<parent_opaque_id>/<base_filename>` or `<parent_opaque_id>/<path>/<to>/<file>`
    Opaque fileid example: `<opaque_file_id>`

    The endpoint attribute contains the storage_id and space_id (always optional) separated by a `$` character,
    this is optional if the file is an absolute path.

    endpoint example: `storage_id` or `storage_id$space_id`

    """

    def __init__(
        self,
        abs_path: Union[str, None] = None,
        rel_path: Union[str, None] = None,
        opaque_id: Union[str, None] = None,
        parent_id: Union[str, None] = None,
        storage_id: Union[str, None] = None,
        space_id: Union[str, None] = None,
    ) -> None:
        """
        initializes the Resource class, either abs_path, rel_path or opaque_id is required
        and with rel_path the parent_id is also required, the rest parameters are fully optional.


        :param abs_path: absolute path (semi-optional)
        :param rel_path: relative path (semi-optional)
        :param parent_id: parent id (semi-optional)
        :param opaque_id: opaque id (semi-optional)
        :param storage_id: storage id (optional)
        :param space_id: space id (optional)
        """
        self._abs_path: Union[str, None] = abs_path
        self._rel_path: Union[str, None] = rel_path
        self._parent_id: Union[str, None] = parent_id
        self._opaque_id: Union[str, None] = opaque_id
        self._space_id: Union[str, None] = space_id
        self._storage_id: Union[str, None] = storage_id

    @classmethod
    def from_file_ref_and_endpoint(cls, file: str, endpoint: Union[str, None] = None) -> "Resource":
        """
        Extracts the attributes from the file and endpoint and returns a resource.

        :param file: The file reference
        :param endpoint: The storage id and space id (optional)
        :return: Resource object
        """

        abs_path = None
        rel_path = None
        opaque_id = None
        parent_id = None
        storage_id = None
        space_id = None

        if file.startswith("/"):
            # assume we have an absolute path
            abs_path = file
        else:
            # try splitting endpoint
            parts = endpoint.split("$", 2)
            storage_id = parts[0]
            if len(parts) == 2:
                space_id = parts[1]
            if file.find("/") > 0:
                # assume we have an relative path,
                parent_id = file[: file.find("/")]
                rel_path = file[file.find("/"):]
            else:
                # assume we have an opaque fileid
                opaque_id = file
        return cls(abs_path, rel_path, opaque_id, parent_id, storage_id, space_id)

    @property
    def ref(self) -> cs3spr.Reference:
        """
        Generates a CS3 reference for a given resource, covering the following cases:
        absolute path, relative hybrid path, fully opaque fileid.

        :return: The cs3 reference.
        :raises: ValueError (Invalid Resource)
        """
        if self._abs_path:
            return cs3spr.Reference(path=self._abs_path)
        if self._rel_path:
            return cs3spr.Reference(
                resource_id=cs3spr.ResourceId(
                    storage_id=self._storage_id,
                    space_id=self._space_id,
                    opaque_id=self._parent_id,
                ),
                path="." + self._rel_path,
            )
        if self._opaque_id:
            return cs3spr.Reference(
                resource_id=cs3spr.ResourceId(
                    storage_id=self._storage_id,
                    space_id=self._space_id,
                    opaque_id=self._opaque_id,
                ),
                path=".",
            )
        raise ValueError("Invalid Resource")

    def recreate_endpoint_and_file(self) -> dict:
        """
        Recreates the endpoint and file reference from the given resource

        :return: (dict) {"file": fileref, "endpoint": endpoint}
        :raises: ValueError (invalid resource)
        """
        endpoint = self._storage_id
        if self._space_id:
            endpoint += f"${self._space_id}"
        if self._abs_path:
            return {"file": self._abs_path, "endpoint": endpoint}
        if self._parent_id and self._rel_path:
            return {"file": f"{self._parent_id}{self._rel_path}", "endpoint": endpoint}
        if self._opaque_id:
            return {"file": self._opaque_id, "endpoint": endpoint}
        raise ValueError("Invalid Resource")

    @classmethod
    def from_cs3_ref(cls, reference: cs3spr.Reference) -> "Resource":
        """
        Alternate constructor that reverses a CS3 reference to obtain a resource.

        :param reference: The CS3 reference.
        :return: Resource object.
        :raises: ValueError (Invalid reference)
        """
        rel_path = None
        opaque_id = None
        parent_id = None
        storage_id = None
        space_id = None

        if reference.path and reference.path.startswith("/"):
            # It's an absolute path, we can return straight away
            return Resource(abs_path=reference.path)
        elif reference.resource_id and reference.resource_id.storage_id:
            storage_id = reference.resource_id.storage_id
            if reference.resource_id.space_id:
                space_id = reference.resource_id.space_id
            if reference.path and len(reference.path) > 1:
                # It's a relative path (remove the "." in the relative path)
                rel_path = reference.path[1:]
                # The opaque_id is a parent id since it's a relative path
                parent_id = reference.resource_id.opaque_id
            else:
                opaque_id = reference.resource_id.opaque_id
            return Resource(
                abs_path=None,
                rel_path=rel_path,
                opaque_id=opaque_id,
                parent_id=parent_id,
                storage_id=storage_id,
                space_id=space_id,
            )
        raise ValueError("Invalid CS3 reference")

    # It is possible that the same resource is different if abs_path is used in one
    # and the other is using opaque_id for example.
    def __eq__(self, other):
        """redefine the equality operator to compare two resources"""
        if isinstance(other, Resource):
            return (
                self._abs_path == other._abs_path
                and self._rel_path == other._rel_path
                and self._parent_id == other._parent_id
                and self._opaque_id == other._opaque_id
                and self._space_id == other._space_id
                and self._storage_id == other._storage_id
            )
        return False

    def get_file_ref_str(self):
        """
        Generates a string from the file ref, '<type>="fileref">'

        :return: str '<type>="fileref">'
        :raises: ValueError (Invalid Resource)
        """
        if self._abs_path:
            return f'absolute_path="{self._abs_path}"'
        elif self._rel_path:
            return f'relative_path="{self._parent_id}/{self._rel_path}"'
        elif self._opaque_id:
            return f'opaque_id="{self._opaque_id}"'
        raise ValueError("Invalid Resource")

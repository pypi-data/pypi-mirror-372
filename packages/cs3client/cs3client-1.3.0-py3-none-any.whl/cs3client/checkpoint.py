"""
checkpoint.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

from typing import Generator, Optional
import logging

import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr
import cs3.storage.provider.v1beta1.provider_api_pb2 as cs3spp
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub

from .config import Config
from .statuscodehandler import StatusCodeHandler
from .cs3resource import Resource


class Checkpoint:
    """
    Checkpoint class to handle checkpoint related API calls with CS3 Gateway API.
    """

    def __init__(
        self,
        config: Config,
        log: logging.Logger,
        gateway: GatewayAPIStub,
        status_code_handler: StatusCodeHandler,
    ) -> None:
        """
        Initializes the checkpoint class with configuration, logger, auth, and gateway stub,

        :param config: Config object containing the configuration parameters.
        :param log: Logger instance for logging.
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway.
        :param status_code_handler: An instance of the StatusCodeHandler class.
        """
        self._gateway: GatewayAPIStub = gateway
        self._log: logging.Logger = log
        self._config: Config = config
        self._status_code_handler: StatusCodeHandler = status_code_handler

    def list_file_versions(
        self, auth_token: tuple, resource: Resource, page_token: str = "", page_size: int = 0
    ) -> Generator[cs3spr.FileVersion, any, any]:
        """
        List all versions of a file.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource object containing the resource information.
        :param page_token: Token for pagination.
        :param page_size: Number of file versions to return.
                          (default is zero, where the server decides the number of versions to return)
        :return: List of file versions (None if no versions are found).
        :raises: AuthenticationException (Operation not permitted)
        :raises: NotFoundException (File not found)
        :raises: UnknownException (Unknown error)
        """
        req = cs3spp.ListFileVersionsRequest(ref=resource.ref, page_token=page_token, page_size=page_size)
        res = self._gateway.ListFileVersions(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list file versions", f"{resource.get_file_ref_str()}")
        self._log.debug(f'msg="list file versions" {resource.get_file_ref_str()}  trace="{res.status.trace}"')
        return res.versions

    def restore_file_version(
            self, auth_token: tuple, resource: Resource, version_key: str, lock_id: Optional[str] = None
    ) -> None:
        """
        Restore a file to a previous version.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource object containing the resource information.
        :param version_key: Key of the version to restore.
        :param lock_id: Lock ID of the file (OPTIONAL).
        :return: None (Success)
        :raises: AuthenticationException (Operation not permitted)
        :raises: NotFoundException (File not found)
        :raises: UnknownException (Unknown error)
        """
        req = cs3spp.RestoreFileVersionRequest(ref=resource.ref, key=version_key, lock_id=lock_id)
        res = self._gateway.RestoreFileVersion(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "restore file version", f"{resource.get_file_ref_str()}")
        self._log.debug(f'msg="restore file version" {resource.get_file_ref_str()}  trace="{res.status.trace}"')
        return

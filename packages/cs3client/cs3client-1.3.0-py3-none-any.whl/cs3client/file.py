"""
file.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import time
import logging
import http
import requests
from typing import Union, Optional, Generator
import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr
import cs3.storage.provider.v1beta1.provider_api_pb2 as cs3sp
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub
import cs3.types.v1beta1.types_pb2 as types
import cs3.rpc.v1beta1.code_pb2 as cs3code


from .config import Config
from .exceptions import AuthenticationException, FileLockedException, NotFoundException
from .cs3resource import Resource
from .statuscodehandler import StatusCodeHandler

LOCK_ATTR_KEY = 'cs3client.advlock'


class File:
    """
    File class to interact with the CS3 API.
    """

    def __init__(
            self, config: Config, log: logging.Logger, gateway: GatewayAPIStub,
            status_code_handler: StatusCodeHandler
    ) -> None:
        """
        Initializes the File class with configuration, logger, auth, gateway stub, and status code handler.

        :param config: Config object containing the configuration parameters
        :param log: Logger instance for logging
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway
        :param status_code_handler: An instance of the StatusCodeHandler class
        """
        self._config: Config = config
        self._log: logging.Logger = log
        self._gateway: GatewayAPIStub = gateway
        self._status_code_handler: StatusCodeHandler = status_code_handler

    def stat(self, auth_token: tuple, resource: Resource) -> cs3spr.ResourceInfo:
        """
        Stat a file and return the ResourceInfo object.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: resource to stat
        :return: cs3.storage.provider.v1beta1.resources_pb2.ResourceInfo (success)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)

        """
        tstart = time.time()
        res = self._gateway.Stat(request=cs3sp.StatRequest(ref=resource.ref), metadata=[auth_token])
        tend = time.time()
        self._status_code_handler.handle_errors(res.status, "stat", resource.get_file_ref_str())
        self._log.info(
            f'msg="Invoked Stat" fileref="{resource.ref}" {resource.get_file_ref_str()}  trace="{res.status.trace}" '
            f'elapsedTimems="{(tend - tstart) * 1000:.1f}"'
        )
        return res.info

    def set_xattr(self, auth_token: tuple, resource: Resource, key: str, value: str, lock_id: Optional[str] = None) -> None:
        """
        Set the extended attribute <key> to <value> for a resource.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: resource that has the attribute.
        :param key: attribute key
        :param value: value to set
        :param lock_id: lock id
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown error)
        """
        md = cs3spr.ArbitraryMetadata()
        md.metadata.update({key: value})  # pylint: disable=no-member
        req = cs3sp.SetArbitraryMetadataRequest(ref=resource.ref, arbitrary_metadata=md, lock_id=lock_id)
        res = self._gateway.SetArbitraryMetadata(request=req, metadata=[auth_token])
        # CS3 storages may refuse to set an xattr in case of lock mismatch: this is an overprotection,
        # as the lock should concern the file's content, not its metadata, however we need to handle that
        self._status_code_handler.handle_errors(res.status, "set extended attribute", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked setxattr" trace="{res.status.trace}"')

    def remove_xattr(self, auth_token: tuple, resource: Resource, key: str, lock_id: Optional[str] = None) -> None:
        """
        Remove the extended attribute <key>.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: cs3client resource
        :param key: key for attribute to remove
        :param lock_id: lock id
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: AuthenticationException (Authentication failed)
        :raises: UnknownException (Unknown error)
        """
        req = cs3sp.UnsetArbitraryMetadataRequest(ref=resource.ref, arbitrary_metadata_keys=[key], lock_id=lock_id)
        res = self._gateway.UnsetArbitraryMetadata(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "remove extended attribute", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked UnsetArbitraryMetaData" trace="{res.status.trace}"')

    def rename_file(
            self, auth_token: tuple, resource: Resource, newresource: Resource, lock_id: Optional[str] = None
    ) -> None:
        """
        Rename/move resource to new resource.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Original resource
        :param newresource: New resource
        :param lock_id: lock id
        :return: None (Success)
        :raises: NotFoundException (Original resource not found)
        :raises: FileLockException (Resource is locked)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        req = cs3sp.MoveRequest(source=resource.ref, destination=newresource.ref, lock_id=lock_id)
        res = self._gateway.Move(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "rename file", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked Move" trace="{res.status.trace}"')

    def remove_file(self, auth_token: tuple, resource: Resource, lock_id: Optional[str] = None) -> None:
        """
        Remove a resource.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource:  Resource to remove
        :param lock_id: lock id
        :return: None (Success)
        :raises: AuthenticationException (Authentication Failed)
        :raises: NotFoundException (Resource not found)
        :raises: UnknownException (Unknown error)
        """
        req = cs3sp.DeleteRequest(ref=resource.ref, lock_id=lock_id)
        res = self._gateway.Delete(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "remove file", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked Delete" trace="{res.status.trace}"')

    def touch_file(self, auth_token: tuple, resource: Resource) -> None:
        """
        Create a resource.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to create
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown error)
        """
        req = cs3sp.TouchFileRequest(
            ref=resource.ref,
            opaque=types.Opaque(map={"Upload-Length": types.OpaqueEntry(decoder="plain", value=str.encode("0"))}),
        )
        res = self._gateway.TouchFile(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "touch file", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked TouchFile" trace="{res.status.trace}"')

    def write_file(
            self, auth_token: tuple, resource: Resource, content: Union[str, bytes], size: int,
            app_name: Optional[str] = None, lock_id: Optional[str] = None,
            disable_versioning: Optional[bool] = False
    ) -> None:
        """
        Write a file using the given userid as access token. The entire content is written
        and any pre-existing file is deleted (or moved to the previous version if supported),
        writing a file with size 0 is equivalent to "touch file" and should be used if the
        implementation does not support touchfile.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to write content to
        :param content: content to write
        :param size: size of content (optional)
        :param app_name: application name (optional)
        :param lock_id: lock id (optional)
        :param disable_versioning: bool to disable versioning on EOS (optional)
        :return: None (Success)
        :raises: FileLockedException (File is locked),
        :raises: AuthenticationException (Authentication failed)
        :raises: UnknownException (Unknown error)

        """
        tstart = time.time()
        # prepare endpoint
        if size == -1:
            if isinstance(content, str):
                content = bytes(content, "UTF-8")
            size = len(content)
        req = cs3sp.InitiateFileUploadRequest(
            ref=resource.ref,
            opaque=types.Opaque(map={"Upload-Length": types.OpaqueEntry(decoder="plain", value=str.encode(str(size)))}),
            lock_id=lock_id
        )
        res = self._gateway.InitiateFileUpload(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "write file", resource.get_file_ref_str())
        tend = time.time()
        self._log.debug(
            f'msg="Invoked InitiateFileUpload" trace="{res.status.trace}" protocols="{res.protocols}"'
        )

        # Upload
        try:
            protocol = [p for p in res.protocols if p.protocol in ["simple", "spaces"]][0]
            if self._config.tus_enabled:
                headers = {
                    "Tus-Resumable": "1.0.0",
                    "File-Path": resource.file,
                    "File-Size": str(size),
                    "X-Reva-Transfer": protocol.token,
                    **dict([auth_token]),
                    "X-Lock-Id": lock_id,
                    "X-Lock_Holder": app_name,
                }
            else:
                headers = {
                    "Upload-Length": str(size),
                    "Content-Length": str(size),
                    "X-Reva-Transfer": protocol.token,
                    **dict([auth_token]),
                    "X-Lock-Id": lock_id,
                    "X-Lock-Holder": app_name,
                }
            if disable_versioning:
                headers.update({"X-Disable-Versioning": "true"})
            putres = requests.put(
                url=protocol.upload_endpoint,
                data=content,
                headers=headers,
                verify=self._config.ssl_verify,
                timeout=self._config.http_timeout,
            )
        except requests.exceptions.RequestException as e:
            self._log.error(f'msg="Exception when uploading file to Reva" reason="{e}"')
            raise IOError(e) from e
        if putres.status_code == http.client.CONFLICT:
            self._log.info(
                f'msg="Got conflict on PUT, file is locked" reason="{putres.reason}" {resource.get_file_ref_str()}'
            )
            raise FileLockedException(f"Lock mismatch or lock expired: {putres.reason}")
        if putres.status_code == http.client.UNAUTHORIZED:
            self._log.warning(
                f'msg="Authentication failed on write" reason="{putres.reason}" {resource.get_file_ref_str()}'
            )
            raise AuthenticationException(f"Operation not permitted: {putres.reason}")
        if putres.status_code != http.client.OK:
            if (
                size == 0
            ):  # 0-byte file uploads may have been finalized after InitiateFileUploadRequest, let's assume it's OK
                # Should use TouchFileRequest instead
                self._log.info(
                    f'msg="0-byte file written successfully" {resource.get_file_ref_str()} '
                    f' elapsedTimems="{(tend - tstart) * 1000:.1f}"'
                )
                return

            self._log.error(
                f'msg="Error uploading file" code="{putres.status_code}" reason="{putres.reason}"'
            )
            raise IOError(putres.reason)
        self._log.info(
            f'msg="File written successfully" {resource.get_file_ref_str()} '
            f'elapsedTimems="{(tend - tstart) * 1000:.1f}"'
        )

    def read_file(self, auth_token: tuple, resource: Resource, lock_id: Optional[str] = None) -> Generator[bytes, None, None]:
        """
        Read a file. Note that the function is a generator, managed by the app server.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to read
        :param lock_id: lock id
        :return: Generator[Bytes, None, None] (Success)
        :raises: NotFoundException (Resource not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        tstart = time.time()

        # prepare endpoint
        req = cs3sp.InitiateFileDownloadRequest(ref=resource.ref, lock_id=lock_id)
        res = self._gateway.InitiateFileDownload(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "read file", resource.get_file_ref_str())
        tend = time.time()
        self._log.debug(
            f'msg="Invoked InitiateFileDownload" trace="{res.status.trace}" protocols="{res.protocols}"'
        )

        # Download
        try:
            protocol = [p for p in res.protocols if p.protocol in ["simple", "spaces"]][0]
            headers = {"X-Reva-Transfer": protocol.token, **dict([auth_token])}
            fileget = requests.get(
                url=protocol.download_endpoint,
                headers=headers,
                verify=self._config.ssl_verify,
                timeout=self._config.http_timeout,
                stream=True,
            )
        except requests.exceptions.RequestException as e:
            self._log.error(f'msg="Exception when downloading file from Reva" reason="{e}"')
            raise IOError(e)
        data = fileget.iter_content(self._config.chunk_size)
        if fileget.status_code != http.client.OK:
            # status.message.replace('"', "'") is not allowed inside f strings python<3.12
            status_msg = fileget.reason.replace('"', "'")
            self._log.error(
                f'msg="Error downloading file from Reva" code="{fileget.status_code}" '
                f'reason="{status_msg}"'
            )
            if fileget.status_code == http.client.NOT_FOUND:
                raise NotFoundException
            else:
                raise IOError(fileget.reason)
        else:
            self._log.info(
                f'msg="File open for read" {resource.get_file_ref_str()} elapsedTimems="{(tend - tstart) * 1000:.1f}"'
            )
            for chunk in data:
                yield chunk

    def make_dir(self, auth_token: tuple, resource: Resource) -> None:
        """
        Create a directory.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Direcotry to create
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: AuthenticationException (Authentication failed)
        :raises: UnknownException (Unknown error)
        """
        req = cs3sp.CreateContainerRequest(ref=resource.ref)
        res = self._gateway.CreateContainer(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "make directory", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked CreateContainer" trace="{res.status.trace}"')

    def list_dir(
            self, auth_token: tuple, resource: Resource
    ) -> Generator[cs3spr.ResourceInfo, None, None]:
        """
        List the contents of a directory, note that the function is a generator.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: the directory
        :return: Generator[cs3.storage.provider.v1beta1.resources_pb2.ResourceInfo, None, None] (Success)
        :raises: NotFoundException (Resrouce not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown error)
        """
        req = cs3sp.ListContainerRequest(ref=resource.ref)
        res = self._gateway.ListContainer(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list directory", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked ListContainer" trace="{res.status.trace}"')
        for info in res.infos:
            yield info

    def _set_lock_using_xattr(self, auth_token, resource: Resource, app_name: str, lock_id: Union[int, str]) -> None:
        """"
        Set a lock to a resource with the given value metadata and appname as holder

        :param resource: Resource to set lock to
        :param app_name: Application name
        :param lock_id: Metadata lock value
        :return: None (Success)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        self._log.debug(f'msg="Using xattrs to execute SetLock" {resource.get_file_ref_str()}" value="{lock_id}"')
        try:
            # The stat can raise a KeyError if the metadata (lock) attribute has not been set yet
            # e.g. the file is not locked
            _ = self.stat(auth_token, resource).arbitrary_metadata.metadata[LOCK_ATTR_KEY]
        except KeyError:
            expiration = int(time.time() + self._config.lock_expiration)
            self.set_xattr(auth_token, resource, LOCK_ATTR_KEY, f"{app_name}!{lock_id}!{expiration}", None)
            return

    def set_lock(self, auth_token: tuple, resource: Resource, app_name: str, lock_id: Union[int, str]) -> None:
        """
        Set a lock to a resource with the given value and appname as holder

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to set lock to
        :param app_name: Application name
        :param lock_id: encoded lock_id or metadata lock value if using xattr
        :return: None (Success)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        # fallback to xattr if the storage does not support locks
        if self._config.lock_by_setting_attr and self._config.lock_not_impl:
            self._set_lock_using_xattr(auth_token, resource, app_name, lock_id)
            return

        lock = cs3spr.Lock(
            type=cs3spr.LOCK_TYPE_WRITE,
            lock_id=lock_id,
            app_name=app_name,
            expiration={"seconds": int(time.time() + + self._config.lock_expiration)},
        )
        req = cs3sp.SetLockRequest(ref=resource.ref, lock=lock)
        res = self._gateway.SetLock(request=req, metadata=[auth_token])

        # if the storage does not support locks, set the lock using xattr
        if res.status.code == cs3code.CODE_UNIMPLEMENTED and self._config.lock_by_setting_attr:
            self._config.lock_not_impl = True
            self._set_lock_using_xattr(auth_token, resource, app_name, lock_id)
            return

        self._status_code_handler.handle_errors(res.status, "set lock", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked SetLock" {resource.get_file_ref_str()}" '
                        f'value="{lock_id} result="{res.status.trace}"')

    def _get_lock_using_xattr(self, auth_token: tuple, resource: Resource) -> dict:
        """
        Get the lock metadata for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to get lock from
        :return: dictionary (KEYS: lock_id, type, app_name, user, expiration) (Success)
        :return: None (No lock set)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        self._log.debug(f'msg="Using xattrs to execute getlock" {resource.get_file_ref_str()}"')
        try:
            currvalue = self.stat(auth_token, resource).arbitrary_metadata.metadata[LOCK_ATTR_KEY]
            values = currvalue.split("!")
            return {
                "lock_id": values[1],
                "type": 2,  # LOCK_TYPE_WRITE, though this is advisory!
                "app_name": values[0],
                "user": {},
                "expiration": int(values[2]),
            }
        except KeyError:
            return None

    def get_lock(self, auth_token: tuple, resource: Resource) -> Union[cs3spr.Lock, dict, None]:
        """
        Get the lock for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to get lock from
        :return: dictionary (KEYS: lock_id, type, app_name, user, expiration) (Success)
        :return: None (No lock set)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        # fallback to xattr if the storage does not support locks
        if self._config.lock_by_setting_attr and self._config.lock_not_impl:
            return self._get_lock_using_xattr(auth_token, resource)

        req = cs3sp.GetLockRequest(ref=resource.ref)
        res = self._gateway.GetLock(request=req, metadata=[auth_token])

        # if the storage does not support locks, get the lock using xattr
        if res.status.code == cs3code.CODE_UNIMPLEMENTED and self._config.lock_by_setting_attr:
            self._config.lock_not_impl = True
            return self._get_lock_using_xattr(auth_token, resource)

        self._status_code_handler.handle_errors(res.status, "get lock", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked GetLock" {resource.get_file_ref_str()}" result="{res.status.trace}"')

        # rebuild a dict corresponding to the internal JSON structure used by Reva
        return {
            "lock_id": res.lock.lock_id,
            "type": res.lock.type,
            "app_name": res.lock.app_name,
            "user": (
                {"opaque_id": res.lock.user.opaque_id, "idp": res.lock.user.idp, "type": res.lock.user.type}
                if res.lock.user.opaque_id
                else {}
            ),
            "expiration": {"seconds": res.lock.expiration.seconds},
        }

    def _refresh_lock_using_xattr(
            self, auth_token: tuple, resource: Resource, app_name: str, lock_id: Union[str, int],
            existing_lock_id: Union[str, int] = None
    ) -> None:
        """
        Refresh the lock metadata for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to refresh lock for
        :param app_name: Application name
        :param lock_id: metadata value to set
        :param existing_lock_id: existing metadata vlue
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        self._log.debug(f'msg="Using xattrs to execute RefreshLock" {resource.get_file_ref_str()}" value="{lock_id}"')
        try:
            # The stat can raise a KeyError if the metadata (lock) attribute has not been set yet
            # e.g. the file is not locked
            currvalue = self.stat(auth_token, resource).arbitrary_metadata.metadata[LOCK_ATTR_KEY]
            values = currvalue.split("!")
            if values[0] == app_name and (not existing_lock_id or values[1] == existing_lock_id):
                raise KeyError
            self._log.info(
                f'Failed precondition on RefreshLock" {resource.get_file_ref_str()}" appname="{app_name}" '
                f'value="{lock_id} previouslock="{currvalue}"'
            )
            raise FileLockedException()
        except KeyError:
            expiration = int(time.time() + self._config.lock_expiration)
            self.set_xattr(auth_token, resource, LOCK_ATTR_KEY, f"{app_name}!{lock_id}!{expiration}", None)
            return

    def refresh_lock(
            self, auth_token: tuple, resource: Resource, app_name: str, lock_id: Union[str, int],
            existing_lock_id: Union[str, int] = None
    ):
        """
        Refresh the lock for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to refresh lock for
        :param app_name: Application name
        :param lock_id: encoded lock_id or metadata lock value if using xattr
        :param existing_lock_id: encoded lock_id or metadata lock value if using xattr
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        # fallback to xattr if the storage does not support locks
        if self._config.lock_by_setting_attr and self._config.lock_not_impl:
            self._refresh_lock_using_xattr(auth_token, resource, app_name, lock_id, existing_lock_id)
            return

        lock = cs3spr.Lock(
            type=cs3spr.LOCK_TYPE_WRITE,
            app_name=app_name,
            lock_id=lock_id,
            expiration={"seconds": int(time.time() + self._config.lock_expiration)},
        )
        req = cs3sp.RefreshLockRequest(ref=resource.ref, lock=lock, existing_lock_id=existing_lock_id)
        res = self._gateway.RefreshLock(request=req, metadata=[auth_token])

        # if the storage does not support locks, refresh the lock using xattr
        if res.status.code == cs3code.CODE_UNIMPLEMENTED and self._config.lock_by_setting_attr:
            self._config.lock_not_impl = True
            self._refresh_lock_using_xattr(auth_token, resource, app_name, lock_id, existing_lock_id)
            return
        self._status_code_handler.handle_errors(res.status, "refresh lock", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked RefreshLock" {resource.get_file_ref_str()} result="{res.status.trace}" '
                        f'value="{lock_id}" old_value="{existing_lock_id}"')

    def _unlock_using_xattr(
            self, auth_token: tuple, resource: Resource, app_name: str, lock_id: Union[str, int]
    ) -> None:
        """
        Remove the lock for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to unlock
        :param app_name: Application name
        :param lock_id: metadata lock value
        :return: None (Success)
        :raises: FileLockedException (File is locked)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        self._log.debug(f'msg="Using xattrs to execute unlock" {resource.get_file_ref_str()}" value="{lock_id}"')
        try:
            # The stat can raise a KeyError if the metadata (lock) attribute has not been set yet
            # e.g. the file is not locked
            currvalue = self.stat(auth_token, resource).arbitrary_metadata.metadata[LOCK_ATTR_KEY]
            values = currvalue.split("!")
            if values[0] == app_name and values[1] == lock_id:
                raise KeyError
            self._log.info(
                f'Failed precondition on unlock" {resource.get_file_ref_str()}" appname="{app_name}" '
                f'value={lock_id} previouslock="{currvalue}"'
            )
            raise FileLockedException()
        except KeyError:
            self.remove_xattr(auth_token, resource, LOCK_ATTR_KEY, None)
            return

    def unlock(self, auth_token: tuple, resource: Resource, app_name, lock_id: Union[str, int]):
        """
        Remove the lock for the given filepath

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource to unlock
        :param app_name: app_name
        :param lock_id: encoded lock_id or metadata lock value if using xattr
        :return: None
        :raises: FileLockedException (File is locked)
        :raises: NotFoundException (File not found)
        :raises: AuthenticationException (Authentication Failed)
        :raises: UnknownException (Unknown Error)
        """
        # fallback to xattr if the storage does not support locks
        if self._config.lock_by_setting_attr and self._config.lock_not_impl:
            self._unlock_using_xattr(auth_token, resource, app_name, lock_id)
            return

        lock = cs3spr.Lock(type=cs3spr.LOCK_TYPE_WRITE, app_name=app_name, lock_id=lock_id)
        req = cs3sp.UnlockRequest(ref=resource.ref, lock=lock)
        res = self._gateway.Unlock(request=req, metadata=[auth_token])

        # if the storage does not support locks, set the lock using xattr and retry
        if res.status.code == cs3code.CODE_UNIMPLEMENTED and self._config.lock_by_setting_attr:
            self._config.lock_not_impl = True
            self._unlock_using_xattr(auth_token, resource, app_name, lock_id)
            return

        self._status_code_handler.handle_errors(res.status, "unlock", resource.get_file_ref_str())
        self._log.debug(f'msg="Invoked Unlock" {resource.get_file_ref_str()} result="{res.status.trace}" '
                        f'value="{lock_id}"')

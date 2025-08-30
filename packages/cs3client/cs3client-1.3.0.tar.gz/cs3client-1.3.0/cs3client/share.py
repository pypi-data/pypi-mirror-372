"""
share.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import logging
from typing import Optional

import cs3.sharing.collaboration.v1beta1.collaboration_api_pb2 as cs3scapi
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub
import cs3.sharing.collaboration.v1beta1.resources_pb2 as cs3scr
import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr
import cs3.identity.group.v1beta1.resources_pb2 as cs3igr
import cs3.identity.user.v1beta1.resources_pb2 as cs3iur
import cs3.sharing.link.v1beta1.link_api_pb2 as cs3slapi
import cs3.sharing.link.v1beta1.resources_pb2 as cs3slr
import google.protobuf.field_mask_pb2 as field_masks
import cs3.types.v1beta1.types_pb2 as cs3types

from .cs3resource import Resource
from .config import Config
from .statuscodehandler import StatusCodeHandler


class Share:
    """
    Share class to handle share related API calls with the CS3 Gateway API.
    """

    def __init__(
        self,
        config: Config,
        log: logging.Logger,
        gateway: GatewayAPIStub,
        status_code_handler: StatusCodeHandler,
    ) -> None:
        """
        Initializes the Share class with configuration, logger, auth, and gateway stub,

        :param config: Config object containing the configuration parameters.
        :param log: Logger instance for logging.
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway.
        :param status_code_handler: An instance of the StatusCodeHandler class.
        """
        self._status_code_handler: StatusCodeHandler = status_code_handler
        self._gateway: GatewayAPIStub = gateway
        self._log: logging.Logger = log
        self._config: Config = config

    def create_share(
        self,
        auth_token: tuple,
        resource_info: cs3spr.ResourceInfo,
        opaque_id: str,
        idp: str,
        role: str,
        grantee_type: str
    ) -> cs3scr.Share:
        """
        Create a share for a resource to the user/group with the specified role, using their opaque id and idp.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource_info: Resource info, see file.stat (REQUIRED).
        :param opaque_id: Opaque group/user id, (REQUIRED).
        :param idp: Identity provider, (REQUIRED).
        :param role: Role to assign to the grantee, VIEWER or EDITOR (REQUIRED).
        :param grantee_type: Type of grantee, USER or GROUP (REQUIRED).
        :return: Share object.
        :raises: NotFoundException (Resource not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: FileLockedException (Resource Locked)
        :raises: AlreadyExistsException (Share already exists)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid values)
        """
        share_grant = Share._create_share_grant(opaque_id, idp, role, grantee_type)
        req = cs3scapi.CreateShareRequest(resource_info=resource_info, grant=share_grant)
        res = self._gateway.CreateShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "create share", f'opaque_id="{opaque_id}" resource_id="{resource_info.id}"'
        )
        self._log.debug(
            f'msg="Invoked CreateShare" opaque_id="{opaque_id}" resource_id="{resource_info.id}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def list_existing_shares(
        self, auth_token: tuple, filter_list: list[cs3scr.Filter] = None, page_size: int = 0, page_token: Optional[str] = None
    ) -> list[cs3scr.Share]:
        """
        List shares based on a filter.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param filter: Filter object to filter the shares, see create_share_filter.
        :param page_size: Number of shares to return in a page, defaults to 0, server decides.
        :param page_token: Token to get to a specific page.
        :return: (List of shares (may be empty), next page token)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3scapi.ListSharesRequest(filters=filter_list, page_size=page_size, page_token=page_token)
        res = self._gateway.ListExistingShares(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list existing shares", f'filter="{filter_list}"')
        self._log.debug(
            f'msg="Invoked ListExistingShares" filter="{filter_list}" res_count="{len(res.share_infos)}'
            f'trace="{res.status.trace}"'
        )
        return (res.share_infos, res.next_page_token)

    def get_share(self, auth_token: tuple, opaque_id: Optional[str] = None, share_key: Optional[cs3scr.ShareKey] = None) -> cs3scr.Share:
        """
        Get a share by its opaque id or share key (combination of resource_id, grantee and owner),
        one of them is required.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param opaque_id: Opaque share id (SEMI-OPTIONAL).
        :param share_key: Share key, see ShareKey definition in cs3apis (SEMI-OPTIONAL).
        :return: Share object.
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (both opaque_id and share_key are missing)
        """
        req = None
        if opaque_id:
            req = cs3scapi.GetShareRequest(ref=cs3scr.ShareReference(id=cs3scr.ShareId(opaque_id=opaque_id)))
        elif share_key:
            req = cs3scapi.GetShareRequest(ref=cs3scr.ShareReference(key=share_key))
        else:
            raise ValueError("opaque_id or share_key is required")

        res = self._gateway.GetShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "get share", f'opaque_id/share_key="{opaque_id if opaque_id else share_key}"'
        )
        self._log.debug(
            f'msg="Invoked GetShare" opaque_id/share_key="{opaque_id if opaque_id else share_key}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def remove_share(self, auth_token: tuple, opaque_id: Optional[str] = None, share_key: Optional[cs3scr.ShareKey] = None) -> None:
        """
        Remove a share by its opaque id or share key (combination of resource_id, grantee and owner),
        one of them is required.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param opaque_id: Opaque share id (SEMI-OPTIONAL).
        :param share_key: Share key, see ShareKey definition in cs3apis (SEMI-OPTIONAL).
        :return: None
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (both opaque_id and share_key are missing)
        """
        req = None
        if opaque_id:
            req = cs3scapi.RemoveShareRequest(ref=cs3scr.ShareReference(id=cs3scr.ShareId(opaque_id=opaque_id)))
        elif share_key:
            req = cs3scapi.RemoveShareRequest(ref=cs3scr.ShareReference(key=share_key))
        else:
            raise ValueError("opaque_id or share_key is required")
        res = self._gateway.RemoveShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "remove share", f'opaque_id/share_key="{opaque_id if opaque_id else share_key}"'
        )
        self._log.debug(
            f'msg="Invoked RemoveShare" opaque_id/share_key="{opaque_id if opaque_id else share_key}" '
            f'trace="{res.status.trace}"'
        )
        return

    def update_share(
        self, auth_token: tuple,
        role: str,
        opaque_id: Optional[str] = None,
        share_key: Optional[cs3scr.ShareKey] = None,
        display_name: Optional[str] = None
    ) -> cs3scr.Share:
        """
        Update a share by its opaque id.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param opaque_id: Opaque share id. (SEMI-OPTIONAL).
        :param share_key: Share key, see ShareKey definition in cs3apis (SEMI-OPTIONAL).
        :param role: Role to update the share, VIEWER or EDITOR (REQUIRED).
        :param display_name: new display name.
        :return: Share object
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid or missing values)
        """
        permissions = cs3scr.SharePermissions(permissions=Share._create_permissions(role))
        update = cs3scapi.UpdateShareRequest.UpdateField(permissions=permissions, display_name=display_name)

        ref = None
        if opaque_id:
            ref = cs3scr.ShareReference(id=cs3scr.ShareId(opaque_id=opaque_id))
        elif share_key:
            ref = cs3scr.ShareReference(key=share_key)
        else:
            raise ValueError("opaque_id or share_key is required")

        req = cs3scapi.UpdateShareRequest(ref=ref, field=update)
        res = self._gateway.UpdateShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "update share", f'opaque_id/share_key="{opaque_id if opaque_id else share_key}"'
        )
        self._log.debug(
            f'msg="Invoked UpdateShare" opaque_id/share_key="{opaque_id if opaque_id else share_key}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def list_received_existing_shares(
        self, auth_token: tuple, filter_list: Optional[list] = None, page_size: int = 0, page_token: Optional[str] = None
    ) -> list:
        """
        List received existing shares.
        NOTE: Filters for received shares are not yet implemented (14/08/2024)

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param filter: Filter object to filter the shares, see create_share_filter.
        :param page_size: Number of shares to return in a page, defaults to 0, server decides.
        :param page_token: Token to get to a specific page.
        :return: List of received shares.
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3scapi.ListReceivedSharesRequest(filters=filter_list, page_size=page_size, page_token=page_token)
        res = self._gateway.ListExistingReceivedShares(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list received existing shares", f'filter="{filter_list}"')
        self._log.debug(
            f'msg="Invoked ListExistingReceivedShares" filter="{filter_list}" res_count="{len(res.share_infos)}"'
            f'trace="{res.status.trace}"'
        )
        return (res.share_infos, res.next_page_token)

    def get_received_share(
            self, auth_token: tuple, opaque_id: Optional[str] = None, share_key: Optional[cs3scr.ShareKey] = None
    ) -> cs3scr.ReceivedShare:
        """
        Get a received share by its opaque id or share key (combination of resource_id, grantee and owner),
        one of them is required.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param opaque_id: Opaque share id. (SEMI-OPTIONAL).
        :param share_key: Share key, see ShareKey definition in cs3apis (SEMI-OPTIONAL).
        :return: ReceivedShare object.
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (both opaque_id and share_key are missing)
        """
        req = None
        if opaque_id:
            req = cs3scapi.GetReceivedShareRequest(ref=cs3scr.ShareReference(id=cs3scr.ShareId(opaque_id=opaque_id)))
        elif share_key:
            req = cs3scapi.GetReceivedShareRequest(ref=cs3scr.ShareReference(key=share_key))
        else:
            raise ValueError("opaque_id or share_key is required")
        res = self._gateway.GetReceivedShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "get received share", f'opaque_id/share_key="{opaque_id if opaque_id else share_key}"'
        )
        self._log.debug(
            f'msg="Invoked GetReceivedShare" opaque_id/share_key="{opaque_id if opaque_id else share_key}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def update_received_share(
        self, auth_token: tuple, received_share: cs3scr.ReceivedShare, state: str = "SHARE_STATE_ACCEPTED"
    ) -> cs3scr.ReceivedShare:
        """
        Update the state of a received share (SHARE_STATE_ACCEPTED, SHARE_STATE_ACCEPTED, SHARE_STATE_REJECTED).

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param recieved_share: ReceivedShare object.
        :param state: Share state to update to, defaults to SHARE_STATE_ACCEPTED, (REQUIRED).
        :return: Updated ReceivedShare object.
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        resource = Resource(
            opaque_id=received_share.share.resource_id.opaque_id,
            storage_id=received_share.share.resource_id.storage_id,
        )
        req = cs3scapi.UpdateReceivedShareRequest(
            share=cs3scr.ReceivedShare(
                share=received_share.share,
                state=cs3scr.ShareState.Value(state),
                mount_point=resource.ref,
            ),
            update_mask=field_masks.FieldMask(paths=["state"]),
        )
        res = self._gateway.UpdateReceivedShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "update received share", f'opaque_id="{received_share.share.id.opaque_id}"'
        )
        self._log.debug(
            f'msg="Invoked UpdateReceivedShare" opaque_id="{received_share.share.id.opaque_id}" new_state="{state}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def create_public_share(
        self,
        auth_token: tuple,
        resource_info: cs3spr.ResourceInfo,
        role: str,
        password: Optional[str] = None,
        expiration: Optional[cs3types.Timestamp] = None,
        description: Optional[str] = None,
        internal: bool = False,
        notify_uploads: bool = False,
        notify_uploads_extra_recipients: Optional[list] = None,
    ) -> cs3slr.PublicShare:
        """
        Create a public share.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource_info: Resource info, see file.stat (REQUIRED).
        :param role: Role to assign to the grantee, VIEWER or EDITOR (REQUIRED)
        :param password: Password to access the share.
        :param expiration: Expiration timestamp for the share.
        :param description: Description for the share.
        :param internal: Internal share flag.
        :param notify_upload: Notify upload flag.
        :param notify_uploads_extra_recipients: List of extra recipients to notify on upload.
        :return: Public Share object.
        :raises: NotFoundException (Resource not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: FileLockedException (Resource Locked)
        :raises: AlreadyExistsException (Share already exists)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid values)
        """
        permissions = cs3slr.PublicSharePermissions(permissions=Share._create_permissions(role))
        grant = cs3slr.Grant(permissions=permissions, password=password, expiration=expiration)

        req = cs3slapi.CreatePublicShareRequest(
            resource_info=resource_info,
            grant=grant,
            description=description,
            internal=internal,
            notify_uploads=notify_uploads,
            notify_uploads_extra_recipients=notify_uploads_extra_recipients,
        )

        res = self._gateway.CreatePublicShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "create public share", f'resource_id="{resource_info.id}"')
        self._log.debug(f'msg="Invoked CreatePublicShare" resource_id="{resource_info.id}" trace="{res.status.trace}"')
        return res.share

    def list_existing_public_shares(
        self, auth_token: tuple, filter_list: Optional[list] = None, page_size: int = 0, page_token: Optional[str] = None, sign: bool = False
    ) -> list:
        """
        List existing public shares.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param filter: Filter object to filter the shares, see create_public_share_filter.
        :param page_size: Number of shares to return in a page, defaults to 0 and then the server decides.
        :param page_token: Token to get to a specific page.
        :param sign: if the signature should be included in the share.
        :return: (List of public shares, next page token)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid values)
        """
        req = cs3slapi.ListPublicSharesRequest(
            filters=filter_list, page_size=page_size, page_token=page_token, sign=sign
        )
        res = self._gateway.ListExistingPublicShares(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list existing public shares", f'filter="{filter_list}"')
        self._log.debug(
            f'msg="Invoked ListExistingPublicShares" filter="{filter_list}" res_count="{len(res.share_infos)}" '
            f'trace="{res.status.trace}"'
        )
        return (res.share_infos, res.next_page_token)

    def get_public_share(
            self, auth_token: tuple, opaque_id: Optional[str] = None, token: Optional[str] = None, sign: bool = False
    ) -> cs3slr.PublicShare:
        """
        Get a public share by its opaque id or token, one of them is required.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param opaque_id: Opaque share id (SEMI-OPTIONAL).
        :param share_token: Share token (SEMI-OPTIONAL).
        :param sign: if the signature should be included in the share.
        :return: PublicShare object.
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid value or missing values)
        """
        ref = None
        if token:
            ref = cs3slr.PublicShareReference(token=token)
        elif opaque_id:
            ref = cs3slr.PublicShareReference(id=cs3slr.PublicShareId(opaque_id=opaque_id))
        else:
            raise ValueError("token or opaque_id is required")
        req = cs3slapi.GetPublicShareRequest(ref=ref, sign=sign)
        res = self._gateway.GetPublicShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "get public share", f'opaque_id/token="{opaque_id if opaque_id else token}"'
        )
        self._log.debug(
            f'msg="Invoked GetPublicShare" opaque_id/token="{opaque_id if opaque_id else token}" '
            f'trace="{res.status.trace}"'
        )
        return res.share

    def update_public_share(
        self,
        auth_token: tuple,
        type: str,
        role: str,
        opaque_id: Optional[str] = None,
        token: Optional[str] = None,
        password: Optional[str] = None,
        expiration: Optional[cs3types.Timestamp] = None,
        notify_uploads_extra_recipients: Optional[str] = None,
        description: Optional[str] = None,
        display_name: Optional[str] = None,
        notify_uploads: bool = False,
    ) -> None:
        """
        Update a public share by its opaque id or token. (one of them is required), role and type are required,
        however, other parameters are optional. Note that only the type of update specified will be applied.
        The role will only change if type is TYPE_PERMISSIONS.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param type: Type of update to perform TYPE_PERMISSIONS, TYPE_PASSWORD, TYPE_EXPIRATION, TYPE_DISPLAYNAME,
                        TYPE_DESCRIPTION, TYPE_NOTIFYUPLOADS, TYPE_NOTIFYUPLOADSEXTRARECIPIENTS (REQUIRED).
        :param role: Role to assign to the grantee, VIEWER or EDITOR (REQUIRED).
        :param opaque_id: Opaque share id (SEMI-OPTIONAL).
        :param token: Share token (SEMI-OPTIONAL).
        :param display_name: Display name for the share.
        :param description: Description for the share.
        :param notify_uploads: Notify uploads flag.
        :param expiration: Expiration timestamp for the share.
        :param notify_uploads_extra_recipients: List of extra recipients to notify on upload.
        :param password: Password to access the share.
        :return: PublicShare object.
        :raises: NotFoundException (Share not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        :raises: ValueError (Invalid or missing values)
        """
        ref = None
        if token:
            ref = cs3slr.PublicShareReference(token=token)
        elif opaque_id:
            ref = cs3slr.PublicShareReference(id=cs3slr.PublicShareId(opaque_id=opaque_id))
        else:
            raise ValueError("token or opaque_id is required")

        update = Share._create_public_share_update(
            type=type,
            role=role,
            expiration=expiration,
            display_name=display_name,
            description=description,
            notify_uploads=notify_uploads,
            notify_uploads_extra_recipients=notify_uploads_extra_recipients,
            password=password,
        )
        req = cs3slapi.UpdatePublicShareRequest(ref=ref, update=update)
        res = self._gateway.UpdatePublicShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status,
            "update public share",
            f'token/opaque_id="{opaque_id if opaque_id else token}" type="{type}"',
        )
        self._log.debug(
            f'msg="Invoked UpdatePublicShare" token/opaque_id="{opaque_id if opaque_id else token} "'
            f'type="{type}" trace="{res.status.trace}"'
        )
        return res.share

    def remove_public_share(self, auth_token: tuple, token: Optional[str] = None, opaque_id: Optional[str] = None) -> None:
        """
        Remove a public share by its token or opaque id, one of them is required.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param token: Share token (SEMI-OPTIONAL).
        :param opaque_id: Opaque share id (SEMI-OPTIONAL).
        :return: None
        :raises: ValueError if token or opaque_id is not provided.
        """
        ref = None
        if token:
            ref = cs3slr.PublicShareReference(token=token)
        elif opaque_id:
            ref = cs3slr.PublicShareReference(id=cs3slr.PublicShareId(opaque_id=opaque_id))
        else:
            raise ValueError("token or opaque_id is required")

        req = cs3slapi.RemovePublicShareRequest(ref=ref)
        res = self._gateway.RemovePublicShare(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(
            res.status, "remove public share", f'opaque_id/token="{opaque_id if opaque_id else token}"'
        )
        self._log.debug(
            f'msg="Invoked RemovePublicShare" opaque_id/token="{opaque_id if opaque_id else token}" '
            f'trace="{res.status.trace}"'
        )
        return

    @classmethod
    def _create_public_share_update(
        cls,
        type: str,
        role: str,
        password: Optional[str] = None,
        expiration: Optional[cs3types.Timestamp] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        notify_uploads: bool = False,
        notify_uploads_extra_recipients: Optional[str] = None,
    ) -> cs3slr.PublicShare:
        """
        Create a public share update object, based on the type the property will be updated,
        can be TYPE_PASSWORD, TYPE_EXPIRATION, TYPE_DISPLAYNAME, TYPE_DESCRIPTION, TYPE_NOTIFYUPLOADS,
        TYPE_NOTIFY_UPLOADS_EXTRA_RECIPIENTS.

        :param role: Role to assign to the grantee, VIEWER or EDITOR (REQUIRED)
        :param type: Type of update (REQUIRED).
        :param password: Password to access the share.
        :param expiration: Expiration timestamp for the share.
        :param display_name: Display name for the share.
        :param description: Description for the share.
        :param notify_uploads: Notify uploads flag.
        :param notify_uploads_extra_recipients: List of extra recipients to notify on upload.
        :return: PublicShare object.
        :raises: ValueError (Invalid update type or missing values)
        """
        # Check if required parameters are provided
        if not role or not type:
            raise ValueError("role and type are required")

        # Translate type to enum value (will throw ValueError if invalid type)
        update_type = cs3slapi.UpdatePublicShareRequest.Update.Type.Value(type)

        # Create grant object
        grant = cs3slr.Grant(
            permissions=cs3slr.PublicSharePermissions(permissions=Share._create_permissions(role)),
            password=password,
            expiration=expiration,
        )
        return cs3slapi.UpdatePublicShareRequest.Update(
            grant=grant,
            type=update_type,
            display_name=display_name,
            description=description,
            notify_uploads=notify_uploads,
            notify_uploads_extra_recipients=notify_uploads_extra_recipients,
        )

    @classmethod
    def _create_share_grant(
        cls, opaque_id: str, idp: str, role: str, grantee_type: str, expiration: Optional[cs3types.Timestamp] = None
    ) -> cs3scr.ShareGrant:
        """
        Create a share grant object.

        :param opaque_id: Opaque group/user id.
        :param idp: Identity provider.
        :param role: Role to assign to the grantee, VIEWER or EDITOR.
        :param grantee_type: Type of grantee, USER or GROUP.
        :return: ShareGrant object.
        :raises: ValueError (Invalid grantee type)
        """

        grantee = None
        if grantee_type == "USER":
            type = cs3spr.GRANTEE_TYPE_USER
            user_id = cs3iur.UserId(idp=idp, opaque_id=opaque_id)
            grantee = cs3spr.Grantee(type=type, user_id=user_id)
        elif grantee_type == "GROUP":
            type = cs3spr.GRANTEE_TYPE_GROUP
            id = cs3igr.GroupId(idp=idp, opaque_id=opaque_id)
            grantee = cs3spr.Grantee(type=type, group_id=id)
        else:
            raise ValueError("Invalid grantee type")
        permissions = cs3scr.SharePermissions(permissions=Share._create_permissions(role))
        return cs3scr.ShareGrant(permissions=permissions, grantee=grantee, expiration=expiration)

    @classmethod
    def _create_permissions(cls, role) -> cs3spr.ResourcePermissions:
        """
        Create a share permissions object.

        :param role: Role to assign to the grantee, VIEWER or EDITOR.
        :return: ResourcePermissions object.
        :raises: ValueError (Invalid role)
        """
        if role == "VIEWER":
            return cs3spr.ResourcePermissions(
                get_path=True,
                get_quota=True,
                initiate_file_download=True,
                list_file_versions=True,
                list_grants=True,
                list_container=True,
                list_recycle=True,
                stat=True,
                create_container=False,
                delete=False,
                initiate_file_upload=False,
                restore_file_version=False,
                move=False,
            )
        elif role == "EDITOR":
            return cs3spr.ResourcePermissions(
                get_path=True,
                get_quota=True,
                initiate_file_download=True,
                list_file_versions=True,
                list_grants=True,
                list_container=True,
                list_recycle=True,
                stat=True,
                create_container=True,
                delete=True,
                initiate_file_upload=True,
                restore_file_version=True,
                move=True,
            )
        else:
            raise ValueError("Invalid role")

    @classmethod
    def create_public_share_filter(
        cls,
        filter_type: str,
        resource_id: cs3spr.ResourceId = None,
        owner_idp: Optional[str] = None,
        owner_opaque_id: Optional[str] = None,
        creator_idp: Optional[str] = None,
        creator_opaque_id: Optional[str] = None,
    ) -> cs3slapi.ListPublicSharesRequest.Filter:
        """
        Create a public share filter object, based on the filter type (can be TYPE_RESOURCE_ID, TYPE_OWNER,
        TYPE_CREATOR). The corresponding parameters must be provided, e.g. if the filter_type is TYPE_RESOURCE_ID,
        the resource parameter must be provided, and so on.

        :param resource: resource_id.
        :param owner_idp: Identity provider of the owner.
        :param owner_opaque_id: Opaque id of the owner.
        :param creator_idp: Identity provider of the creator.
        :param creator_opaque_id: Opaque id of the creator.
        :param filter_type: Filter type.
        :return: Filter object (Success)
        :raises: ValueError (Invalid filter type or missing parameters)
        """
        # Convert the filter_type string to enum value (will throw ValueError if invalid type)
        filter_type = cs3slapi.ListPublicSharesRequest.Filter.Type.Value(filter_type)

        # Set the appropriate term based on the filter type
        if filter_type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_RESOURCE_ID and resource_id:
            return cs3slapi.ListPublicSharesRequest.Filter(type=filter_type, resource_id=resource_id)
        elif filter_type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_OWNER and owner_idp and owner_opaque_id:
            return cs3slapi.ListPublicSharesRequest.Filter(
                type=filter_type, owner=cs3iur.UserId(idp=owner_idp, opaque_id=owner_opaque_id)
            )
        elif (
            filter_type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_CREATOR
            and creator_idp
            and creator_opaque_id
        ):
            return cs3slapi.ListPublicSharesRequest.Filter(
                type=filter_type, creator=cs3iur.UserId(idp=creator_idp, opaque_id=creator_opaque_id)
            )
        else:
            raise ValueError("Invalid filter type or missing parameters")

    @classmethod
    def create_share_filter(
        cls,
        filter_type: str,
        resource_id: cs3spr.ResourceId = None,
        owner_idp: Optional[str] = None,
        owner_opaque_id: Optional[str] = None,
        creator_idp: Optional[str] = None,
        creator_opaque_id: Optional[str] = None,
        grantee_type: Optional[str] = None,
        space_id: Optional[str] = None,
        share_state: Optional[str] = None,
    ) -> cs3scr.Filter:
        """
        Create a share filter object, based on the filter type (can be TYPE_RESOURCE_ID, TYPE_OWNER, TYPE_CREATOR,
        TYPE_GRANTEE_TYPE, TYPE_SPACE_ID, TYPE_STATE). The corresponding parameters must be provided, e.g. if the
        filter_type is TYPE_RESOURCE_ID, the resource parameter must be provided, and so on.

        :param filter_type: Filter type (REQUIRED).
        :param resource: Resource object to filter by.
        :param owner_idp: Identity provider of the owner.
        :param owner_opaque_id: Opaque id of the owner.
        :param creator_idp: Identity provider of the creator.
        :param creator_opaque_id: Opaque id of the creator.
        :param grantee_type: Type of grantee, USER or GROUP.
        :param space_id: Space id.
        :param share_state: Share state (SHARE_STATE_ACCEPTED, SHARE_STATE_ACCEPTED, SHARE_STATE_REJECTED).
        :return: Filter object (Success)
        :raises: ValueError (Invalid filter type or missing parameters)
        """

        # Convert the filter_type string to enum value
        filter_type = cs3scr.Filter.Type.Value(filter_type)

        # Set the appropriate term based on the filter type
        if filter_type == cs3scr.Filter.Type.TYPE_RESOURCE_ID and resource_id:
            return cs3scr.Filter(type=filter_type, resource_id=resource_id)
        elif filter_type == cs3scr.Filter.Type.TYPE_OWNER and owner_idp and owner_opaque_id:
            return cs3scr.Filter(type=filter_type, owner=cs3iur.UserId(idp=owner_idp, opaque_id=owner_opaque_id))
        elif filter_type == cs3scr.Filter.Type.TYPE_CREATOR and creator_idp and creator_opaque_id:
            return cs3scr.Filter(type=filter_type, creator=cs3iur.UserId(idp=creator_idp, opaque_id=creator_opaque_id))
        elif filter_type == cs3scr.Filter.Type.TYPE_GRANTEE_TYPE and grantee_type:
            return cs3scr.Filter(type=filter_type, grantee_type=grantee_type)
        elif filter_type == cs3scr.Filter.Type.TYPE_SPACE_ID and space_id:
            return cs3scr.Filter(type=filter_type, space_id=space_id)
        elif filter_type == cs3scr.Filter.Type.TYPE_STATE and share_state:
            return cs3scr.Filter(type=filter_type, state=cs3scr.ShareState.Value(share_state))
        else:
            raise ValueError("Invalid filter type or missing parameters")

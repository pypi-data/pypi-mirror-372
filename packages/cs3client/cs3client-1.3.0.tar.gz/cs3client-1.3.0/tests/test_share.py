"""
test_share.py

Tests that the Share class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 28/08/2024
"""

import pytest
from unittest.mock import Mock, patch
import cs3.sharing.collaboration.v1beta1.resources_pb2 as cs3scr
import cs3.sharing.link.v1beta1.link_api_pb2 as cs3slapi
import cs3.storage.provider.v1beta1.resources_pb2 as cs3spr
import cs3.rpc.v1beta1.code_pb2 as cs3code

from cs3client.exceptions import (
    AuthenticationException,
    NotFoundException,
    UnknownException,
    FileLockedException,
    AlreadyExistsException,
)
from .fixtures import (  # noqa: F401 (they are used, the framework is not detecting it)
    mock_config,
    mock_logger,
    mock_gateway,
    share_instance,
    mock_status_code_handler,
)

# Test cases for the Share class.


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (cs3code.CODE_FAILED_PRECONDITION, "File is locked", FileLockedException, None),
        (cs3code.CODE_ABORTED, "File is locked", FileLockedException, None),
        (cs3code.CODE_ALREADY_EXISTS, "Share already exists", AlreadyExistsException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_create_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    opaque_id = "opaque_id"
    idp = "idp"
    role = "VIEWER"
    resource_info = cs3spr.ResourceInfo(id=cs3spr.ResourceId(storage_id="storage_id", opaque_id="opaque_id"))
    grantee_type = "USER"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "CreateShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.create_share(
                    auth_token,
                    resource_info=resource_info,
                    opaque_id=opaque_id,
                    idp=idp,
                    role=role,
                    grantee_type=grantee_type
                )
        else:
            result = share_instance.create_share(
                auth_token,
                resource_info=resource_info,
                opaque_id=opaque_id,
                idp=idp,
                role=role,
                grantee_type=grantee_type
            )
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, (["share1", "share2"], "token")),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_list_existing_shares(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share_infos = expected_result[0]
        mock_response.next_page_token = expected_result[1]
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "ListExistingShares", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.list_existing_shares(auth_token)
        else:
            result = share_instance.list_existing_shares(auth_token)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_get_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    share_id = "share_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "GetShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.get_share(auth_token, share_id)
        else:
            result = share_instance.get_share(auth_token, share_id)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_remove_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    share_id = "share_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "RemoveShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.remove_share(auth_token, share_id)
        else:
            result = share_instance.remove_share(auth_token, share_id)
            assert result is None


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (cs3code.CODE_ALREADY_EXISTS, "Share already exists", AlreadyExistsException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_update_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    opaque_id = "share_id"
    role = "VIEWER"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "UpdateShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.update_share(auth_token, role=role, opaque_id=opaque_id)
        else:
            result = share_instance.update_share(auth_token, role=role, opaque_id=opaque_id)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, (["share1", "share2"], "token")),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_list_existing_received_shares(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share_infos = expected_result[0]
        mock_response.next_page_token = expected_result[1]
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "ListExistingReceivedShares", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.list_received_existing_shares(auth_token)
        else:
            result = share_instance.list_received_existing_shares(auth_token)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_get_received_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    share_id = "share_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "GetReceivedShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.get_received_share(auth_token, share_id)
        else:
            result = share_instance.get_received_share(auth_token, share_id)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_update_received_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    resource_id = cs3spr.ResourceId(storage_id="storage_id", opaque_id="opaque_id")
    share = cs3scr.Share(resource_id=resource_id)
    received_share = cs3scr.ReceivedShare(share=share)

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "UpdateReceivedShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.update_received_share(auth_token, received_share=received_share)
        else:
            result = share_instance.update_received_share(auth_token, received_share=received_share)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (cs3code.CODE_FAILED_PRECONDITION, "File is locked", FileLockedException, None),
        (cs3code.CODE_ABORTED, "File is locked", FileLockedException, None),
        (cs3code.CODE_ALREADY_EXISTS, "Share already exists", AlreadyExistsException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_create_public_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    resource_info = cs3spr.ResourceInfo(id=cs3spr.ResourceId(storage_id="storage_id", opaque_id="opaque_id"))
    role = "EDITOR"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "CreatePublicShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.create_public_share(auth_token, resource_info=resource_info, role=role)
        else:
            result = share_instance.create_public_share(auth_token, resource_info=resource_info, role=role)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, (["share1", "share2"], "token")),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def list_existing_public_shares(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share_infos = expected_result[0]
        mock_response.next_page_token = expected_result[1]
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "ListExistingPublicShares", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.list_existing_public_shares(auth_token)
        else:
            result = share_instance.list_existing_public_shares(auth_token)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_get_public_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    share_id = "share_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "GetPublicShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.get_public_share(auth_token, share_id)
        else:
            result = share_instance.get_public_share(auth_token, share_id)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_update_public_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    type = "TYPE_PERMISSIONS"
    role = "EDITOR"
    opqaue_id = "opaque_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "UpdatePublicShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.update_public_share(auth_token, type=type, role=role, opaque_id=opqaue_id)
        else:
            result = share_instance.update_public_share(auth_token, type=type, role=role, opaque_id=opqaue_id)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "share", None, "share"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (cs3code.CODE_FAILED_PRECONDITION, "File is locked", FileLockedException, None),
        (cs3code.CODE_ABORTED, "File is locked", FileLockedException, None),
        (cs3code.CODE_ALREADY_EXISTS, "Share already exists", AlreadyExistsException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_remove_public_share(
    share_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    share_id = "share_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    if status_code == cs3code.CODE_OK:
        mock_response.share = expected_result
    auth_token = ('x-access-token', "some_token")

    with patch.object(share_instance._gateway, "RemovePublicShare", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                share_instance.remove_public_share(auth_token, share_id)
        else:
            result = share_instance.remove_public_share(auth_token, share_id)
            assert result is None


def test_create_public_share_filter_resource_id(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_RESOURCE_ID"
    resource_id = cs3spr.ResourceId(storage_id="storage_id", opaque_id="opaque_id")

    # Call the method
    result = share_instance.create_public_share_filter(filter_type=filter_type, resource_id=resource_id)

    # Assertions
    assert result.type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_RESOURCE_ID
    assert result.resource_id == resource_id


def test_create_public_share_filter_owner(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_OWNER"
    owner_idp = "owner_idp"
    owner_opaque_id = "owner_opaque_id"

    # Call the method
    result = share_instance.create_public_share_filter(
        filter_type=filter_type, owner_idp=owner_idp, owner_opaque_id=owner_opaque_id
    )

    # Assertions
    assert result.type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_OWNER
    assert result.owner.idp == owner_idp
    assert result.owner.opaque_id == owner_opaque_id


def test_create_public_share_filter_creator(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_CREATOR"
    creator_idp = "creator_idp"
    creator_opaque_id = "creator_opaque_id"

    # Call the method
    result = share_instance.create_public_share_filter(
        filter_type=filter_type, creator_idp=creator_idp, creator_opaque_id=creator_opaque_id
    )

    # Assertions
    assert result.type == cs3slapi.ListPublicSharesRequest.Filter.Type.TYPE_CREATOR
    assert result.creator.idp == creator_idp
    assert result.creator.opaque_id == creator_opaque_id


def test_create_public_share_filter_invalid_resource_id(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_RESOURCE_ID"

    # This should raise ValueError due to missing resource_id
    with pytest.raises(ValueError):
        share_instance.create_public_share_filter(filter_type=filter_type)


def test_create_public_share_filter_invalid_owner(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_OWNER"

    # This should raise ValueError due to missing owner_idp and owner_opaque_id
    with pytest.raises(ValueError):
        share_instance.create_public_share_filter(filter_type=filter_type)


def test_create_public_share_filter_invalid_creator(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_CREATOR"

    # This should raise ValueError due to missing creator_idp and creator_opaque_id
    with pytest.raises(ValueError):
        share_instance.create_public_share_filter(filter_type=filter_type)


def test_create_public_share_filter_invalid_type(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "INVALID_TYPE"

    # This should raise ValueError due to invalid filter_type
    with pytest.raises(ValueError):
        share_instance.create_public_share_filter(filter_type=filter_type)


# Test when filtering by resource ID
def test_create_share_filter_resource_id(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_RESOURCE_ID"
    resource_id = cs3spr.ResourceId(storage_id="storage_id", opaque_id="opaque_id")

    # Call the method
    result = share_instance.create_share_filter(filter_type=filter_type, resource_id=resource_id)

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_RESOURCE_ID
    assert result.resource_id == resource_id


# Test when filtering by owner
def test_create_share_filter_owner(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_OWNER"
    owner_idp = "example_idp"
    owner_opaque_id = "owner_opaque_id"

    # Call the method
    result = share_instance.create_share_filter(
        filter_type=filter_type, owner_idp=owner_idp, owner_opaque_id=owner_opaque_id
    )

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_OWNER
    assert result.owner.idp == owner_idp
    assert result.owner.opaque_id == owner_opaque_id


# Test when filtering by creator
def test_create_share_filter_creator(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_CREATOR"
    creator_idp = "creator_idp"
    creator_opaque_id = "creator_opaque_id"

    # Call the method
    result = share_instance.create_share_filter(
        filter_type=filter_type, creator_idp=creator_idp, creator_opaque_id=creator_opaque_id
    )

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_CREATOR
    assert result.creator.idp == creator_idp
    assert result.creator.opaque_id == creator_opaque_id


# Test when filtering by grantee type
def test_create_share_filter_grantee_type(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_GRANTEE_TYPE"
    grantee_type = cs3spr.GranteeType.GRANTEE_TYPE_USER

    # Call the method
    result = share_instance.create_share_filter(filter_type=filter_type, grantee_type=grantee_type)

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_GRANTEE_TYPE
    assert result.grantee_type == grantee_type


# Test when filtering by space ID
def test_create_share_filter_space_id(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_SPACE_ID"
    space_id = "space_id"

    # Call the method
    result = share_instance.create_share_filter(filter_type=filter_type, space_id=space_id)

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_SPACE_ID
    assert result.space_id == space_id


# Test when filtering by share state
def test_create_share_filter_state(share_instance):  # noqa: F811 (not a redefinition)
    # Setup inputs
    filter_type = "TYPE_STATE"
    share_state = "SHARE_STATE_ACCEPTED"  # Example state string

    # Call the method
    result = share_instance.create_share_filter(filter_type=filter_type, share_state=share_state)

    # Assertions
    assert result.type == cs3scr.Filter.Type.TYPE_STATE
    assert result.state == cs3scr.ShareState.Value(share_state)


# Test for invalid filter type or missing parameters
def test_create_share_filter_invalid(share_instance):  # noqa: F811 (not a redefinition)
    # Setup invalid inputs
    filter_type = "INVALID_TYPE"

    # Call the method and check for ValueError
    with pytest.raises(ValueError):
        share_instance.create_share_filter(filter_type=filter_type)

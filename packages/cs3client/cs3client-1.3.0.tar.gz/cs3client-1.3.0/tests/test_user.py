"""
test_user.py

Tests that the User class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 28/08/2024
"""

import pytest
from unittest.mock import Mock, patch
import cs3.rpc.v1beta1.code_pb2 as cs3code

from cs3client.exceptions import (
    AuthenticationException,
    NotFoundException,
    UnknownException,
)
from .fixtures import (  # noqa: F401 (they are used, the framework is not detecting it)
    mock_config,
    mock_logger,
    mock_gateway,
    user_instance,
    mock_status_code_handler,
)

# Test cases for the User class


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, user_data",
    [
        (cs3code.CODE_OK, None, None, Mock(idp="idp", opaque_id="opaque_id")),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (-2, "error", UnknownException, None),
    ],
)
def test_get_user(
    user_instance, status_code, status_message, expected_exception, user_data  # noqa: F811 (not a redefinition)
):
    idp = "idp"
    opaque_id = "opaque_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.user = user_data

    with patch.object(user_instance._gateway, "GetUser", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                user_instance.get_user(idp, opaque_id)
        else:
            result = user_instance.get_user(idp, opaque_id)
            assert result == user_data


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, user_data",
    [
        (cs3code.CODE_OK, None, None, Mock(idp="idp", opaque_id="opaque_id")),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (-2, "error", UnknownException, None),
    ],
)
def test_get_user_by_claim(
    user_instance, status_code, status_message, expected_exception, user_data  # noqa: F811 (not a redefinition)
):
    claim = "claim"
    value = "value"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.user = user_data

    with patch.object(user_instance._gateway, "GetUserByClaim", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                user_instance.get_user_by_claim(claim, value)
        else:
            result = user_instance.get_user_by_claim(claim, value)
            assert result == user_data


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, groups",
    [
        (cs3code.CODE_OK, None, None, ["group1", "group2"]),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (-2, "error", UnknownException, None),
    ],
)
def test_get_user_groups(
    user_instance, status_code, status_message, expected_exception, groups  # noqa: F811 (not a redefinition)
):
    idp = "idp"
    opaque_id = "opaque_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.groups = groups

    with patch.object(user_instance._gateway, "GetUserGroups", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                user_instance.get_user_groups(idp, opaque_id)
        else:
            result = user_instance.get_user_groups(idp, opaque_id)
            assert result == groups


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, users",
    [
        (cs3code.CODE_OK, None, None, [Mock(), Mock()]),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "error", AuthenticationException, None),
        (-2, "error", UnknownException, None),
    ],
)
def test_find_users(
    user_instance, status_code, status_message, expected_exception, users  # noqa: F811 (not a redefinition)
):
    filter = "filter"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.users = users
    auth_token = ('x-access-token', "some_token")

    with patch.object(user_instance._gateway, "FindUsers", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                user_instance.find_users(auth_token, filter)
        else:
            result = user_instance.find_users(auth_token, filter)
            assert result == users

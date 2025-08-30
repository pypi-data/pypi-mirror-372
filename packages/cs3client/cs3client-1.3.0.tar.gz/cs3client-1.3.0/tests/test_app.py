"""
test_app.py

Tests that the App class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import cs3.rpc.v1beta1.code_pb2 as cs3code
from unittest.mock import Mock, patch
import pytest

from cs3client.exceptions import (
    AuthenticationException,
    NotFoundException,
    UnknownException,
)
from cs3client.cs3resource import Resource
from .fixtures import (  # noqa: F401 (they are used, the framework is not detecting it)
    mock_config,
    mock_logger,
    mock_gateway,
    app_instance,
    mock_status_code_handler,
)

# Test cases for the App class


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, providers",
    [
        (cs3code.CODE_OK, None, None, ["provider1", "provider2"]),
        (cs3code.CODE_UNAUTHENTICATED, "error", AuthenticationException, None),
        (cs3code.CODE_INTERNAL, "error", UnknownException, None),
    ],
)
def test_list_app_providers(
    app_instance, status_code, status_message, expected_exception, providers  # noqa: F811 (not a redefinition)
):
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.providers = providers
    auth_token = ('x-access-token', "some_token")

    with patch.object(app_instance._gateway, "ListAppProviders", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                app_instance.list_app_providers(auth_token)
        else:
            result = app_instance.list_app_providers(auth_token)
            assert result == providers


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, open_in_app_url",
    [
        (cs3code.CODE_OK, None, None, "url"),
        (cs3code.CODE_UNAUTHENTICATED, "error", AuthenticationException, None),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (cs3code.CODE_INTERNAL, "error", UnknownException, None),
    ],
)
def test_open_in_app(
    app_instance, status_code, status_message, expected_exception, open_in_app_url  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    view_mode = "VIEW_MODE_VIEW_ONLY"
    app = "app"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.OpenInAppURL = open_in_app_url
    auth_token = ('x-access-token', "some_token")

    with patch.object(app_instance._gateway, "OpenInApp", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                app_instance.open_in_app(auth_token, resource, view_mode, app)
        else:
            result = app_instance.open_in_app(auth_token, resource, view_mode, app)
            assert result == open_in_app_url

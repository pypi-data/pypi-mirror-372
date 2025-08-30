"""
test_checkpoint.py

Tests that the App class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

from unittest.mock import Mock, patch
import pytest
import cs3.rpc.v1beta1.code_pb2 as cs3code

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
    checkpoint_instance,
    mock_status_code_handler,
)

# Test cases for the Checkpoint class


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, versions",
    [
        (cs3code.CODE_OK, None, None, [Mock(), Mock()]),
        (cs3code.CODE_UNAUTHENTICATED, "error", AuthenticationException, None),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException, None),
        (-2, "error", UnknownException, None),
    ],
)
def test_list_file_versions(
    checkpoint_instance, status_code, status_message, expected_exception, versions  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    page_token = "page_token"
    page_size = 10

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.versions = versions
    auth_token = ('x-access-token', "some_token")

    with patch.object(checkpoint_instance._gateway, "ListFileVersions", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                checkpoint_instance.list_file_versions(auth_token, resource, page_token, page_size)
        else:
            result = checkpoint_instance.list_file_versions(auth_token, resource, page_token, page_size)
            assert result == versions


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_UNAUTHENTICATED, "error", AuthenticationException),
        (cs3code.CODE_NOT_FOUND, "error", NotFoundException),
        (-2, "error", UnknownException),
    ],
)
def test_restore_file_version(
    checkpoint_instance, status_code, status_message, expected_exception  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    version_key = "version_key"
    lock_id = "lock_id"

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(checkpoint_instance._gateway, "RestoreFileVersion", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                checkpoint_instance.restore_file_version(auth_token, resource, version_key, lock_id)
        else:
            result = checkpoint_instance.restore_file_version(auth_token, resource, version_key, lock_id)
            assert result is None

"""
test_file.py

Tests that the File class methods work as expected.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import pytest
from unittest.mock import Mock, patch
import cs3.rpc.v1beta1.code_pb2 as cs3code

from cs3client.cs3resource import Resource
from cs3client.exceptions import (
    AuthenticationException,
    NotFoundException,
    FileLockedException,
    UnknownException,
)
from .fixtures import (  # noqa: F401 (they are used, the framework is not detecting it)
    mock_config,
    mock_logger,
    mock_gateway,
    file_instance,
    mock_status_code_handler,
)

# Test cases for the file class.


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, expected_result",
    [
        (cs3code.CODE_OK, "resource_info", None, "resource_info"),
        (cs3code.CODE_NOT_FOUND, "Resource not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication failed", AuthenticationException, None),
        (-1, "Internal error", UnknownException, None),
    ],
)
def test_stat(
    file_instance, status_code, status_message, expected_exception, expected_result  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")
    if status_code == cs3code.CODE_OK:
        mock_response.info = status_message

    with patch.object(file_instance._gateway, "Stat", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.stat(auth_token, resource)
        else:
            result = file_instance.stat(auth_token, resource)
            assert result == expected_result


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException),
        (cs3code.CODE_ABORTED, "Failed precondition", FileLockedException),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException),
    ],
)
def test_set_xattr(file_instance, status_code, status_message, expected_exception):  # noqa: F811 (not a redefinition)
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    key = "testkey"
    value = "testvalue"
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "SetArbitraryMetadata", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.set_xattr(auth_token, resource, key, value)
        else:
            file_instance.set_xattr(auth_token, resource, key, value)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException),
        (cs3code.CODE_ABORTED, "Failed aborted", FileLockedException),
        (cs3code.CODE_UNAUTHENTICATED, "Authentication Failed", AuthenticationException),
        (-1, "Failed aborted", UnknownException),
    ],
)
def test_remove_xattr(
    file_instance, status_code, status_message, expected_exception  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    key = "testkey"
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "UnsetArbitraryMetadata", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.remove_xattr(auth_token, resource, key)
        else:
            file_instance.remove_xattr(auth_token, resource, key)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException),
        (cs3code.CODE_ABORTED, "Failed aborted", FileLockedException),
        (cs3code.CODE_NOT_FOUND, "Failed not found", NotFoundException),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException),
        (-1, "unknown error", UnknownException),
    ],
)
def test_rename_file(file_instance, status_code, status_message, expected_exception):  # noqa: F811 (not a redefinition)
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    newresource = Resource.from_file_ref_and_endpoint(endpoint="", file="newtestfile")
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "Move", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.rename_file(auth_token, resource, newresource)
        else:
            file_instance.rename_file(auth_token, resource, newresource)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_NOT_FOUND, "path not found", IOError),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException),
        (-1, "Unknown error", UnknownException),
    ],
)
def test_remove_file(file_instance, status_code, status_message, expected_exception):  # noqa: F811 (not a redefinition)
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "Delete", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.remove_file(auth_token, resource)
        else:
            file_instance.remove_file(auth_token, resource)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException),
        (-1, "Unknown error", UnknownException),
    ],
)
def test_touch_file(file_instance, status_code, status_message, expected_exception):  # noqa: F811 (not a redefinition)
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "TouchFile", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.touch_file(auth_token, resource)
        else:
            file_instance.touch_file(auth_token, resource)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, put_response_status",
    [
        (cs3code.CODE_OK, None, None, 200),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException, None),
        (-1, "Unknown error", UnknownException, None),
    ],
)
def test_write_file(
    file_instance,  # noqa: F811 (not a redefinition)
    status_code,
    status_message,
    expected_exception,
    put_response_status,
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")
    content = "testcontent"
    size = len(content)

    mock_upload_response = Mock()
    mock_upload_response.status.code = status_code
    mock_upload_response.status.message = status_message
    mock_upload_response.protocols = [Mock(protocol="simple", upload_endpoint="http://example.com", token="token")]
    auth_token = ('x-access-token', "some_token")

    mock_put_response = Mock()
    mock_put_response.status_code = put_response_status

    with patch.object(file_instance._gateway, "InitiateFileUpload", return_value=mock_upload_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.write_file(auth_token, resource, content, size)
        else:
            with patch("requests.put", return_value=mock_put_response):
                file_instance.write_file(auth_token, resource, content, size)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception",
    [
        (cs3code.CODE_OK, None, None),
        (cs3code.CODE_FAILED_PRECONDITION, "Failed precondition", FileLockedException),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException),
        (-1, "Unknown error", UnknownException),
    ],
)
def test_make_dir(file_instance, status_code, status_message, expected_exception):  # noqa: F811 (not a redefinition)
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testdir")
    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "CreateContainer", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                file_instance.make_dir(auth_token, resource)
        else:
            file_instance.make_dir(auth_token, resource)


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, infos",
    [
        (cs3code.CODE_OK, None, None, ["file1", "file2"]),
        (cs3code.CODE_NOT_FOUND, "Failed precondition", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException, None),
        (-1, "Unknown error", UnknownException, None),
    ],
)
def test_list_dir(
    file_instance, status_code, status_message, expected_exception, infos  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testdir")

    mock_response = Mock()
    mock_response.status.code = status_code
    mock_response.status.message = status_message
    mock_response.infos = infos
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "ListContainer", return_value=mock_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                res = file_instance.list_dir(auth_token, resource)
                # Lazy evaluation
                first_item = next(res, None)
                if first_item is not None:
                    for _ in res:
                        pass
        else:
            res = file_instance.list_dir(auth_token, resource)
            # Lazy evaluation
            first_item = next(res, None)
            assert first_item == "file1"
            for _ in res:
                pass


@pytest.mark.parametrize(
    "status_code, status_message, expected_exception, iter_content",
    [
        (cs3code.CODE_OK, None, None, [b"chunk1", b"chunk2"]),
        (cs3code.CODE_NOT_FOUND, "File not found", NotFoundException, None),
        (cs3code.CODE_UNAUTHENTICATED, "Failed to authenticate", AuthenticationException, None),
        (-1, "Unknown error", UnknownException, None),
    ],
)
def test_read_file(
    file_instance, status_code, status_message, expected_exception, iter_content  # noqa: F811 (not a redefinition)
):
    resource = Resource.from_file_ref_and_endpoint(endpoint="", file="testfile")

    mock_download_response = Mock()
    mock_download_response.status.code = status_code
    mock_download_response.status.message = status_message
    mock_download_response.protocols = [Mock(protocol="simple", download_endpoint="http://example.com", token="token")]

    mock_fileget_response = Mock()
    mock_fileget_response.status_code = 200
    mock_fileget_response.iter_content = Mock(return_value=iter_content)
    auth_token = ('x-access-token', "some_token")

    with patch.object(file_instance._gateway, "InitiateFileDownload", return_value=mock_download_response):
        if expected_exception:
            with pytest.raises(expected_exception):
                res = file_instance.read_file(auth_token, resource)
                # Lazy evaluation
                first_item = next(res, None)
                if first_item is not None:
                    for _ in res:
                        pass
        else:
            with patch("requests.get", return_value=mock_fileget_response):
                res = file_instance.read_file(auth_token, resource)
                # Lazy evaluation
                chunks = list(res)
                assert chunks == iter_content

"""
test_cs3client.py

Tests the initialization of the CS3Client class.

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

from .fixtures import (  # noqa: F401, E402 (they are used, the framework is not detecting it)
    cs3_client_insecure,
    cs3_client_secure,
    mock_config,
    mock_logger,
    mock_gateway,
    create_mock_jwt,
)

# Test cases for the cs3client class.


def test_cs3client_initialization_secure(cs3_client_secure):  # noqa: F811 (not a redefinition)
    client = cs3_client_secure

    # Make sure configuration is correctly set
    assert client._config.host == "test_host:port"
    assert client._config.grpc_timeout == 10
    assert client._config.http_timeout == 10
    assert client._config.chunk_size == 4194304
    assert client._config.auth_login_type == "basic"
    assert client._config.auth_client_id == "einstein"
    assert client._config.tus_enabled is False
    assert client._config.ssl_enabled is True
    assert client._config.ssl_verify is True
    assert client._config.ssl_client_cert == "test_client_cert"
    assert client._config.ssl_client_key == "test_client_key"
    assert client._config.ssl_ca_cert == "test_ca_cert"
    assert client._config.lock_by_setting_attr is False
    assert client._config.lock_not_impl is False
    assert client._config.lock_expiration == 1800

    # Make sure the gRPC channel is correctly created
    assert client.channel is not None
    assert client._gateway is not None
    assert client.file is not None

    # Make sure file objects are correctly set
    assert client.file._gateway is not None
    assert client.file._config is not None
    assert client.file._log is not None


def test_cs3client_initialization_insecure(cs3_client_insecure):  # noqa: F811 (not a redefinition)
    client = cs3_client_insecure

    # Make sure configuration is correctly set
    assert client._config.host == "test_host:port"
    assert client._config.grpc_timeout == 10
    assert client._config.http_timeout == 10
    assert client._config.chunk_size == 4194304
    assert client._config.auth_login_type == "basic"
    assert client._config.auth_client_id == "einstein"
    assert client._config.tus_enabled is False
    assert client._config.ssl_enabled is False
    assert client._config.ssl_verify is True
    assert client._config.ssl_client_cert == "test_client_cert"
    assert client._config.ssl_client_key == "test_client_key"
    assert client._config.ssl_ca_cert == "test_ca_cert"
    assert client._config.lock_by_setting_attr is False
    assert client._config.lock_not_impl is False
    assert client._config.lock_expiration == 1800

    # Make sure the gRPC channel is correctly created
    assert client.channel is not None
    assert client._gateway is not None
    assert client.file is not None

    # Make sure file objects are correctly set
    assert client.file._gateway is not None
    assert client.file._config is not None
    assert client.file._log is not None

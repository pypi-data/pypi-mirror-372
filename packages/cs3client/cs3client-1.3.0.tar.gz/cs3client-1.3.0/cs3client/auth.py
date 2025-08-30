"""
auth.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import grpc
import jwt
import datetime
import logging
from typing import Union
from cs3.gateway.v1beta1.gateway_api_pb2 import AuthenticateRequest
from cs3.auth.registry.v1beta1.registry_api_pb2 import ListAuthProvidersRequest
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub
from cs3.rpc.v1beta1.code_pb2 import CODE_OK

from .cs3client import CS3Client
from .exceptions import AuthenticationException, SecretNotSetException
from .config import Config


class Auth:
    """
    Auth class to handle authentication and token validation with CS3 Gateway API.
    """

    def __init__(self, cs3_client: CS3Client) -> None:
        """
        Initializes the Auth class with configuration, logger, and gateway stub,
        NOTE that token OR the client secret has to be set when instantiating the auth object.

        :param config: Config object containing the configuration parameters.
        :param log: Logger instance for logging.
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway.
        """
        self._gateway: GatewayAPIStub = cs3_client._gateway
        self._log: logging.Logger = cs3_client._log
        self._config: Config = cs3_client._config
        # The user should be able to change the client secret (e.g. token) and client id at runtime
        self._client_secret: Union[str, None] = self._config.auth_client_secret
        self._client_id: Union[str, None] = self._config.auth_client_id
        self._token: Union[str, None] = None

    def set_client_secret(self, token: str) -> None:
        """
        Sets the client secret, exists so that the user can change the client secret (e.g. token, password) at runtime,
        without having to create a new Auth object. Note client secret has to be set when
        instantiating the client object or through the configuration.

        :param token: Auth token/password.
        """
        self._client_secret = token

    def set_client_id(self, id: str) -> None:
        """
        Sets the client id, exists so that the user can change the client id at runtime, without having to create
        a new Auth object. Settings this (either through config or here) is optional unless you are using
        basic authentication.

        :param token: id.
        """
        self._client_id = id

    def get_token(self) -> tuple[str, str]:
        """
        Attempts to get a valid authentication token. If the token is not valid, a new token is requested
        if the client secret is set, if only the token is set then an exception will be thrown stating that
        the credentials have expired.

        :return tuple: A tuple containing the header key and the token.
        :raises: AuthenticationException (token expired, or failed to authenticate)
        :raises: SecretNotSetException (neither token or client secret was set)
        """

        if not self._client_secret:
            self._log.error("Attempted to authenticate, client secret was not set")
            raise SecretNotSetException("The client secret (e.g. token, passowrd) is not set")

        try:
            self.check_token(self._token)
        except AuthenticationException:
            # Token has expired or has not been set, obtain another one.
            req = AuthenticateRequest(
                type=self._config.auth_login_type,
                client_id=self._client_id,
                client_secret=self._client_secret,
            )
            # Send the authentication request to the CS3 Gateway
            res = self._gateway.Authenticate(req)

            if res.status.code != CODE_OK:
                self._log.error(f'msg="Failed to authenticate" '
                                f'user="{self._client_id if self._client_id else "no_id_set"}" '
                                f'error_code="{res.status}"')
                raise AuthenticationException(
                    f'Failed to authenticate: user="{self._client_id if self._client_id else "no_id_set"}" '
                    f'error_code="{res.status}"'
                )
            self._token = res.token
        self._log.debug(f'msg="Authenticated user" user="{self._client_id if self._client_id else "no_id_set"}"')
        return ("x-access-token", self._token)

    def list_auth_providers(self) -> list[str]:
        """
        list authentication providers

        :return: a list of the supported authentication types
        :raises: ConnectionError (Could not connect to host)
        """
        try:
            res = self._gateway.ListAuthProviders(request=ListAuthProvidersRequest())
            if res.status.code != CODE_OK:
                self._log.error(f'msg="List auth providers request failed" error_code="{res.status}"')
                raise Exception(res.status.message)
        except grpc.RpcError as e:
            self._log.error("List auth providers request failed")
            raise ConnectionError(e)
        return res.types

    @classmethod
    def check_token(cls, token: str) -> tuple:
        """
        Checks if the given token is set and valid.

        :param token: JWT token as a string.
        :return tuple: A tuple containing the header key and the token.
        :raises: ValueError (Token missing)
        :raises: AuthenticationException (Token is expired)
        """
        if not token:
            raise AuthenticationException("Token not set")
        # Decode the token without verifying the signature
        decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={"verify_signature": False})
        now = datetime.datetime.now().timestamp()
        token_expiration = decoded_token.get("exp")
        if token_expiration and now > token_expiration:
            raise AuthenticationException("Token has expired")

        return ("x-access-token", token)

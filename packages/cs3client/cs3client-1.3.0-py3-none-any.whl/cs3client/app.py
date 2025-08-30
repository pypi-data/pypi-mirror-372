"""
app.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import logging
from typing import Optional

import cs3.app.registry.v1beta1.registry_api_pb2 as cs3arreg
import cs3.app.registry.v1beta1.resources_pb2 as cs3arres
import cs3.gateway.v1beta1.gateway_api_pb2 as cs3gw
import cs3.app.provider.v1beta1.resources_pb2 as cs3apr
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub

from .cs3resource import Resource
from .statuscodehandler import StatusCodeHandler
from .config import Config


class App:
    """
    App class to handle app related API calls with CS3 Gateway API.
    """

    def __init__(
        self,
        config: Config,
        log: logging.Logger,
        gateway: GatewayAPIStub,
        status_code_handler: StatusCodeHandler,
    ) -> None:
        """
        Initializes the App class with configuration, logger, auth, and gateway stub,

        :param config: Config object containing the configuration parameters.
        :param log: Logger instance for logging.
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway.
        :param status_code_handler: An instance of the StatusCodeHandler class.
        """
        self._status_code_handler: StatusCodeHandler = status_code_handler
        self._gateway: GatewayAPIStub = gateway
        self._log: logging.Logger = log
        self._config: Config = config

    def open_in_app(
            self, auth_token: tuple, resource: Resource, view_mode: Optional[str] = None, app: Optional[str] = None
    ) -> cs3apr.OpenInAppURL:
        """
        Open a file in an app, given the resource, view mode (VIEW_MODE_VIEW_ONLY, VIEW_MODE_READ_ONLY,
        VIEW_MODE_READ_WRITE, VIEW_MODE_PREVIEW), and app name.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param resource: Resource object containing the resource information.
        :param view_mode: View mode of the app.
        :param app: App name.
        :return: URL to open the file in the app.
        :raises: AuthenticationException (Operation not permitted)
        :raises: NotFoundException (Resource not found)
        :raises: UnknownException (Unknown error)
        """
        view_mode_type = None
        if view_mode:
            view_mode_type = cs3gw.OpenInAppRequest.ViewMode.Value(view_mode)
        req = cs3gw.OpenInAppRequest(ref=resource.ref, view_mode=view_mode_type, app=app)
        res = self._gateway.OpenInApp(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "open in app", f"{resource.get_file_ref_str()}")
        self._log.debug(f'msg="Invoked OpenInApp" {resource.get_file_ref_str()} trace="{res.status.trace}"')
        return res.OpenInAppURL

    def list_app_providers(self, auth_token: dict) -> list[cs3arres.ProviderInfo]:
        """
        list_app_providers lists all the app providers.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :return: List of app providers.
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3arreg.ListAppProvidersRequest()
        res = self._gateway.ListAppProviders(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "list app providers")
        self._log.debug(f'msg="Invoked ListAppProviders" res_count="{len(res.providers)}" trace="{res.status.trace}"')
        return res.providers

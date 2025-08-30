"""
cs3client.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import grpc
import logging
import cs3.gateway.v1beta1.gateway_api_pb2_grpc as cs3gw_grpc
from configparser import ConfigParser

from .file import File
from .user import User
from .share import Share
from .statuscodehandler import StatusCodeHandler
from .app import App
from .checkpoint import Checkpoint
from .config import Config


class CS3Client:
    """
    Client class to interact with the CS3 API.
    """

    def __init__(self, config: ConfigParser, config_category: str, log: logging.Logger) -> None:
        """
        Initializes the CS3Client class with configuration and logger.
        :param config: Dictionary containing configuration parameters.
        :param config_category: Category of the configuration parameters.
        :param log: Logger instance for logging.
        """

        self._config: Config = Config(config, config_category)
        self._log: logging.Logger = log

        try:
            self.channel: grpc.Channel = self._create_channel()
            grpc.channel_ready_future(self.channel).result(timeout=self._config.grpc_timeout)
        except grpc.FutureTimeoutError as e:
            log.error(f'msg="Failed to connect to Reva via GRPC" error="{e}"')
            raise TimeoutError("Failed to connect to Reva via GRPC")

        self._gateway: cs3gw_grpc.GatewayAPIStub = cs3gw_grpc.GatewayAPIStub(self.channel)
        self._status_code_handler: StatusCodeHandler = StatusCodeHandler(self._log, self._config)
        self.file: File = File(self._config, self._log, self._gateway, self._status_code_handler)
        self.user: User = User(self._config, self._log, self._gateway, self._status_code_handler)
        self.app: App = App(self._config, self._log, self._gateway, self._status_code_handler)
        self.checkpoint: Checkpoint = Checkpoint(
            self._config, self._log, self._gateway, self._status_code_handler
        )
        self.share = Share(self._config, self._log, self._gateway, self._status_code_handler)

    def _create_channel(self) -> grpc.Channel:
        """
        create_channel creates a gRPC channel to the specified host.

        :return: gRPC channel to the specified host.
        """

        if self._config.ssl_enabled:

            credentials = grpc.ssl_channel_credentials(
                root_certificates=self._config.ssl_ca_cert,
                private_key=self._config.ssl_client_key,
                certificate_chain=self._config.ssl_client_cert,
            )
            channel = grpc.secure_channel(self._config.host, credentials)
        else:
            channel = grpc.insecure_channel(self._config.host)
        return channel

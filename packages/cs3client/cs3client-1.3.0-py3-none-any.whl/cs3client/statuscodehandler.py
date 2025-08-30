"""
statuscodehandler.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import logging
from typing import Optional

import cs3.rpc.v1beta1.code_pb2 as cs3code
import cs3.rpc.v1beta1.status_pb2 as cs3status

from .exceptions import AuthenticationException, PermissionDeniedException, NotFoundException, \
    UnknownException, AlreadyExistsException, FileLockedException, UnimplementedException
from .config import Config


class StatusCodeHandler:
    def __init__(self, log: logging.Logger, config: Config) -> None:
        self._log = log
        self._config = config

    def _log_not_found_info(self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None) -> None:
        self._log.info(
            f'msg="Not found on {operation}" {msg + " " if msg else ""} '
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_authentication_error(
            self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None
    ) -> None:
        self._log.error(
            f'msg="Authentication failed on {operation}" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_permission_denied_info(
            self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None
    ) -> None:
        self._log.info(
            f'msg="Permission denied on {operation}" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_unknown_error(self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None) -> None:
        self._log.error(
            f'msg="Failed to {operation}, unknown error" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_precondition_info(
            self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None
    ) -> None:
        self._log.info(
            f'msg="Failed precondition on {operation}" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_already_exists(self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None) -> None:
        self._log.info(
            f'msg="Already exists on {operation}" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def _log_unimplemented(self, status: cs3status.Status, operation: str, status_msg: str, msg: Optional[str] = None) -> None:
        self._log.info(
            f'msg="Invoked {operation} on unimplemented feature" {msg + " " if msg else ""}'
            f'userid="{self._config.auth_client_id if self._config.auth_client_id else "no_id_set"}" '
            f'trace="{status.trace}" reason="{status_msg}"'
        )

    def handle_errors(self, status: cs3status.Status, operation: str, msg: Optional[str] = None) -> None:

        if status.code == cs3code.CODE_OK:
            return
        # status.message.replace('"', "'") is not allowed inside f strings python<3.12
        status_message = status.message.replace('"', "'")

        if status.code == cs3code.CODE_FAILED_PRECONDITION or status.code == cs3code.CODE_ABORTED:
            self._log_precondition_info(status, operation, status_message, msg)
            raise FileLockedException
        if status.code == cs3code.CODE_ALREADY_EXISTS:
            self._log_already_exists(status, operation, status_message, msg)
            raise AlreadyExistsException
        if status.code == cs3code.CODE_UNIMPLEMENTED:
            self._log.info(f'msg="Invoked {operation} on unimplemented feature" ')
            raise UnimplementedException
        if status.code == cs3code.CODE_NOT_FOUND:
            self._log_not_found_info(status, operation, status_message, msg)
            raise NotFoundException
        if status.code == cs3code.CODE_UNAUTHENTICATED:
            self._log_authentication_error(status, operation, status_message, msg)
            raise AuthenticationException
        if status.code == cs3code.CODE_PERMISSION_DENIED:
            self._log_permission_denied_info(status, operation, status_message, msg)
            raise PermissionDeniedException
        if status.code != cs3code.CODE_OK:
            if "path not found" in str(status.message).lower():
                self._log.info(f'msg="Invoked {operation} on missing file" ')
                raise NotFoundException
            self._log_unknown_error(status, operation, status_message, msg)
            raise UnknownException(f'Unknown Error: operation="{operation}" status_code="{status.code}" '
                                   f'message="{status.message}"')

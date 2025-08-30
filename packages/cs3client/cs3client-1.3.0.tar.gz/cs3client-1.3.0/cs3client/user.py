"""
user.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 30/08/2024
"""

import logging
import cs3.identity.user.v1beta1.resources_pb2 as cs3iur
import cs3.identity.user.v1beta1.user_api_pb2 as cs3iu
from cs3.gateway.v1beta1.gateway_api_pb2_grpc import GatewayAPIStub

from .config import Config
from .statuscodehandler import StatusCodeHandler


class User:
    """
    User class to handle user related API calls with CS3 Gateway API.
    """

    def __init__(
        self,
        config: Config,
        log: logging.Logger,
        gateway: GatewayAPIStub,
        status_code_handler: StatusCodeHandler,
    ) -> None:
        """
        Initializes the User class with logger, auth, and gateway stub,

        :param log: Logger instance for logging.
        :param gateway: GatewayAPIStub instance for interacting with CS3 Gateway.
        :param auth: An instance of the auth class.
        """
        self._log: logging.Logger = log
        self._gateway: GatewayAPIStub = gateway
        self._config: Config = config
        self._status_code_handler: StatusCodeHandler = status_code_handler

    def get_user(self, idp, opaque_id) -> cs3iur.User:
        """
        Get the user information provided the idp and opaque_id.

        :param idp: Identity provider.
        :param opaque_id: Opaque user id.
        :return: User information.
        :raises: return NotFoundException (User not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3iu.GetUserRequest(user_id=cs3iur.UserId(idp=idp, opaque_id=opaque_id), skip_fetching_user_groups=True)
        res = self._gateway.GetUser(request=req)
        self._status_code_handler.handle_errors(res.status, "get user", f'opaque_id="{opaque_id}"')
        self._log.debug(f'msg="Invoked GetUser" opaque_id="{res.user.id.opaque_id}" trace="{res.status.trace}"')
        return res.user

    def get_user_by_claim(self, claim, value) -> cs3iur.User:
        """
        Get the user information provided the claim and value.

        :param claim: Claim to search for.
        :param value: Value to search for.
        :return: User information.
        :raises: NotFoundException (User not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3iu.GetUserByClaimRequest(claim=claim, value=value, skip_fetching_user_groups=True)
        res = self._gateway.GetUserByClaim(request=req)
        self._status_code_handler.handle_errors(res.status, "get user by claim", f'claim="{claim}" value="{value}"')
        self._log.debug(f'msg="Invoked GetUserByClaim" opaque_id="{res.user.id.opaque_id}" trace="{res.status.trace}"')
        return res.user

    def get_user_groups(self, idp, opaque_id) -> list[str]:
        """
        Get the groups the user is a part of.

        :param idp: Identity provider.
        :param opaque_id: Opaque user id.
        :return: A list of the groups the user is part of.
        :raises: NotFoundException (User not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3iu.GetUserGroupsRequest(user_id=cs3iur.UserId(idp=idp, opaque_id=opaque_id))
        res = self._gateway.GetUserGroups(request=req)
        self._status_code_handler.handle_errors(res.status, "get user groups", f'opaque_id="{opaque_id}"')
        self._log.debug(f'msg="Invoked GetUserGroups" opaque_id="{opaque_id}" trace="{res.status.trace}"')
        return res.groups

    def find_users(self, auth_token: tuple, filter) -> list[cs3iur.User]:
        """
        Find a user based on a filter.

        :param auth_token: tuple in the form ('x-access-token', <token>) (see auth.get_token/auth.check_token)
        :param filter: Filter to search for.
        :return: a list of user(s).
        :raises: NotFoundException (User not found)
        :raises: AuthenticationException (Operation not permitted)
        :raises: UnknownException (Unknown error)
        """
        req = cs3iu.FindUsersRequest(filter=filter, skip_fetching_user_groups=True)
        res = self._gateway.FindUsers(request=req, metadata=[auth_token])
        self._status_code_handler.handle_errors(res.status, "find users")
        self._log.debug(f'msg="Invoked FindUsers" filter="{filter}" trace="{res.status.trace}"')
        return res.users

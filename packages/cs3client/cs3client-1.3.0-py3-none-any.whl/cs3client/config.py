"""
config.py

Authors: Rasmus Welander, Diogo Castro, Giuseppe Lo Presti.
Emails: rasmus.oscar.welander@cern.ch, diogo.castro@cern.ch, giuseppe.lopresti@cern.ch
Last updated: 29/07/2024
"""

from configparser import ConfigParser


class Config:
    """
    A class to read and store the configuration parameters provided to the CS3 client.
    """

    def __init__(self, config: ConfigParser, config_category: str) -> None:
        """
        Initializes the Config class with the configuration parameters.

        :param config: Dictionary containing configuration parameters.
        :param config_category: The category of the configuration parameters.
        """
        self._config_category: str = config_category
        self._config: ConfigParser = config

    @property
    def host(self) -> str:
        """
        The host property returns the host address and port from the configuration.

        :return: host address:port
        """
        return self._config.get(self._config_category, "host")

    @property
    def chunk_size(self) -> int:
        """
        The chunk_size property returns the chunk_size value from the configuration,
        fallback to 4194304 if not present.

        :return: The chunk size value.
        """
        return self._config.getint(self._config_category, "chunk_size", fallback=4194304)

    @property
    def grpc_timeout(self) -> int:
        """
        The grpc_timeout property returns the grpc_timeout value from the configuration,
        fallback to 10 if not present.

        :return: The grpc timeout value.
        """
        return self._config.getint(self._config_category, "grpc_timeout", fallback=10)

    @property
    def http_timeout(self) -> int:
        """
        The http_timeout property returns the http_timeout value from the configuration,
        fallback to 10 if not present.

        :return: The http timeout value.
        """
        return self._config.getint(self._config_category, "http_timeout", fallback=10)

    @property
    def ssl_enabled(self) -> bool:
        """
        The ssl_enabled property returns the ssl_enabled value from the configuration,
        fallback to True if not present.

        :return: ssl_enabled value.
        """
        return self._config.getboolean(self._config_category, "ssl_enabled", fallback=False)

    @property
    def ssl_verify(self) -> bool:
        """
        The ssl_verify property returns the ssl_verify value from the configuration,

        :return: ssl_verify
        """
        return self._config.getboolean(self._config_category, "ssl_verify", fallback=False)

    @property
    def ssl_client_cert(self) -> str:
        """
        The ssl_client_cert property returns the ssl_client_cert value from the configuration,
        if not present, fallback to an empty string since it is not required if ssl is not enabled.

        :return: ssl_client_cert
        """
        return self._config.get(self._config_category, "ssl_client_cert", fallback=None)

    @property
    def ssl_client_key(self) -> str:
        """
        The ssl_client_key property returns the ssl_client_key value from the configuration,
        if not present, fallback to an empty string since it is not required if ssl is not enabled.

        :return: ssl_client_key
        """
        return self._config.get(self._config_category, "ssl_client_key", fallback=None)

    @property
    def ssl_ca_cert(self) -> str:
        """
        The ssl_ca_cert property returns the ssl_ca_cert value from the configuration,
        if not present, fallback to an empty string since it is not required if ssl is not enabled.

        :return: ssl_ca_cert
        """
        return self._config.get(self._config_category, "ssl_ca_cert", fallback=None)

    @property
    def auth_login_type(self) -> str:
        """
        The auth_login_type property returns the auth_login_type value from the configuration.
        e.g. basic, bearer, oauth, machine.

        :return: auth_login_type
        """
        return self._config.get(self._config_category, "auth_login_type", fallback="basic")

    @property
    def auth_client_id(self) -> str:
        """
        The auth_client_id property returns the auth_client_id value from the configuration,

        :return: auth_client_id
        """
        return self._config.get(self._config_category, "auth_client_id", fallback=None)

    @property
    def auth_client_secret(self) -> str:
        """
        The auth_client_secret property returns the auth_client_secret value from the configuration,

        :return: auth_client_secret
        """
        return self._config.get(self._config_category, "auth_client_secret", fallback=None)

    @property
    def tus_enabled(self) -> bool:
        """
        The tus_enabled property returns the tus_enabled value from the configuration,

        :return: tus_enabled
        """
        return self._config.getboolean(self._config_category, "tus_enabled", fallback=False)

    # For the lock implementation
    @property
    def lock_by_setting_attr(self) -> bool:
        """
        The lock_by_setting_attr property returns the lock_by_setting_attr value from the configuration,
        fallback to False if not present.

        The lock by setting attribute setting should be set if the storage provider does not
        implement locking functionality. In which case the client will use the fallback mechanism
        by locking resources by setting metadata attributes. If lock_not_impl is set to false and
        lock_by_setting_attr is set to true, the client will attempt to lock normally first,
        and if that fails, it will attempt to lock by setting metadata attributes.


        :return: lock_by_setting_attr
        """
        return self._config.getboolean(self._config_category, "lock_by_setting_attr", fallback=False)

    # For the lock implementation
    @property
    def lock_not_impl(self) -> bool:
        """
        The lock_not_impl property returns the lock_not_impl value from the configuration,
        fallback to False if not present.

        The lock not implemented setting should be set if the storage provider
        does not implement locking functionality. In which case the client will use the
        fallback mechanism by locking resources by setting metadata attributes if the
        lock_by_setting_attr is set to True.

        :return: lock_not_impl
        """
        return self._config.getboolean(self._config_category, "lock_not_impl", fallback=False)

    # For the lock implementation
    @property
    def lock_expiration(self) -> int:
        """
        The lock_expiration property returns the lock_expiration value from the configuration,
        fallback to 1800 if not present.

        The lock expiration setting is used to determine the time
        in seconds before a lock is considered expired.

        :return: lock_expiration
        """
        return self._config.getint(self._config_category, "lock_expiration", fallback=1800)

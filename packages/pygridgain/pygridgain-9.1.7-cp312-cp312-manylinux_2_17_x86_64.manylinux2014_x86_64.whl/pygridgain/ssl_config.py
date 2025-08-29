# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import ssl

from pygridgain.constants import SSL_DEFAULT_CIPHERS, SSL_DEFAULT_VERSION


class SSLConfig:
    """
    SSL Configuration.
    """

    def __init__(
        self,
        protocol_version=SSL_DEFAULT_VERSION,
        ciphers=SSL_DEFAULT_CIPHERS,
        cert_reqs: ssl.VerifyMode = ssl.CERT_NONE,
        key_file: str | None = None,
        key_file_password: str | None = None,
        cert_file: str | None = None,
        ca_file: str | None = None,
    ):
        """
        Initialize SSL configuration.

        For the use of the SSL-related parameters see https://docs.python.org/3/library/ssl.html#ssl-certificates.

        :param protocol_version: (optional) SSL version constant from standard `ssl` module. Defaults to TLS v1.2,
        :param ciphers: (optional) ciphers to use. If not provided, `ssl` default ciphers are used,
        :param cert_reqs: (optional) determines how the remote side certificate is treated:

         * `ssl.CERT_NONE` − remote certificate is ignored (default),
         * `ssl.CERT_OPTIONAL` − remote certificate will be validated,
           if provided,
         * `ssl.CERT_REQUIRED` − valid remote certificate is required,

        :param key_file: (optional) a path to SSL key file to identify local (client) party,
        :param key_file_password: (optional) password for SSL key file, can be provided when key file is encrypted
         to prevent OpenSSL password prompt,
        :param cert_file: (optional) a path to ssl certificate file to identify local (client) party,
        :param ca_file: (optional) a path to a trusted certificate or a certificate chain.
         Required to check the validity of the remote (server-side) certificate,
        """
        self._protocol_version = protocol_version
        self._ciphers = ciphers
        self._cert_reqs = cert_reqs
        self._key_file = key_file
        self._key_file_password = key_file_password
        self._cert_file = cert_file
        self._ca_file = ca_file

    @property
    def protocol_version(self):
        """SSL version constant from standard `ssl` module."""
        return self._protocol_version

    @property
    def ciphers(self):
        """Ciphers to use."""
        return self._ciphers

    @property
    def cert_reqs(self):
        """
        Determines how the remote side certificate is treated:

         * `ssl.CERT_NONE` − remote certificate is ignored (default),
         * `ssl.CERT_OPTIONAL` − remote certificate will be validated,
           if provided,
         * `ssl.CERT_REQUIRED` − valid remote certificate is required,
        """
        return self._cert_reqs

    @property
    def key_file(self):
        """A path to SSL key file to identify local (client) party."""
        return self._key_file

    @property
    def key_file_password(self):
        """Password for SSL key file, can be provided when key file is encrypted to prevent OpenSSL password prompt."""
        return self._key_file_password

    @property
    def cert_file(self):
        """A path to SSL certificate file to identify local (client) party."""
        return self._cert_file

    @property
    def ca_file(self):
        """
        A path to a trusted certificate or a certificate chain.
        Required to check the validity of the remote (server-side) certificate.
        """
        return self._ca_file

# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
"""
This module contains some constants, used internally throughout the API.
"""

import ssl

__all__ = [
    "SUPPORTED_PROTOCOLS",
    "PROTOCOL_BYTE_ORDER",
    "PROTOCOL_STRING_ENCODING",
    "PROTOCOL_CHAR_ENCODING",
    "SSL_DEFAULT_VERSION",
    "SSL_DEFAULT_CIPHERS",
    "DEFAULT_PORT",
]

SUPPORTED_PROTOCOLS = {
    (3, 0, 0),
}

PROTOCOL_BYTE_ORDER = "big"
PROTOCOL_STRING_ENCODING = "utf-8"
PROTOCOL_CHAR_ENCODING = "utf-16le"

SSL_DEFAULT_VERSION = ssl.PROTOCOL_TLS
SSL_DEFAULT_CIPHERS = ssl._DEFAULT_CIPHERS

DEFAULT_PORT = 10800

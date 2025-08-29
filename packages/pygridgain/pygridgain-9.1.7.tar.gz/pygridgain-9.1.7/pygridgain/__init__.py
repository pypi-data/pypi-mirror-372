# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import os

from pygridgain.async_binary_map import AsyncBinaryMap
from pygridgain.async_client import AsyncClient
from pygridgain.async_structures import AsyncStructures
from pygridgain.basic_authenticator import BasicAuthenticator
from pygridgain.end_point import EndPoint
from pygridgain.error_code import ErrorCode, ErrorGroup
from pygridgain.ignite_error import IgniteError
from pygridgain.ssl_config import SSLConfig

__all__ = [
    "AsyncBinaryMap",
    "AsyncClient",
    "AsyncStructures",
    "EndPoint",
    "IgniteError",
    "ErrorCode",
    "ErrorGroup",
    "SSLConfig",
    "BasicAuthenticator",
]


def _read_version():
    version_path = os.path.join(os.path.dirname(__file__), "_version.txt")
    with open(version_path, "r") as fd:
        version = fd.read().strip()
        if not version:
            raise RuntimeError("Cannot find version information")
        return version


__version__ = _read_version()

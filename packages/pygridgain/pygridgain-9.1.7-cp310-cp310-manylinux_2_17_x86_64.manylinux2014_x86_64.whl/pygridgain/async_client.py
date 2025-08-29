# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import collections
from typing import Iterable

from .async_cluster_connection import AsyncClusterConnection
from .async_structures import AsyncStructures
from .end_point import EndPoint
from .error_code import ErrorCode
from .ignite_error import IgniteError


class AsyncClient:
    """
    Asynchronous Client implementation.
    """

    def __init__(self, address: EndPoint | Iterable[EndPoint], **kwargs):
        """
        Initialize client.

        :param address: An address or a collection of addresses to connect to.
         An address is an EndPoint or a Sequence of EndPoints.
        :param connection_timeout: (optional) Timeout (in seconds) for performing initial connection with the node.
         Default is 10.0 seconds,
        :param ssl_config: (optional) SSLConfig parameters for establishing secure connection.
         If not provided, a non-secure connection will be created.
        :param authenticator: (optional) Authenticator object. If none is provided, authentication is disabled.
        :param heartbeat_interval: (optional) Interval in seconds at which heartbeat messages are sent.
         None means heartbeats are disabled.
         Default is 30.0 seconds.
        """
        address0 = [address] if isinstance(address, EndPoint) else address
        AsyncClient._validate_address(address0)

        self._cluster_connection = AsyncClusterConnection(address0, **kwargs)
        self._structures = AsyncStructures(self._cluster_connection)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        """
        Connect to cluster node(s).
        """
        return await self._cluster_connection.connect()

    async def close(self):
        """
        Close connection to the cluster.
        """
        await self._cluster_connection.close()

    def structures(self) -> AsyncStructures:
        """
        Get AsyncStructures facade instance which can be used to create and access to different distributed structures.
        """
        return self._structures

    @staticmethod
    def _validate_address(address: Iterable[EndPoint]):
        if not isinstance(address, collections.abc.Iterable) or isinstance(address, (str, bytes, bytearray)):
            raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, f"Wrong address argument type: {type(address).__name__}")

        empty = True
        for addr in address:
            empty = False
            if not isinstance(addr, EndPoint):
                raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, f"Wrong address argument type: {type(addr).__name__}")
            if not addr.host:
                raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, f"Address host cannot be empty: {addr}")

        if empty:
            raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, "No addresses provided to connect")

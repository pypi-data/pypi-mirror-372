# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import asyncio
import logging
import random
import threading
from typing import TYPE_CHECKING, Iterable

from pygridgain import _native_extension

from .async_node_connection import AsyncNodeConnection, RequestBuilder
from .end_point import EndPoint
from .error_code import ErrorCode
from .ignite_error import IgniteError, connection_errors

if TYPE_CHECKING:
    from pygridgain._native_extension import _PySqlResultSet, _PySqlResultSetRow

logger = logging.getLogger(".".join(__name__.split(".")[:-1]))


class _SqlResultSetRow:
    def __init__(self, py_row_data: "_PySqlResultSetRow"):
        self._py_row_data = py_row_data

    def long_value(self, idx: int) -> int:
        """
        Get a column value as a long value.

        :param idx: Column index.
        :return: Column value converted to long.
        """
        return self._py_row_data.long_value(idx)

    def binary_value(self, idx: int) -> bytes:
        """
        Get a column value as a binary value.

        :param idx: Column index.
        :return: Column value converted to bytes.
        """
        return self._py_row_data.binary_value(idx)


class _AsyncSqlResultSet:
    def __init__(self, connection: AsyncNodeConnection, py_result_set: "_PySqlResultSet"):
        self._connection = connection
        self._py_result_set = py_result_set
        self._local_row_idx = 0
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._closed:
            raise StopAsyncIteration

        if not self._py_result_set.has_row(self._local_row_idx):
            if self._py_result_set.closed_remotely():
                raise StopAsyncIteration

            await self._get_next_page()
            self._local_row_idx = 0

        row = self._py_result_set.get_row(self._local_row_idx)
        self._local_row_idx += 1

        return _SqlResultSetRow(row)

    async def _get_next_page(self):

        def req_builder(req_id: int) -> bytes:
            return self._py_result_set.make_next_page_request(req_id)

        resp_data = await self._connection.request(req_builder=req_builder)
        self._py_result_set.parse_next_page_response(resp_data)

    async def close(self):
        """
        Close the cursor.
        """
        if not self._closed and not self._py_result_set.closed_remotely():
            self._closed = True
            try:

                def req_builder(req_id: int) -> bytes:
                    return self._py_result_set.make_close_request(req_id)

                await self._connection.request(req_builder=req_builder)
            except IgniteError as e:
                logger.debug("Error while trying to close SQL cursor: %s", e)


class AsyncClusterConnection:
    """
    Asynchronous cluster connection, which is basically an abstraction over multiple node connections.
    """

    def __init__(self, address: Iterable[EndPoint], **kwargs):
        """
        Initialize cluster connection.

        :param address: An address or a collection of addresses to connect to. An address is a str or a tuple (str, int)
         where the first value is the host and the second value is the port. If the address is a 'str', only then
         the default port is used (10800).
        :param connection_timeout: (optional) sets timeout (in seconds) for performing initial connection with the node.
         Default is 10.0 seconds,
        :param ssl_config: (optional) SSLConfig parameters for establishing secure connection.
         If not provided, a non-secure connection will be created.
        :param authenticator: (optional) Authenticator object. If none is provided, authentication is disabled.
        :param heartbeat_interval: (optional) Interval in seconds at which heartbeat messages are sent.
         Default is 30.0 seconds.
        """
        self._address = address
        self._connection_args = kwargs
        self._nodes = []
        self._protocol_context = None
        self._observable_ts = 0
        self._observable_ts_lock = threading.Lock()

    async def connect(self):
        """
        Connect to cluster node(s).
        """
        return await self._connect(self._address)

    async def _connect(self, end_points: Iterable[EndPoint]):
        for end_point in end_points:
            conn = AsyncNodeConnection(self, end_point, **self._connection_args)
            self._nodes.append(conn)

        connect_results = await asyncio.gather(*[conn.connect() for conn in self._nodes], return_exceptions=True)

        reconnect_coro = []
        for i, res in enumerate(connect_results):
            if isinstance(res, Exception):
                if isinstance(res, connection_errors):
                    reconnect_coro.append(self._nodes[i].reconnect())
                else:
                    raise res

        await asyncio.gather(*reconnect_coro, return_exceptions=True)

        if self._protocol_context is None:
            raise IgniteError(ErrorCode.CONNECTION, "Failed to connect to the cluster")

    async def close(self):
        await asyncio.gather(*[conn.close() for conn in self._nodes], return_exceptions=True)
        self._nodes.clear()

    async def request(self, req_builder: RequestBuilder, timeout: float | None) -> bytearray | None:
        """
        Perform request.

        :param req_builder: Request builder function.
        :param timeout: (optional) Timeout in seconds.
        """
        try:
            return (await asyncio.wait_for(self._do_request(req_builder), timeout=timeout))[0]
        except asyncio.TimeoutError:
            raise IgniteError(ErrorCode.CONNECTION, "The request has timed out")

    async def request_node(self, req_builder: RequestBuilder, timeout: float | None) -> (bytearray | None, AsyncNodeConnection):
        """
        Perform request.

        :param req_builder: Request builder function.
        :param timeout: (optional) Timeout in seconds.
        """
        try:
            return await asyncio.wait_for(self._do_request(req_builder), timeout=timeout)
        except asyncio.TimeoutError:
            raise IgniteError(ErrorCode.CONNECTION, "The request has timed out")

    async def _do_request(self, req_builder: RequestBuilder) -> (bytearray | None, AsyncNodeConnection):
        """
        Perform request.

        :param req_builder: Request builder function.
        """
        node = await self._get_random_node(reconnect=True)
        return await node.request(req_builder), node

    async def _get_random_node(self, reconnect=True) -> AsyncNodeConnection:
        alive_nodes = [n for n in self._nodes if n.alive]
        if alive_nodes:
            return random.choice(alive_nodes)
        elif reconnect:
            await asyncio.gather(*[n.reconnect() for n in self._nodes], return_exceptions=True)
            return await self._get_random_node(reconnect=False)
        else:
            # cannot choose from an empty sequence
            raise IgniteError(ErrorCode.CONNECTION, "Can not reconnect: out of nodes") from None

    async def sql(self, query: str) -> _AsyncSqlResultSet:
        """
        Perform an SQL query.
        This is a temp method until we implement a proper SQL API.

        :param query: Query.
        :return: Result set.
        """

        def req_builder(req_id: int) -> bytes:
            return _native_extension.make_sql_request(req_id, self._observable_ts, query)

        resp_data, node = await self.request_node(req_builder=req_builder, timeout=None)

        return _AsyncSqlResultSet(node, _native_extension.parse_sql_response(resp_data))

    def on_observable_ts(self, value: int):
        """
        Callback to call when observable timestamp changes.
        :param value: New value.
        """
        with self._observable_ts_lock:
            if value > self._observable_ts:
                self._observable_ts = value

    @property
    def protocol_context(self):
        """
        Returns protocol context, or None, if no connection to the cluster was established yet.

        This method is not a part of the public API. Unless you wish to extend the `pygridgain` capabilities
        (with additional testing, logging, examining connections, etc.), you probably should not use it.
        """
        return self._protocol_context

    @protocol_context.setter
    def protocol_context(self, value):
        self._protocol_context = value

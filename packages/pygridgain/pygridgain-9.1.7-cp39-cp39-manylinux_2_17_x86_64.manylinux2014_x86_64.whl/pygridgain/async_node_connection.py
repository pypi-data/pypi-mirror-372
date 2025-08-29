# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/

import asyncio
import logging
import socket
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from pygridgain import _native_extension
from pygridgain.bitmask_feature import BitmaskFeature
from pygridgain.constants import PROTOCOL_BYTE_ORDER, SUPPORTED_PROTOCOLS
from pygridgain.end_point import EndPoint
from pygridgain.error_code import ErrorCode, ErrorGroup
from pygridgain.ignite_error import IgniteError, connection_errors
from pygridgain.protocol_context import ProtocolContext
from pygridgain.utils import (
    check_ssl_config,
    create_ssl_context,
    extra_from_connection_config,
)

if TYPE_CHECKING:
    from pygridgain._native_extension import AsyncClusterConnection

MAGIC_BYTES = b"IGNI"

logger = logging.getLogger(".".join(__name__.split(".")[:-1]))

RequestBuilder = Callable[[int], bytes]


class HandshakeError(IgniteError):
    """
    This exception is raised on connection handshake failure.
    """

    def __init__(self, expected_version: (int, int, int), message: str):
        super().__init__(ErrorCode.HANDSHAKE_HEADER, message)
        self.expected_version = expected_version
        self.message = message


@dataclass
class HandshakeResponse:
    version: (int, int, int)
    error: IgniteError | None
    observable_ts: int
    idle_timeout_ms: int


@dataclass
class ResponseHeader:
    req_id: int
    assignment_ts: int | None
    observable_ts: int
    error: IgniteError | None
    bytes_processed: int


class BaseProtocol(asyncio.Protocol):
    def __init__(self, conn, handshake_fut):
        super().__init__()
        self._buffer = bytearray()
        self._conn = conn
        self._handshake_fut = handshake_fut
        self._magic_received = False
        self._expected_size = 0

    def connection_lost(self, exc):
        self.__process_connection_error(exc if exc else socket.error("Connection closed"))

    def connection_made(self, transport: asyncio.WriteTransport) -> None:
        try:
            self.__send_handshake(transport, self._conn)
        except Exception as e:
            self._handshake_fut.set_exception(e)

    def data_received(self, data: bytes) -> None:
        self._buffer += data
        if len(self._buffer) < 4:
            return

        if not self._magic_received:
            if self._buffer[:4] != MAGIC_BYTES:
                raise IgniteError(
                    ErrorCode.PROTOCOL,
                    "Failed to receive magic bytes in handshake response. "
                    "Possible reasons: wrong port number used, TLS is enabled on server but not on client.",
                )
            self._magic_received = True
            self._buffer = self._buffer[4:]

        while (message := self.__get_next_message()) is not None:
            if not self._handshake_fut.done():
                handshake_rsp = self.__parse_handshake(message)
                self._handshake_fut.set_result(handshake_rsp)
            else:
                self._conn.process_message(message)

    def __get_next_message(self) -> bytearray | None:
        if len(self._buffer) < 4:
            return None

        if self._expected_size == 0:
            self._expected_size = int.from_bytes(self._buffer[0:4], byteorder=PROTOCOL_BYTE_ORDER, signed=True)
            if self._expected_size <= 0:
                raise IgniteError(ErrorCode.PROTOCOL, f"Unexpected message size: {self._expected_size}")

        logger.debug("Expected size=%i", self._expected_size)
        if len(self._buffer) < self._expected_size + 4:
            return None

        message = self._buffer[4 : self._expected_size + 4]
        self._buffer = self._buffer[self._expected_size + 4 :]
        self._expected_size = 0

        return message

    def __process_connection_error(self, exc):
        connected = self._handshake_fut.done()
        if not connected:
            self._handshake_fut.set_exception(exc)
        self._conn.process_connection_lost(exc, connected)

    @staticmethod
    def __send_handshake(transport, conn):
        extra = extra_from_connection_config(conn.authenticator)
        handshake_req = BaseProtocol.__make_handshake(conn.protocol_context.version, extra)
        transport.write(handshake_req)

    @staticmethod
    def __parse_handshake(message) -> HandshakeResponse:
        return _native_extension.parse_handshake(message)

    @staticmethod
    def __make_handshake(version: (str, str, str), extra: {str, str}) -> bytes:
        return _native_extension.make_handshake(version, extra)


class AsyncNodeConnection:
    """
    Asyncio connection to a server node. It serves multiple purposes:

    * wrapper of asyncio streams. See also https://docs.python.org/3/library/asyncio-stream.html
    * encapsulates handshake and reconnection.
    """

    def __init__(
        self,
        cluster_connection: "AsyncClusterConnection",
        end_point: EndPoint,
        connection_timeout: float = 10.0,
        authenticator=None,
        ssl_config=None,
        heartbeat_interval: float = 30.0,
    ):
        """
        Initialize connection.

        For the use of the SSL-related parameters see
        https://docs.python.org/3/library/ssl.html#ssl-certificates.

        :param cluster_connection: Cluster connection,
        :param end_point: Server node's address,
        :param connection_timeout: (optional) sets timeout (in seconds) for performing initial connection with the node,
         Default is 10.0 seconds,
        :param authenticator: (optional) Authenticator object.
         If none is provided, authentication is disabled,
        :param ssl_config: (optional) SSL Configuration object,
        :param heartbeat_interval: (optional) Interval in seconds at which heartbeat messages are sent.
        """
        if not end_point:
            raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, "Address is not specified for the connection")

        if connection_timeout <= 0.0:
            raise IgniteError(ErrorCode.ILLEGAL_ARGUMENT, "Argument 'connection_timeout' should be positive")

        check_ssl_config(ssl_config)

        self.authenticator = authenticator

        self._cluster_connection = cluster_connection
        self._connection_timeout = connection_timeout
        self._end_point = end_point
        self._ssl_config = ssl_config
        self._heartbeat_interval = heartbeat_interval
        self._failed = False
        self._pending_reqs = {}
        self._transport = None
        self._loop = asyncio.get_event_loop()
        self._closed = False
        self._transport_closed_fut = None
        self._req_id_counter = 0
        self._req_id_counter_lock = threading.Lock()
        self._heartbeat_task = None

    @property
    def closed(self) -> bool:
        """Tells if the socket is closed."""
        return self._closed or not self._transport or self._transport.is_closing()

    @property
    def failed(self) -> bool:
        """Tells if connection is failed."""
        return self._failed

    @property
    def alive(self) -> bool:
        """Tells if connection is up and no failure detected."""
        return not self.failed and not self.closed

    @property
    def protocol_context(self):
        """
        Returns protocol context, or None, if no connection to the cluster was yet established.
        """
        return self._cluster_connection.protocol_context

    async def connect(self):
        """
        Connect to the given server node with protocol version fallback.
        """
        if self.alive:
            return
        await self._connect()

    async def _connect(self):
        detecting_protocol = False

        if self._cluster_connection.protocol_context is None:
            detecting_protocol = True
            self._cluster_connection.protocol_context = ProtocolContext(max(SUPPORTED_PROTOCOLS), BitmaskFeature.all_supported())

        while True:
            try:
                self._on_handshake_start()
                result = await self._connect_version()
                self._on_handshake_success(result)
                return
            except HandshakeError as e:
                if e.expected_version in SUPPORTED_PROTOCOLS:
                    self._cluster_connection.protocol_context.version = e.expected_version
                    continue
                else:
                    self._on_handshake_fail(e)
                    raise e
            except IgniteError as e:
                self._on_handshake_fail(e)
                raise e
            except Exception as e:
                self._on_handshake_fail(e)
                # restore undefined protocol version
                if detecting_protocol:
                    self._cluster_connection.protocol_context = None
                raise IgniteError(ErrorCode.CONNECTION, "Failed to connect to the cluster") from e

    def process_connection_lost(self, err, reconnect=False):
        self._failed = True
        for _, fut in self._pending_reqs.items():
            fut.set_exception(err)
        self._pending_reqs.clear()

        if self._transport_closed_fut and not self._transport_closed_fut.done():
            self._transport_closed_fut.set_result(None)

        if reconnect and not self._closed:
            self._on_connection_lost(err)
            self._loop.create_task(self._reconnect())

    def process_message(self, data: bytearray):
        resp_header: ResponseHeader = _native_extension.read_response_header(data)
        logger.debug("Received a message with id=%i and len=%i", resp_header.req_id, len(data))

        self._cluster_connection.on_observable_ts(resp_header.observable_ts)

        data = data[resp_header.bytes_processed :]
        if resp_header.req_id in self._pending_reqs:
            if resp_header.error:
                self._pending_reqs[resp_header.req_id].set_exception(resp_header.error)
            else:
                self._pending_reqs[resp_header.req_id].set_result(data)
                del self._pending_reqs[resp_header.req_id]

    async def _do_connect(self, ssl_context) -> HandshakeResponse:
        """
        Establish transport level connection and wait for the protocol handshake.
        """
        handshake_fut = self._loop.create_future()
        self._transport, _ = await self._loop.create_connection(
            lambda: BaseProtocol(self, handshake_fut), host=self._end_point.host, port=self._end_point.port, ssl=ssl_context
        )

        return await handshake_fut

    async def _connect_version(self) -> HandshakeResponse:
        """
        Connect to the given server node using the protocol version defined on the client.
        """
        ssl_context = create_ssl_context(self._ssl_config)
        self._closed = False

        try:
            handshake_rsp = await asyncio.wait_for(self._do_connect(ssl_context), timeout=self._connection_timeout)
        except asyncio.TimeoutError:
            raise IgniteError(ErrorCode.CONNECTION, f"Initial connection establishment with {self._end_point} timed out")

        if handshake_rsp.error:
            await self.close()
            self._process_handshake_error(handshake_rsp)

        return handshake_rsp

    async def reconnect(self):
        await self._reconnect()

    async def _reconnect(self):
        if self.alive:
            return

        await self._close_transport()
        # connect and silence the connection errors
        try:
            await self._connect()
        except connection_errors:
            pass

    async def request(self, req_builder: RequestBuilder) -> bytearray | None:
        """
        Perform request.

        :param req_builder: Request builder function.
        :return: Response data.
        """
        if not self.alive:
            raise IgniteError(ErrorCode.CONNECTION, "Attempt to use closed connection.")

        req_id = self._next_req_id()
        data = req_builder(req_id)

        if data is None:
            return None

        return await self._send(req_id, data)

    async def _send(self, req_id, data):
        fut = self._loop.create_future()
        self._pending_reqs[req_id] = fut
        try:
            logger.debug("Sending req_id=%i size=%i", req_id, len(data))
            self._transport.write(data)
            return await fut
        except Exception as e:
            raise IgniteError(ErrorCode.CONNECTION, f"Error while performing a request id={req_id} with {self._end_point}") from e

    async def close(self):
        self._closed = True
        await self._close_transport()

    async def _close_transport(self):
        """
        Close connection.
        """
        if self._transport and not self._transport.is_closing():
            self._transport_closed_fut = self._loop.create_future()

            self._transport.close()
            self._transport = None
            try:
                await asyncio.wait_for(self._transport_closed_fut, 1.0)
            except asyncio.TimeoutError:
                pass
            finally:
                self._on_connection_lost(expected=True)
                self._transport_closed_fut = None

    def _process_handshake_error(self, response: HandshakeResponse):
        # if handshake fails for any reason other than protocol mismatch
        # (i.e., authentication error), the server version is 0.0.0
        if response.error.error_group == ErrorGroup.AUTHENTICATION:
            raise response.error

        protocol_version = self._cluster_connection.protocol_context.version
        server_version = response.version

        error_text = f"Handshake error: {response.error}"
        if any(server_version):
            error_text += (
                f" Server expects protocol version "
                f"{server_version[0]}.{server_version[1]}.{server_version[2]}. "
                f"Client provides "
                f"{protocol_version[0]}.{protocol_version[1]}.{protocol_version[2]}."
            )
        raise HandshakeError(server_version, error_text)

    def _on_handshake_start(self):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Connecting to node %s with protocol context %s", self._end_point, self.protocol_context)

    async def send_heartbeat(self) -> bool:
        if not self.alive:
            return False

        def req_builder(req_id: int) -> bytes:
            return _native_extension.make_heartbeat_request(req_id)

        try:
            await self.request(req_builder=req_builder)
        except IgniteError:
            # It's OK if we were not able to send a request.
            # Means the connection is dead already.
            return False

        return True

    async def heartbeat_task(self, interval: float):
        keep_running = True
        while keep_running:
            await asyncio.sleep(interval)
            keep_running = await self.send_heartbeat()

    def _on_handshake_success(self, resp: HandshakeResponse):
        self._cluster_connection.protocol_context.features = BitmaskFeature.no_supported()
        self._failed = False
        self._cluster_connection.on_observable_ts(resp.observable_ts)

        if self._heartbeat_interval is not None:
            idle_timeout = resp.idle_timeout_ms / 1000.0

            # The interval should be no greater than one third of the idle timeout.
            # Otherwise, there is a chance that the client is going to be disconnected on idle timeout,
            # and this is exactly what we want to prevent with heartbeats.
            actual_heartbeat_interval = min(idle_timeout / 3, self._heartbeat_interval)

            # We don't want to DDOS the server with heartbeats, so the minimal interval is 0.5 seconds
            actual_heartbeat_interval = max(0.5, actual_heartbeat_interval)

            self._heartbeat_task = asyncio.create_task(self.heartbeat_task(actual_heartbeat_interval), name="Delayed HeartBeat")

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Connected to node %s with protocol context %s", self._end_point, self.protocol_context)

    def _on_handshake_fail(self, err: Exception):
        self._failed = True

        if isinstance(err, IgniteError) and err.error_group == ErrorGroup.AUTHENTICATION:
            logger.error("Authentication failed while connecting to node %s: %s", self._end_point, err)
        else:
            logger.error(
                "Failed to perform handshake, connection to node %s with protocol context %s failed: %s",
                self._end_point,
                self.protocol_context,
                err,
                exc_info=True,
            )

    def _on_connection_lost(self, err=None, expected=False):
        if expected:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Connection closed to node %s", self._end_point)
        else:
            logger.info("Connection lost to node %s: %s", self._end_point, err)

    def _next_req_id(self):
        with self._req_id_counter_lock:
            req_id = self._req_id_counter
            self._req_id_counter += 1
            return req_id

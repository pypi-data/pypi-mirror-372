# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
from typing import TYPE_CHECKING, AsyncIterator, Iterable, Optional, Tuple, Union

from pygridgain.async_cluster_connection import AsyncClusterConnection
from pygridgain.error_code import ErrorCode
from pygridgain.ignite_error import IgniteError

if TYPE_CHECKING:
    from pygridgain._native_extension import _PyBinaryMap


class AsyncBinaryMap:
    """
    An object that maps keys to values.
    A map cannot contain duplicate keys;
    Each key can map to at most one value.
    """

    Binary = Union[bytes, bytearray]

    def __init__(self, cluster_connection: AsyncClusterConnection, py_map: "_PyBinaryMap"):
        self._cluster_connection = cluster_connection
        self._py_map = py_map
        self._table_name = self._py_map.table_name()

    async def put(self, key: Binary, value: Binary) -> Optional[bytes]:
        """
        Associates the specified value with the specified key in this map. If the map previously contained a mapping for
        the key, the old value is replaced by the specified value.

        :param key: Key.
        :param value: Value.
        :return: The previous value associated with the key, or None if there was no mapping for key.
        """

        def req_builder(req_id: int) -> bytes:
            return self._py_map.make_put_request(req_id, key, value)

        resp_data = await self._cluster_connection.request(req_builder=req_builder, timeout=None)

        return self._py_map.parse_value_response(resp_data)

    async def get(self, key: Binary, default: Optional[bytes] = None) -> Optional[bytes]:
        """
        Returns the value to which the specified key is mapped, or None if this map contains no mapping for the key.

        :param key: Key.
        :param default: The value to return if the value is not present in the Map.
        :return: The value to which the specified key is mapped, or None if this map contains no mapping for the key.
        """

        def req_builder(req_id: int) -> bytes:
            return self._py_map.make_get_request(req_id, key)

        resp_data = await self._cluster_connection.request(req_builder=req_builder, timeout=None)

        res = self._py_map.parse_value_response(resp_data)
        return res if res is not None else default

    async def pop(self, key: Binary, default: Optional[bytes] = None) -> Optional[bytes]:
        """
        Removes the mapping for a key from this map if it is present.

        :param key: Key.
        :param default: The value to return if the value is not present in the Map.
        :return: The value with which this map previously associated the key, or None if the map contained no mapping
          for the key.
        """

        def req_builder(req_id: int) -> bytes:
            return self._py_map.make_remove_request(req_id, key)

        resp_data = await self._cluster_connection.request(req_builder=req_builder, timeout=None)

        res = self._py_map.parse_value_response(resp_data)
        return res if res is not None else default

    async def contains(self, key: Binary) -> bool:
        """
        Returns True if this map contains a mapping for the specified key.

        :param key: Key.
        :return: True if this map contains a mapping for the specified key, False otherwise.
        """

        def req_builder(req_id: int) -> bytes:
            return self._py_map.make_contains_request(req_id, key)

        resp_data = await self._cluster_connection.request(req_builder=req_builder, timeout=None)

        return self._py_map.parse_bool_response(resp_data)

    async def put_all(self, entries: Iterable[Tuple[Binary, Binary]]) -> None:
        """
        Copies all the mappings from the specified map to this map.
        The effect of this call is equivalent to that of calling put on this map once for each mapping from key to value
        in the specified map.

        :param entries: Entries.
        """
        entries_dict = None
        try:
            entries_dict = dict(entries)
        except TypeError as e:
            raise IgniteError(
                ErrorCode.ILLEGAL_ARGUMENT, f"Entries must be Iterable[Tuple[Binary, Binary]], got {type(entries).__name__}"
            ) from e

        def req_builder(req_id: int) -> bytes:
            return self._py_map.make_put_all_request(req_id, entries_dict)

        await self._cluster_connection.request(req_builder=req_builder, timeout=None)

    async def __aiter__(self) -> AsyncIterator[tuple[bytes, bytes]]:
        """
        Returns read-only async cursor to all entries of the map.
        """
        async with await self._cluster_connection.sql(f"SELECT * FROM {self._table_name}") as result_set:
            async for row in result_set:
                yield row.binary_value(0), row.binary_value(1)

    async def clear(self) -> None:
        """
        Removes all the entries from this map. The map will be empty after this call returns.
        """
        async with await self._cluster_connection.sql(f"DELETE FROM {self._table_name}"):
            pass

    async def count(self) -> int:
        """
        Returns the number of entries in the map.

        :return: The number of entries in the map.
        """
        async with await self._cluster_connection.sql(f"SELECT COUNT(*) FROM {self._table_name}") as result_set:
            first_row = await anext(result_set)
            return first_row.long_value(0)

    async def empty(self) -> bool:
        """
        Returns True if this map contains no entries.
        Works much faster than count().

        :return: True if this map contains no entries and False otherwise.
        """
        async with await self._cluster_connection.sql(f"SELECT 1 FROM {self._table_name} limit 1") as result_set:
            return (await anext(result_set, None)) is None

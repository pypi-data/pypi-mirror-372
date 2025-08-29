# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
from pygridgain import _native_extension
from pygridgain.async_binary_map import AsyncBinaryMap
from pygridgain.async_cluster_connection import AsyncClusterConnection


class AsyncStructures:
    """
    A facade that provides the ability to create or access to different distributed structures.
    """

    def __init__(self, cluster_connection: AsyncClusterConnection):
        self._cluster_connection = cluster_connection

    async def get_or_create_binary_map(self, name: str) -> AsyncBinaryMap:
        """
        Get or create a binary map.

        :param name: Map name.
        """

        def req_builder(req_id: int) -> bytes:
            return _native_extension.make_map_request(req_id, name)

        resp_data = await self._cluster_connection.request(req_builder=req_builder, timeout=None)

        py_map = _native_extension.parse_create_map_response(resp_data)

        return AsyncBinaryMap(self._cluster_connection, py_map)

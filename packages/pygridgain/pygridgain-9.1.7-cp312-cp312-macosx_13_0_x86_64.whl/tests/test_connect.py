# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import asyncio

import pytest

from pygridgain import AsyncClient, EndPoint, IgniteError
from tests.util import server_addresses_basic, server_addresses_invalid, server_host


@pytest.mark.parametrize("address", [server_addresses_basic, server_addresses_basic[0]])
@pytest.mark.asyncio
async def test_connection_success(address):
    async with AsyncClient(address=address) as client:
        assert client is not None


@pytest.mark.parametrize("address", [EndPoint(server_host), server_addresses_invalid, server_addresses_invalid[0]])
@pytest.mark.asyncio
async def test_connection_fail(address):
    with pytest.raises(IgniteError) as err:
        client = AsyncClient(address=address, connection_timeout=1.0)
        await client.connect()
    assert err.match("Initial connection establishment with (.*) timed out")


ERR_MSG_WRONG_TYPE = "Wrong address argument type"
ERR_MSG_EMPTY = "No addresses provided to connect"
ERR_MSG_HOST_EMPTY = "Address host cannot be empty"


@pytest.mark.parametrize(
    "address,err_msg",
    [
        (123, ERR_MSG_WRONG_TYPE),
        ([123], ERR_MSG_WRONG_TYPE),
        ([server_addresses_basic[0], 123], ERR_MSG_WRONG_TYPE),
        ([], ERR_MSG_EMPTY),
        ("", ERR_MSG_WRONG_TYPE),
        ([EndPoint("")], ERR_MSG_HOST_EMPTY),
        ([EndPoint("", 10800)], ERR_MSG_HOST_EMPTY),
    ],
)
@pytest.mark.asyncio
async def test_connection_wrong_arg(address, err_msg):
    with pytest.raises(IgniteError) as err:
        client = AsyncClient(address=address, connection_timeout=1.0)
        await client.connect()
    assert err.match(err_msg)


@pytest.mark.parametrize("interval", [2.0, 20.0, 0.0001])
@pytest.mark.asyncio
async def test_heartbeat_enabled(interval, original_name):
    async with AsyncClient(address=server_addresses_basic[0], heartbeat_interval=interval) as client:
        bin_map = await client.structures().get_or_create_binary_map(original_name)
        data_in = {f"{i}".encode("utf-8"): f"{i*2}".encode("utf-8") for i in range(2_000)}
        await bin_map.put_all(data_in)

        data_out = {}
        async for key, val in bin_map:
            data_out[key] = val
            if len(data_out) == 500:
                await asyncio.sleep(7)

        assert data_in == data_out


@pytest.mark.asyncio
async def test_heartbeat_disabled(original_name):
    async with AsyncClient(address=server_addresses_basic[0], heartbeat_interval=None) as client:
        bin_map = await client.structures().get_or_create_binary_map(original_name)
        data_in = {f"{i}".encode("utf-8"): f"{i*2}".encode("utf-8") for i in range(2_000)}
        await bin_map.put_all(data_in)

        data_out = {}
        with pytest.raises(IgniteError) as err:
            async for key, val in bin_map:
                data_out[key] = val
                if len(data_out) == 500:
                    await asyncio.sleep(7)

        assert err.match("Error while performing a request")

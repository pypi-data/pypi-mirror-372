# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import pytest

from pygridgain import AsyncBinaryMap, IgniteError


@pytest.fixture()
async def async_map(async_client, original_name) -> AsyncBinaryMap:
    return await async_client.structures().get_or_create_binary_map(original_name)


@pytest.mark.asyncio
async def test_get_or_create(async_client, original_name):
    bin_map = await async_client.structures().get_or_create_binary_map(original_name)
    assert bin_map is not None


@pytest.mark.asyncio
async def test_put(async_map):
    await async_map.put(b"1", b"0")
    assert await async_map.put(b"1", b"42") == b"0"
    assert await async_map.put(b"1", b"1234567890") == b"42"
    assert await async_map.put(b"1", b"1234567890") == b"1234567890"


@pytest.mark.asyncio
async def test_put_type_error(async_map):
    with pytest.raises(IgniteError) as err:
        await async_map.put(b"1", 1)
    assert err.match("Expected bytes or bytearray as an argument")

    with pytest.raises(IgniteError) as err:
        await async_map.put(1, b"1")
    assert err.match("Expected bytes or bytearray as an argument")


@pytest.mark.asyncio
async def test_get(async_map):
    assert await async_map.get(b"42") is None

    assert await async_map.get(b"42", b"Lorem ipsum") == b"Lorem ipsum"

    await async_map.put(b"1", b"0")
    assert await async_map.get(b"1") == b"0"


@pytest.mark.asyncio
async def test_get_type_error(async_map):
    with pytest.raises(IgniteError) as err:
        await async_map.get(1)
    assert err.match("Expected bytes or bytearray as an argument")


@pytest.mark.asyncio
async def test_pop(async_map):
    await async_map.pop(b"1")
    assert await async_map.pop(b"1") is None
    assert await async_map.pop(b"1", b"5435") == b"5435"
    assert await async_map.get(b"1") is None
    assert await async_map.put(b"1", b"42") is None
    assert await async_map.get(b"1") == b"42"
    assert await async_map.pop(b"1") == b"42"
    assert await async_map.pop(b"1") is None


@pytest.mark.asyncio
async def test_pop_type_error(async_map):
    with pytest.raises(IgniteError) as err:
        await async_map.pop(1)
    assert err.match("Expected bytes or bytearray as an argument")


@pytest.mark.asyncio
async def test_contains(async_map):
    assert not await async_map.contains(b"42")

    await async_map.put(b"1", b"42")
    assert await async_map.contains(b"1")


@pytest.mark.asyncio
async def test_contains_type_error(async_map):
    with pytest.raises(IgniteError) as err:
        await async_map.contains(1)
    assert err.match("Expected bytes or bytearray as an argument")


@pytest.mark.asyncio
async def test_put_all(async_map):
    await async_map.pop(b"1")
    await async_map.pop(b"2")
    await async_map.pop(b"3")
    await async_map.pop(b"4")
    await async_map.pop(b"5")

    await async_map.put_all(
        {
            b"1": b"10",
            b"3": b"30",
            b"4": b"40",
        }
    )

    assert await async_map.get(b"1") == b"10"
    assert await async_map.get(b"2") is None
    assert await async_map.get(b"3") == b"30"
    assert await async_map.get(b"4") == b"40"
    assert await async_map.get(b"5") is None


@pytest.mark.asyncio
async def test_put_all_type_error(async_map):
    with pytest.raises(IgniteError) as err:
        await async_map.put_all({1: 1})
    assert err.match("Expected bytes or bytearray as an argument")

    with pytest.raises(IgniteError) as err:
        await async_map.put_all([1, 2])
    assert err.match("Entries must be Iterable\\[Tuple\\[Binary, Binary\\]\\]")


@pytest.mark.asyncio
async def test_clear(async_map):
    await async_map.put_all(
        {
            b"1": b"1",
            b"3": b"333",
            b"4": b"4444",
        }
    )

    assert await async_map.get(b"1") == b"1"
    assert await async_map.get(b"3") == b"333"
    assert await async_map.get(b"4") == b"4444"

    await async_map.clear()

    assert await async_map.get(b"1") is None
    assert await async_map.get(b"3") is None
    assert await async_map.get(b"4") is None


@pytest.mark.asyncio
async def test_count(async_map):
    await async_map.clear()
    assert await async_map.count() == 0

    await async_map.put(b"1", b"1")
    assert await async_map.count() == 1

    await async_map.put(b"2", b"2")
    assert await async_map.count() == 2

    await async_map.put(b"32", b"32")
    assert await async_map.count() == 3

    await async_map.pop(b"2")
    assert await async_map.count() == 2

    await async_map.clear()
    assert await async_map.count() == 0


@pytest.mark.asyncio
async def test_empty(async_map):
    await async_map.clear()
    assert await async_map.empty()
    assert await async_map.count() == 0

    await async_map.put(b"1", b"1")
    assert not await async_map.empty()
    assert await async_map.count() != 0

    await async_map.pop(b"1")
    assert await async_map.empty()
    assert await async_map.count() == 0


@pytest.mark.asyncio
async def test_get_all(async_map):
    await async_map.clear()

    data_in = {
        b"7": b"777",
        b"8": b"123",
        b"9": b"321",
    }

    await async_map.put_all(data_in)

    data_out = {}
    async for key, value in async_map:
        data_out[key] = value

    assert data_in == data_out


@pytest.mark.parametrize("entries_num", [1024, 1025, 2000, 2048, 2049])
@pytest.mark.asyncio
async def test_get_all_big(async_map, entries_num):
    await async_map.clear()

    data_in = {f"{i}".encode("utf-8"): f"{i*2}".encode("utf-8") for i in range(1_025)}

    await async_map.put_all(data_in)

    data_out = {k: v async for k, v in async_map}
    assert data_in == data_out

# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import logging

import pytest

from pygridgain import AsyncClient
from tests.util import check_cluster_started, server_addresses_basic, start_cluster_gen

TEST_PAGE_SIZE = 32


@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


@pytest.fixture(autouse=True, scope="session")
def ensure_cluster_started():
    if not check_cluster_started():
        yield from start_cluster_gen()
    else:
        yield None


@pytest.fixture()
async def async_client():
    client = AsyncClient(address=server_addresses_basic[0])
    await client.connect()
    yield client
    await client.close()


@pytest.fixture()
def original_name(request):
    return request.node.originalname

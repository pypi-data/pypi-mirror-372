# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import os
from typing import Optional

import pytest

from pygridgain import AsyncClient, IgniteError, SSLConfig
from tests.util import (
    get_test_dir,
    server_addresses_basic,
    server_addresses_ssl_basic,
    server_addresses_ssl_client_auth,
)


def create_ssl_config(ssl_key: Optional[str], ssl_cert: Optional[str], ssl_ca: Optional[str]):
    ssl_dir_path = os.path.join(get_test_dir(), "ssl")

    return SSLConfig(
        key_file=os.path.join(ssl_dir_path, ssl_key) if ssl_key else None,
        cert_file=os.path.join(ssl_dir_path, ssl_cert) if ssl_cert else None,
        ca_file=os.path.join(ssl_dir_path, ssl_ca) if ssl_ca else None,
    )


@pytest.mark.asyncio
async def test_connection_success():
    ssl_cfg = create_ssl_config("client.pem", "client.pem", "ca.pem")
    async with AsyncClient(address=server_addresses_ssl_basic, ssl_config=ssl_cfg, connection_timeout=1.0) as client:
        assert client is not None


@pytest.mark.asyncio
async def test_connection_unknown():
    ssl_cfg = create_ssl_config("client_unknown.pem", "client_unknown.pem", "ca.pem")
    async with AsyncClient(address=server_addresses_ssl_basic, ssl_config=ssl_cfg, connection_timeout=1.0) as client:
        assert client is not None


test_data = [
    (server_addresses_ssl_client_auth, create_ssl_config("client_unknown.pem", "client_unknown.pem", "ca.pem")),
    (server_addresses_ssl_basic, None),
    (server_addresses_basic, create_ssl_config("client.pem", "client.pem", "ca.pem")),
    (server_addresses_ssl_client_auth, create_ssl_config(None, None, "ca.pem")),
    (server_addresses_ssl_client_auth, create_ssl_config("client.pem", "client.pem", "non_existing_ca.pem")),
    (server_addresses_ssl_client_auth, create_ssl_config("non_existing_key.pem", "client.pem", "ca.pem")),
    (server_addresses_ssl_client_auth, create_ssl_config("client.pem", "non_existing_cert.pem", "ca.pem")),
]


@pytest.mark.parametrize("address,ssl_cfg", test_data)
@pytest.mark.asyncio
async def test_connection_reject(address, ssl_cfg):
    with pytest.raises(IgniteError) as err:
        async with AsyncClient(address=address, ssl_config=ssl_cfg, connection_timeout=1.0):
            pass
    assert err.match("Failed to connect to the cluster")

# Copyright (C) GridGain Systems. All Rights Reserved.
# _________        _____ __________________        _____
# __  ____/___________(_)______  /__  ____/______ ____(_)_______
# _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
# / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
# \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/
import asyncio
import os
import signal
import subprocess
import time

import psutil

from pygridgain import AsyncClient, EndPoint, IgniteError

server_host = os.getenv("IGNITE_CLUSTER_HOST", "127.0.0.1")
server_addresses_invalid = [EndPoint(server_host, 10000)]
server_addresses_basic = [EndPoint(server_host, 10942), EndPoint(server_host, 10943)]
server_addresses_ssl_basic = [EndPoint(server_host, 10944)]
server_addresses_ssl_client_auth = [EndPoint(server_host, 10945)]
server_addresses_all = server_addresses_basic + server_addresses_ssl_basic + server_addresses_ssl_client_auth


def wait_for_condition(condition, interval=0.1, timeout=10, error=None):
    start = time.time()
    res = condition()

    while not res and time.time() - start < timeout:
        time.sleep(interval)
        res = condition()

    if res:
        return True

    if error is not None:
        raise RuntimeError(error)

    return False


def is_windows():
    return os.name == "nt"


def get_test_dir():
    return os.path.dirname(os.path.realpath(__file__))


def get_proj_dir():
    return os.path.abspath(os.path.join(get_test_dir(), "..", "..", "..", "..", ".."))


def get_ignite_dirs():
    ignite_home = os.getenv("IGNITE_HOME")
    if ignite_home is not None:
        yield ignite_home

    yield get_proj_dir()


def get_ignite_runner():
    ext = ".bat" if is_windows() else ""
    for ignite_dir in get_ignite_dirs():
        runner = os.path.join(ignite_dir, "gradlew" + ext)
        print("Probing platform node runner at '{0}'...".format(runner))
        if os.path.exists(runner):
            return runner

    raise RuntimeError(
        "Ignite not found. Please make sure your IGNITE_HOME environment variable points to a directory " "with a valid Ignite instance"
    )


def kill_process_tree(pid):
    if is_windows():
        subprocess.call(["taskkill", "/F", "/T", "/PID", str(pid)])
    else:
        children = psutil.Process(pid).children(recursive=True)
        for child in children:
            os.kill(child.pid, signal.SIGKILL)
        os.kill(pid, signal.SIGKILL)


# noinspection PyBroadException
async def check_server_started_async(addr: EndPoint) -> bool:
    try:
        async with AsyncClient(address=addr, connection_timeout=1.0) as _:
            pass
    except IgniteError:
        return False
    return True


def check_server_started(addr: EndPoint) -> bool:
    return asyncio.run(check_server_started_async(addr))


def check_cluster_started() -> bool:
    for addr in server_addresses_basic:
        if not check_server_started(addr):
            return False
    return True


def start_cluster(debug=False, jvm_opts="") -> subprocess.Popen:
    runner = get_ignite_runner()

    env = os.environ.copy()

    env["JVM_OPTS"] = env.get("JVM_OPTS", "") + jvm_opts

    if debug:
        env["JVM_OPTS"] = (
            env.get("JVM_OPTS", "") + "-Djava.net.preferIPv4Stack=true -Xdebug -Xnoagent -Djava.compiler=NONE "
            "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 "
        )

    ignite_cmd = [
        runner,
        ":ignite-runner:runnerPlatformTest",
        "--no-daemon",
        "-x",
        "compileJava",
        "-x",
        "compileTestFixturesJava",
        "-x",
        "compileIntegrationTestJava",
        "-x",
        "compileTestJava",
    ]

    print("Starting test node runner:", ignite_cmd)

    ignite_dir = next(get_ignite_dirs())
    if ignite_dir is None:
        raise RuntimeError("Can not resolve an Ignite project directory")

    cluster = subprocess.Popen(ignite_cmd, env=env, cwd=ignite_dir)

    for addr in server_addresses_basic:
        started = wait_for_condition(lambda: check_server_started(addr), timeout=180)
        if not started:
            kill_process_tree(cluster.pid)
            raise RuntimeError("Failed to start test cluster: timeout while trying to connect")

    return cluster


def start_cluster_gen(debug=False):
    srv = start_cluster(debug=debug)
    try:
        yield srv
    finally:
        kill_process_tree(srv.pid)

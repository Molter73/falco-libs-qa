import pytest
import subprocess
import docker
import os
from time import sleep
from sinspqa import SINSP_LOG_PATH, LOGS_PATH
from sinspqa.sinsp import is_ebpf


@pytest.fixture(scope="session", autouse=True)
def load_module():
    """
    Loads and unloads the scap.ko module to be used by the integration tests.
    """
    if is_ebpf():
        # Runnning with the ebpf probe
        yield
        return

    subprocess.run(args=["insmod", "/driver/scap.ko"]).check_returncode()
    yield
    subprocess.run(["rmmod", "scap"]).check_returncode()


@pytest.fixture(scope="session", autouse=True)
def docker_client():
    """
    Create a docker client to be used by the tests.

    Returns:
        A docker.DockerClient object created from the environment the tests run on.
    """
    return docker.from_env()


@pytest.fixture(scope="module")
def tester_id(docker_client):
    """
    Get the truncated ID of the test runner.

    Returns:
        A 12 character string with the ID.
    """
    return docker_client.containers.get("falco-tester").id[:12]


@pytest.fixture(scope="module")
def sinsp(request, docker_client):
    """
    Run a container with the `sinsp-example`.

    Parameters:
        docker_client (docker.DockerClient): A docker client used to create the container.

    Returns:
        A docker.Container running the `sinsp-example` binary.
    """
    mounts = [
        docker.types.Mount("/dev", "/dev", type="bind",
                           consistency="delegated", read_only=True)
    ]

    environment = {}

    if is_ebpf():
        environment["BPF_PROBE"] = os.environ.get("BPF_PROBE")

    sinsp = docker_client.containers.run("sinsp-example:latest",
                                         request.param,
                                         detach=True,
                                         privileged=True,
                                         mounts=mounts,
                                         environment=environment)
    sleep(1)  # Wait for sinsp to start capturing
    yield sinsp
    sinsp.stop()

    # Dump all logs to a file for the report.
    with open(SINSP_LOG_PATH, "w") as f:
        f.write(sinsp.logs().decode("ascii"))

    sinsp.remove(force=True)


@pytest.fixture(scope="function")
def nginx_container(docker_client):
    container = docker_client.containers.run(
        "nginx:1.14-alpine",
        detach=True
    )
    yield container
    container.stop()

    logs = container.logs().decode('ascii')
    if logs:
        with open(os.path.join(LOGS_PATH, 'nginx.log'), 'w') as f:
            f.write(logs)

    container.remove()


@pytest.fixture(scope="function")
def curl_container(docker_client):
    container = docker_client.containers.run(
        "pstauffer/curl:latest",
        ["sleep", "300"],
        detach=True
    )
    yield container
    container.stop()

    logs = container.logs().decode('ascii')
    if logs:
        with open(os.path.join(LOGS_PATH, 'curl.log'), 'w') as f:
            f.write(logs)

    container.remove()


def pytest_html_report_title(report):
    report.title = "sinsp integration tests"


def dump_logs(pytest_html, extra):
    for file in os.listdir(LOGS_PATH):
        full_path = os.path.join(LOGS_PATH, file)
        if not os.path.isfile(full_path):
            continue

        with open(full_path, 'r', errors='replace') as f:
            logs = f.read()
            extra.append(pytest_html.extras.text(logs, name=file))

        # Remove file so it doesn't bleed to following tests
        os.remove(full_path)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "teardown":
        dump_logs(pytest_html, extra)

    report.extra = extra

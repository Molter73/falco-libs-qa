import pytest
import subprocess
import docker
import os
from time import sleep
from sinspqa import SINSP_LOG_PATH


@pytest.fixture(scope="session", autouse=True)
def load_module():
    """
    Loads and unloads the scap.ko module to be used by the integration tests.
    """
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


@pytest.fixture()
def sinsp(docker_client):
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
    sinsp = docker_client.containers.run("sinsp-example:latest",
                                         ["-f", "evt.category=process and evt.type=execve"],
                                         detach=True,
                                         privileged=True,
                                         mounts=mounts)
    sleep(1)  # Wait for sinsp to start capturing
    yield sinsp
    sinsp.stop()

    # Dump all logs to a file for the report.
    with open(SINSP_LOG_PATH, "w") as f:
        f.write(sinsp.logs().decode("ascii"))

    sinsp.remove(force=True)


def pytest_html_report_title(report):
    report.title = "sinsp integration tests"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "teardown":
        if os.path.isfile(SINSP_LOG_PATH):
            with open(SINSP_LOG_PATH, "r", errors='replace') as f:
                logs = f.read()
                extra.append(pytest_html.extras.text(logs, name="sinsp.log"))

    report.extra = extra

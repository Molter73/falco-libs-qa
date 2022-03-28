import pytest
import subprocess
import docker
from time import sleep


@pytest.fixture(scope="session", autouse=True)
def load_module():
    subprocess.run(args=["insmod", "/driver/scap.ko"]).check_returncode()
    yield
    subprocess.run(["rmmod", "scap"]).check_returncode()


@pytest.fixture()
def docker_client():
    return docker.from_env()


@pytest.fixture()
def sinsp(docker_client):
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
    sinsp.remove(force=True)

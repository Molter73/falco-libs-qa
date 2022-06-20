import pytest
from sinspqa.sinsp import assert_events


sinsp_filters = [
    ["-f", "evt.category=process and not container.id=host"]
]


@pytest.fixture(scope="function")
def nginx(docker_client):
    container = docker_client.containers.run(
        "nginx:1.14-alpine",
        detach=True,
        auto_remove=True
    )
    yield container
    container.stop()


@pytest.mark.parametrize("sinsp", sinsp_filters, indirect=True)
def test_process(sinsp, nginx):
    container_id = nginx.id[:12]

    nginx.exec_run("sleep 5")
    nginx.exec_run("sh -c ls")

    expected_events = [
        {
            'container.id': container_id,
            'evt.args': 'filename=/usr/sbin/nginx ',
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'runc',
            'proc.cmdline': 'runc:[1:CHILD] init',
        }, {
            'container.id': container_id,
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'nginx',
            'proc.cmdline': 'nginx -g daemon off;'
        }, {
            'container.id': container_id,
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'sleep',
            'proc.cmdline': 'sleep 5'
        }, {
            'container.id': container_id,
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'sh',
            'proc.cmdline': 'sh -c ls'
        }
    ]

    assert_events(expected_events, sinsp)

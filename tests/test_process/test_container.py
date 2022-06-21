import pytest
from sinspqa.sinsp import assert_events
from sinspqa.docker import get_container_id


sinsp_filters = [
    ["-f", "evt.category=process and not container.id=host"]
]


containers = [{
    'nginx': {
        'image': 'nginx:1.14-alpine',
    }
}]


@pytest.mark.parametrize("sinsp", sinsp_filters, indirect=True)
@pytest.mark.parametrize("run_containers", containers, indirect=True)
def test_exec_in_container(sinsp, run_containers):
    nginx_container = run_containers['nginx']

    container_id = get_container_id(nginx_container)

    nginx_container.exec_run("sleep 5")
    nginx_container.exec_run("sh -c ls")

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

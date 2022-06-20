import pytest
import subprocess
from sinspqa.sinsp import assert_events


sinsp_filters = [
    ["-f", "evt.category=process and evt.type=execve"]
]


@pytest.mark.parametrize("sinsp", sinsp_filters, indirect=True)
def test_process(sinsp, container_id):
    """
    Runs a simple test where a bash script is executed and a corresponding sinsp event is found in the provided
    container's logs

    Parameters:
        sinsp (docker.Container): A detached container running the `sinsp-example` binary
    """
    expected_events = [
        {
            'container.id': container_id,
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'cat',
            'proc.cmdline': 'cat /tmp/test.txt'
        }, {
            'container.id': container_id,
            'evt.category': 'process',
            'evt.type': 'execve',
            'proc.exe': 'rm',
            'proc.cmdline': 'rm -f /tmp/test.txt'
        }
    ]

    subprocess.run("./test_sample.sh")

    assert_events(expected_events, sinsp)

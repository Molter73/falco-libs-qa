import pytest
import subprocess
from sinspqa.sinsp import assert_events


def test_process(sinsp):
    """
    Runs a simple test where a bash script is executed and a corresponding sinsp event is found in the provided
    container's logs

    Parameters:
        sinsp (docker.Container): A detached container running the `sinsp-example` binary
    """
    expected_events = [
        {
            'is_host': False,
            'cat': 'PROCESS',
            'type': 'execve',
            'exe': '/usr/bin/cat',
            'cmd': 'cat /tmp/test.txt'
        }, {
            'is_host': False,
            'cat': 'PROCESS',
            'type': 'execve',
            'exe': '/usr/bin/rm',
            'cmd': 'rm -f /tmp/test.txt'
        }
    ]

    subprocess.run("./test_sample.sh")

    assert_events(expected_events, sinsp)

import pytest
import subprocess
from sinspqa.sinsp import assert_events, is_ebpf


sinsp_filters = [
    ["-f", "evt.category=process and evt.type=execve"]
]


@pytest.mark.parametrize("sinsp", sinsp_filters, indirect=True)
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
            'cmd': 'cat /tmp/test.txt' if not is_ebpf() else "cat"
        }, {
            'is_host': False,
            'cat': 'PROCESS',
            'type': 'execve',
            'exe': '/usr/bin/rm',
            'cmd': 'rm -f /tmp/test.txt' if not is_ebpf() else "rm"
        }
    ]

    subprocess.run("./test_sample.sh")

    assert_events(expected_events, sinsp)

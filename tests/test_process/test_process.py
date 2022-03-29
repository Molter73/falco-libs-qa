import pytest
import subprocess
from sinspqa.sinsp import SinspStreamer, parse_log, validate_event


def test_process(sinsp):
    """
    Runs a simple test where a bash script is executed and a corresponding sinsp event is found in the provided
    container's logs

    Parameters:
        sinsp (docker.Container): A detached container running the `sinsp-example` binary
    """
    success = False
    expected_event = {
        'is_host': False,
        'cat': 'PROCESS',
        'type': 'execve',
        'exe': 'test_sample.sh',
        'cmd': 'test_sample.sh bash ./test_sample.sh'
    }

    reader = SinspStreamer(sinsp)

    subprocess.run("./test_sample.sh")

    for log in reader.read():
        if validate_event(expected_event, parse_log(log)):
            success = True
            break

    assert success

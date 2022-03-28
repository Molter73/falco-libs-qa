import pytest
import subprocess
from sinspqa.sinsp import SinspStreamer, parse_log, validate_event


def test_process(sinsp):
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

import pytest
import re
from sinspqa import sinsp, event_generator
from sinspqa.sinsp import assert_events, SinspField

sinsp_filters = ["-f", "evt.is_open_write=true and fd.typechar='f' and fd.num>=0"]


def create_containers(syscall):
    return {
        'sinsp': sinsp.container_spec(args=sinsp_filters),
        'generator': event_generator.container_spec(syscall),
    }


def create_expected_arg(directory):
    return fr'^fd=3\(<f>{re.escape(directory)}\/created-by-event-generator\) dirfd=-100\(AT_FDCWD\) name={re.escape(directory)}\/created-by-event-generator flags=4358\(O_TRUNC\|O_CREAT\|O_WRONLY\|O_CLOEXEC\) mode=0755 dev=.* ino=\d+ $'


containers = [
    create_containers('syscall.WriteBelowEtc')
]

expected_args = [
    create_expected_arg('/etc')
]

parameters = [
    (create_containers('syscall.WriteBelowEtc'), create_expected_arg('/etc')),
    (create_containers('syscall.WriteBelowBinaryDir'), create_expected_arg('/bin')),
    (create_containers('syscall.CreateFilesBelowDev'), create_expected_arg('/dev')),
    (create_containers('syscall.WriteBelowRpmDatabase'), create_expected_arg('/var/lib/rpm')),
]


@pytest.mark.parametrize('run_containers,expected_arg', parameters, indirect=['run_containers'])
def test_file_writes(run_containers, expected_arg):
    sinsp_container = run_containers['sinsp']
    generator_container = run_containers['generator']
    generator_container.wait()

    expected_events = [
        {
            "evt.args": SinspField.regex_field(expected_arg),
            "evt.cpu": SinspField.numeric_field(),
            "evt.dir": "<",
            "evt.num": SinspField.numeric_field(),
            "evt.time": SinspField.numeric_field(),
            "evt.type": SinspField.regex_field(r'^(?:open|openat|openat2)$'),
            "proc.name": "event-generator",
            "thread.tid": SinspField.numeric_field()
        }
    ]

    assert_events(expected_events, sinsp_container)

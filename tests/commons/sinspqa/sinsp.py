from datetime import datetime
from time import sleep
import os
import json
import docker
import re
from enum import Enum

SINSP_TAG = os.environ.get('SINSP_TAG', 'latest')


class SinspStreamer:
    """
    Allows streaming of `sinsp-example` logs for analysis.
    """

    def __init__(self, container, timeout=10):
        """
        Parameters:
            container (docker.Container): A container object to stream logs from.
            timeout (int): The maximum amount of time the streamer will read logs from the container.
        """
        self.container = container
        self.timeout = timeout
        self.last_timestamp = None

    def read(self):
        """
        Reads logs from a container and returns them as a generator.

        Returns:
            A string holding a single log line from the container.
        """
        start = datetime.now()

        while True:
            sleep(0.2)

            for raw_log in self.container.logs(stream=True,
                                               follow=False,
                                               timestamps=True,
                                               since=self.last_timestamp):
                self.last_timestamp, log = self.extract_log(raw_log)
                yield log

            if (datetime.now() - start).total_seconds() > self.timeout:
                break

    def extract_log(self, raw_log):
        """
        Split the docker log timestamp from the log line and return them

        Parameters:
            raw_log (binary): The log line as extracted from the logs call.

        Returns:
            A tuple holding a datetime object with the timestamp and a string with the log line.
        """
        decoded_log = raw_log.decode("ascii").strip()
        split_log = decoded_log.split(" ")
        return datetime.strptime(split_log[0][:-4], "%Y-%m-%dT%H:%M:%S.%f"), " ".join(split_log[1:])


class SinspFieldTypes(Enum):
    STRING = 0
    REGEX = 1


class SinspField:
    """
    Stores the value expected in a field output by sinsp-example.
    """
    def __init__(self, value, value_type=SinspFieldTypes.STRING):
        self.value_type = value_type

        if self.value_type == SinspFieldTypes.REGEX:
            self.value = re.compile(value)
        else:
            self.value = value

    def compare(self, other: str) -> bool:
        if self.value_type == SinspFieldTypes.REGEX:
            return self.value.match(other)

        return self.value == other

    def __repr__(self):
        if self.value_type == SinspFieldTypes.REGEX:
            return f"r'{self.value.pattern}'"
        else:
            return self.value

    def numeric_field():
        return SinspField(r'^\d+$', SinspFieldTypes.REGEX)

    def regex_field(regex: str):
        return SinspField(regex, SinspFieldTypes.REGEX)


def parse_log(log):
    """
    Parses a log line from the `sinsp-example` binary.

    Parameters:
        log (str): A string holding a single log line from `sinsp-example``

    Returns:
        A dictionary holding all the captured values for the event, except the timestamp.
    """
    try:
        return json.loads(log)
    except json.JSONDecodeError as e:
        print(f'Failed to parse JSON: {e}')
        print(log)
        return None


def validate_event(expected_fields, event):
    """
    Checks all `expected_fields` are in the `event`

    Parameters:
        expected_fields (dict): A dictionary holding the values expected in the event.
        event (dict): A sinsp event parsed by calling `parse_log`

    Returns:
        True if all `expected_fields` are in the event and have matching values, False otherwise.
    """
    if event is None:
        return False

    for k in expected_fields:
        if k not in event:
            return False

        expected = expected_fields[k]

        if isinstance(expected, str) or expected is None:
            if expected == event[k]:
                continue
            return False

        if not expected.compare(str(event[k])):
            return False

    return True


def assert_events(expected_events, container):
    reader = SinspStreamer(container)

    for event in expected_events:
        success = False

        for log in reader.read():
            if not log:
                continue

            if validate_event(event, parse_log(log)):
                success = True
                break
        assert success, f"Did not receive expected event: {event}"


def is_ebpf():
    """
    Checks if the tests are being run with eBPF.

    Returns:
        True if the test is running with the eBPF driver, False otherwise.
    """
    return "BPF_PROBE" in os.environ


def sinsp_validation(container: docker.models.containers.Container) -> (bool, str):
    container.reload()
    exit_code = container.attrs['State']['ExitCode']
    if exit_code != 0:
        return False, f'container exited with code {exit_code}'

    return True, None


def container_spec(image=f'quay.io/mmoltras/sinsp-example:{SINSP_TAG}', args=[]):
    mounts = [
        docker.types.Mount("/dev", "/dev", type="bind",
                           consistency="delegated", read_only=True)
    ]
    environment = {}

    if is_ebpf():
        environment["BPF_PROBE"] = os.environ.get("BPF_PROBE")
        args.extend([
            '-e', 'bpf',
            '-b', os.environ['BPF_PROBE']
        ])

    return {
        'image': image,
        'args': args,
        'mounts': mounts,
        'env': environment,
        'privileged': True,
        'init_wait': 2,
        'post_validation': sinsp_validation,
    }

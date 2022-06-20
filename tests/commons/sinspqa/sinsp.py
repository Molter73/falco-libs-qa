from datetime import datetime
from time import sleep
import os
import json


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


def parse_log(log):
    """
    Parses a log line from the `sinsp-example` binary.

    Parameters:
        log (str): A string holding a single log line from `sinsp-example``

    Returns:
        A dictionary holding all the captured values for the event, except the timestamp.
    """
    return json.loads(log)


def validate_event(expected_fields, event):
    """
    Checks all `expected_fields` are in the `event`

    Parameters:
        expected_fields (dict): A dictionary holding the values expected in the event.
        event (dict): A sinsp event parsed by calling `parse_log`

    Returns:
        True if all `expected_fields` are in the event and have matching values, False otherwise.
    """
    for k in expected_fields:
        if k not in event:
            return False

        if event[k] != expected_fields[k]:
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

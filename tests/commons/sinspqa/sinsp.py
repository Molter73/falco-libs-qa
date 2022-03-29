import docker
from datetime import datetime
from time import sleep
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

    def read(self):
        """
        Reads logs from a container and returns them as a generator.

        Returns:
            A string holding a single log line from the container.
        """
        logs = self.container.logs(stream=True, follow=False)
        start = datetime.now()

        while True:
            sleep(0.2)

            for log in logs:
                yield log.decode("ascii").strip()

            if (datetime.now() - start).total_seconds() > self.timeout:
                break



def parse_log(log):
    """
    Parses a log line from the `sinsp-example` binary.

    Parameters:
        log (str): A string holding a single log line from `sinsp-example``

    Returns:
        A dictionary holding all the captured values for the event, except the timestamp.
    """
    output = {}

    # Discard the time stamp
    fields = log.split("[")[2:]
    fields = "[".join(fields).split(":")

    # Handle host vs. container ID
    if fields[0] == "[HOST]":
        output["is_host"] = True
    else:
        output["is_host"] = False
        output["container_id"] = fields[0][1:-1]

    for field in fields[1:]:
        f = field.split("=")
        output[f[0][1:].lower()] = f[1][:-1]

    return output


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

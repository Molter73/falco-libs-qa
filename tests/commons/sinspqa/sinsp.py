import docker
from datetime import datetime
from time import sleep
import json


class SinspStreamer:
    def __init__(self, container, timeout=10):
        self.container = container
        self.timeout = timeout

    def read(self):
        logs = self.container.logs(stream=True, follow=False)
        start = datetime.now()

        while True:
            sleep(0.2)

            for log in logs:
                yield log.decode("ascii").strip()

            if (datetime.now() - start).total_seconds() > self.timeout:
                break



def parse_log(log):
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
    print(expected_fields, event)
    for k in expected_fields:
        if k not in event:
            return False

        if event[k] != expected_fields[k]:
            return False

    return True

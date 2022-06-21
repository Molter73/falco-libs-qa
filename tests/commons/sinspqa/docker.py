from docker.models.containers import Container


def get_container_id(container: Container) -> str:
    return container.id[:12]


def get_network_data(container: Container) -> str:
    container.reload()

    ip = container.attrs['NetworkSettings']['IPAddress']
    # Try and get a single port number
    ports = container.attrs['NetworkSettings']['Ports']
    ports = list(ports.keys())

    port = ports[0].split('/')[0] if len(ports) else None

    return f'{ip}:{port}' if port else ip

from __future__ import annotations

from urllib.parse import urlsplit
from uuid import uuid4

from remotivelabs.broker.exceptions import BrokerError

DEFAULT_SECURE_PORT = 443
DEFAULT_INSECURE_PORT = 50051


def get_connection_details_from_url(url: str) -> tuple[str, bool]:
    url_parts = urlsplit(url)
    if not url_parts.hostname:
        raise BrokerError(f"invalid hostname: {url}")

    use_tls = url_parts.scheme == "https"

    default_port = DEFAULT_SECURE_PORT if use_tls else DEFAULT_INSECURE_PORT
    port = url_parts.port if url_parts.port else default_port

    host = url_parts.hostname + ":" + str(port)
    return (host, use_tls)


def create_random_client_id() -> str:
    return str(uuid4())

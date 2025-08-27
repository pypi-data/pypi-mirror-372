import urllib
import urllib.parse

from openstack.connection import Connection


def get_endpoint(connection: Connection, service_type: str, interface: str) -> str:
    endpoint = connection.endpoint_for(service_type=service_type, interface=interface)

    parsed_endpoint = urllib.parse.urlparse(endpoint)

    new_hostname = urllib.parse.urlparse(connection.auth["auth_url"]).hostname

    port = parsed_endpoint.port

    ret = urllib.parse.urlunparse(
        parsed_endpoint._replace(netloc=f"{new_hostname}:{port}")._replace(
            scheme="https"
        )
    )

    return ret


def get_endpoints(
    connection: Connection, service_type: str, interface: str
) -> list[str]:
    endpoint = connection.endpoint_for(service_type=service_type, interface=interface)

    parsed_endpoint = urllib.parse.urlparse(endpoint)

    new_hostname = urllib.parse.urlparse(connection.auth["auth_url"]).hostname

    port = parsed_endpoint.port

    http_ret = urllib.parse.urlunparse(
        parsed_endpoint._replace(netloc=f"{new_hostname}:{port}")._replace(
            scheme="http"
        )
    )

    https_ret = urllib.parse.urlunparse(
        parsed_endpoint._replace(netloc=f"{new_hostname}:{port}")._replace(
            scheme="https"
        )
    )

    return [https_ret, http_ret]

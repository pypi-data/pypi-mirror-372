from openstack.connection import Connection
from openstack.identity.v3.service import Service
from openstack.load_balancer.v2.load_balancer import LoadBalancer


import osi_dump.util.openstack_util as os_util


def get_load_balancer_flavor(connection: Connection, flavor_id: str) -> dict: 

    if not flavor_id: 
        return None

    octavia_endpoints = os_util.get_endpoints(
        connection=connection, service_type="load-balancer", interface="public"
    )

    response = None

    for endpoint in octavia_endpoints:
        try:
            url = f"{endpoint}/v2.0/lbaas/flavors/{flavor_id}"
            response = connection.session.get(url)
            if response.status_code == 200:
                break
        except Exception as e:
            print(e)

    if response is None:
        return None
    
    data = response.json()

    return data["flavor"]

def get_load_balancers(connection: Connection) -> list[LoadBalancer]:
    # octavia_endpoint = os_util.get_endpoint(
    #     connection=connection, service_type="load-balancer", interface="public"
    # )

    octavia_endpoints = os_util.get_endpoints(
        connection=connection, service_type="load-balancer", interface="public"
    )

    response = None

    for endpoint in octavia_endpoints:
        try:
            url = f"{endpoint}/v2.0/lbaas/loadbalancers"
            response = connection.session.get(url)
            if response.status_code == 200:
                break
        except Exception as e:
            print(e)

    if response is None:
        return None

    data = response.json()

    return data["loadbalancers"]


def get_amphoraes(connection: Connection, load_balancer_id: str) -> list[dict]:

    # octavia_endpoint = os_util.get_endpoint(
    #     connection=connection, service_type="load-balancer", interface="public"
    # )

    octavia_endpoints = os_util.get_endpoints(
        connection=connection, service_type="load-balancer", interface="public"
    )

    response = None

    for endpoint in octavia_endpoints:
        try:
            url = f"{endpoint}/v2/octavia/amphorae?load_balancer_id={load_balancer_id}&fields=status&fields=compute_id&fields=compute_flavor&fields=role"
            response = connection.session.get(url)
            if response.status_code == 200:
                break
        except Exception as e:
            print(e)

    if response is None:
        return None

    data = response.json()

    amphoraes = data["amphorae"]

    amphoraes = [dict(sorted(amphorae.items())) for amphorae in amphoraes]

    return amphoraes

import logging

from openstack.connection import Connection
from openstack.identity.v3.service import Service
from openstack.load_balancer.v2.load_balancer import LoadBalancer

import osi_dump.util.openstack_util as os_util

logger = logging.getLogger(__name__)


def get_users(connection: Connection):

    keystone_endpoints = os_util.get_endpoints(connection=connection, service_type="identity", interface="public")

    for keystone_endpoint in keystone_endpoints:
        try:
            if "v3" not in keystone_endpoint: 
                url = f"{keystone_endpoint}/v3/users"
            else: 
                url = f"{keystone_endpoint}/users"
                
            response = connection.session.get(url)
            if response.status_code == 200:
                break
        except Exception as e: 
            logger.info(e)


    if response is None:
        return []

    return response.json()["users"]

def get_role_assignments(connection: Connection): 
    keystone_endpoint = connection.endpoint_for(service_type="identity", interface="public")
    
    logger.info(keystone_endpoint)
    
    try:
        if "v3" not in keystone_endpoint: 
            url = f"{keystone_endpoint}/v3/role_assignments?include_names"
        else: 
            url = f"{keystone_endpoint}/role_assignments?include_names"
            
        logger.info(url)
        response = connection.session.get(url)
    except Exception as e: 
        logger.info(e)
        
    if response is None: 
        return []
    
    return response.json()['role_assignments']    
    
    # keystone_endpoints = [connection.endpoint_for(service_type="keystone", interface="public")]
    
    # for endpoint in keystone_endpoints: 
    #     try: 
    #         url = f"{endpoint}/v3/role_assignments?include_names"
    #         response = connection.session.get(url)
    #         if response.status_code == 200: 
    #             break
    #     except Exception as e: 
    #         logger.info(e) 
    
    # if response is None: 
    #     return []
    
    # return response.json()['role_assignments']
    
import logging

import concurrent

from openstack.connection import Connection
from openstack.identity.v3.project import Project as OSProject
from openstack.load_balancer.v2.load_balancer import LoadBalancer as OSLoadBalancer

from osi_dump.importer.project.project_importer import ProjectImporter
from osi_dump.model.project import Project
import osi_dump.api.octavia as octavia_api
logger = logging.getLogger(__name__)


class OpenStackProjectImporter(ProjectImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_projects(self) -> list[Project]:
        """Import projects information from Openstack

        Raises:
            Exception: Raises exception if fetching project failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing projects for {self.connection.auth['auth_url']}")
        try:
            osload_balancers: list[OSLoadBalancer] = octavia_api.get_load_balancers(
                connection=self.connection
            )
        except Exception as e:
            raise Exception(
                f"Can not fetch load_balancers for {self.connection.auth['auth_url']} {e}"
            ) from e

        project_lb_dict = {}

        for osload_balancer in osload_balancers: 
            if project_lb_dict.get(osload_balancer["project_id"]):
                project_lb_dict[osload_balancer["project_id"]] += 1 
            else: 
                project_lb_dict[osload_balancer["project_id"]] = 1

        try:
            osprojects: list[OSProject] = list(self.connection.identity.projects())
        except Exception as e:
            raise Exception(
                f"Can not fetch projects for {self.connection.auth['auth_url']}"
            ) from e

        projects: list[Project] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_project_info, project, project_lb_dict)
                for project in osprojects
            ]
            for future in concurrent.futures.as_completed(futures):
                projects.append(future.result())

        logger.info(f"Imported projects for {self.connection.auth['auth_url']}")

        return projects

    def _get_project_info(self, project: OSProject, project_lb_dict: dict) -> Project:
        
        usage_instance=None
        quota_instance=None
        usage_ram=None
        quota_ram=None
        usage_vcpu=None
        quota_vcpu=None

        try:
            compute_quotas = self.connection.compute.get_quota_set(
                project.id, usage=True
            )

            usage_instance=compute_quotas.usage["instances"]
            quota_instance=compute_quotas.instances
            usage_ram=compute_quotas.usage["ram"]
            quota_ram=compute_quotas.ram
            usage_vcpu=compute_quotas.usage["cores"]
            quota_vcpu=compute_quotas.cores
        except Exception as e:
            logger.warning(f"Get compute quotas failed for {project.id} error: {e}")

        usage_volume=None
        quota_volume=None
        usage_snapshot=None
        quota_snapshot=None
        usage_storage=None
        quota_storage=None
        try:
            storage_quotas = self.connection.block_storage.get_quota_set(
                project.id, usage=True
            )
            usage_volume=storage_quotas.usage["volumes"]
            quota_volume=storage_quotas.volumes
            usage_snapshot=storage_quotas.usage["snapshots"]
            quota_snapshot=storage_quotas.snapshots
            usage_storage=storage_quotas.usage["gigabytes"]
            quota_storage=storage_quotas.gigabytes
        except Exception as e:
            logger.warning(f"Get storage quotas failed for {project.id} error: {e}")

        domain_name = None
        try:
            domain = self.connection.identity.get_domain(project.domain_id)
            domain_name = domain.name
        except Exception as e:
            logger.warning(f"Get domain failed for {project.domain_id} error: {e}")

        lb_count = project_lb_dict.get(project.id)

        project_ret = Project(
            project_id=project.id,
            project_name=project.name,
            domain_id=project.domain_id,
            domain_name=domain_name,
            enabled=project.is_enabled,
            parent_id=project.parent_id,
            usage_instance=usage_instance, 
            quota_instance=quota_instance,
            usage_ram=usage_ram,
            quota_ram=quota_ram, 
            usage_vcpu=usage_vcpu,
            quota_vcpu=quota_vcpu,
            usage_volume=usage_volume,
            quota_volume=quota_volume,
            usage_snapshot=usage_snapshot,
            quota_snapshot=quota_snapshot,
            usage_storage=usage_storage,
            quota_storage=quota_storage,
            load_balancer_count=lb_count
        )

        return project_ret

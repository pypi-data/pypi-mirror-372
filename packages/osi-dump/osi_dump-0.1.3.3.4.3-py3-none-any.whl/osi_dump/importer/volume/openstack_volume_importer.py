import logging

import concurrent

from openstack.connection import Connection

from openstack.block_storage.v3.volume import Volume as OSVolume

from osi_dump.importer.volume.volume_importer import VolumeImporter
from osi_dump.model.volume import Volume

logger = logging.getLogger(__name__)


class OpenStackVolumeImporter(VolumeImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_volumes(self) -> list[Volume]:
        """Import hypervisors information from Openstack

        Raises:
            Exception: Raises exception if fetching hypervisor failed

        Returns:
            list[Hypervisor]: _description_
        """

        logger.info(f"Importing volumes for {self.connection.auth['auth_url']}")

        try:
            osvolumes: list[OSVolume] = list(
                self.connection.block_storage.volumes(details=True, all_projects=True)
            )
        except Exception as e:
            raise Exception(
                f"Can not fetch volumes for {self.connection.auth['auth_url']}"
            ) from e

        volumes: list[Volume] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_volume_info, volume) for volume in osvolumes
            ]
            for future in concurrent.futures.as_completed(futures):
                volumes.append(future.result())

        logger.info(f"Imported volumes for {self.connection.auth['auth_url']}")

        return volumes

    def _get_volume_info(self, volume: OSVolume) -> Volume:

        snapshots = []
        try:
            snapshots = list(
                self.connection.block_storage.snapshots(
                    details=False, all_projects=True, volume_id=volume.id
                )
            )

            snapshots = [snapshot["id"] for snapshot in snapshots]

        except Exception as e:
            logger.warning(f"Fetching snapshots failed for {volume.id} error: {e}")

        ret_volume = Volume(
            volume_id=volume.id,
            volume_name=volume.name,
            project_id=volume.project_id,
            status=volume.status,
            attachments=[att["server_id"] for att in volume.attachments],
            type=volume.volume_type,
            size=volume.size,
            snapshots=snapshots,
            updated_at=volume.updated_at,
            created_at=volume.created_at,
        )

        return ret_volume

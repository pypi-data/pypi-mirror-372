import logging

import concurrent

from openstack.connection import Connection
from openstack.image.v2.image import Image as OSImage

from osi_dump.importer.image.image_importer import ImageImporter
from osi_dump.model.image import Image

logger = logging.getLogger(__name__)


class OpenStackImageImporter(ImageImporter):
    def __init__(self, connection: Connection):
        self.connection = connection

    def import_images(self) -> list[Image]:
        """Import instances information from Openstack

        Raises:
            Exception: Raises exception if fetching server failed

        Returns:
            list[Instance]: _description_
        """

        logger.info(f"Importing images for {self.connection.auth['auth_url']}")

        try:

            os_images: list[OSImage] = list(self.connection.list_images(show_all=True))
        except Exception as e:
            raise Exception(
                f"Can not fetch images for {self.connection.auth['auth_url']}"
            ) from e

        images: list[OSImage] = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._get_image_info, image) for image in os_images
            ]
            for future in concurrent.futures.as_completed(futures):
                images.append(future.result())

        logger.info(f"Imported images for {self.connection.auth['auth_url']}")

        return images

    def _get_image_info(self, os_image: OSImage) -> Image:

        try:
            properties: dict = os_image.properties

            properties.pop("owner_specified.openstack.md5", None)
            properties.pop("owner_specified.openstack.sha256", None)
            properties.pop("owner_specified.openstack.object", None)
            properties.pop("stores", None)
        except Exception as e: 
            logger.warn(f"properties for {os_image.id} is None")

        image = Image(
            image_id=os_image.id,
            disk_format=os_image.disk_format,
            min_disk=os_image.min_disk,
            min_ram=os_image.min_ram,
            image_name=os_image.name,
            owner=os_image.owner,
            properties=os_image.properties,
            protected=os_image.is_protected,
            status=os_image.status,
            os_distro=os_image.os_distro,
            size=os_image.size,
            virtual_size=os_image.virtual_size,
            visibility=os_image.visibility,
            created_at=os_image.created_at,
            updated_at=os_image.updated_at,
        )

        return image

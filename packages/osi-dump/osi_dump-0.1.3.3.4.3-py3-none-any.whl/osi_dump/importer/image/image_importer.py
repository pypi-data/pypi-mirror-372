from abc import ABC, abstractmethod

from osi_dump.model.image import Image


class ImageImporter(ABC):
    @abstractmethod
    def import_images(self) -> list[Image]:
        pass

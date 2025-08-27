from abc import ABC, abstractmethod


class ImageExporter(ABC):
    @abstractmethod
    def export_images(self, images, output_file: str):
        pass

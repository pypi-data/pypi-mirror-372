from typing import List, Mapping

from kognic.io.model.scene.abstract.base_frame import BaseFrame
from kognic.io.model.scene.resources.image import Image


class Frame(BaseFrame):
    images: List[Image]

    @property
    def resources(self) -> Mapping[str, Image]:
        return {i.resource_id: i for i in self.images}

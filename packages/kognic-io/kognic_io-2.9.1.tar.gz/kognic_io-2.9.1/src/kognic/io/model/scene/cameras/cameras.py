from typing import Mapping, Optional

from kognic.io.model.scene.abstract.base_scene import BaseScene
from kognic.io.model.scene.cameras.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData
from kognic.io.model.scene.resources import Image
from kognic.io.model.scene.sensor_specification import SensorSpecification


class Cameras(BaseScene):
    external_id: str
    frame: Frame
    sensor_specification: Optional[SensorSpecification] = None
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, Image]:
        return self.frame.resources

from typing import List, Mapping, Optional

from kognic.io.model.scene.abstract.base_scene import BaseScene
from kognic.io.model.scene.cameras_sequence.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData
from kognic.io.model.scene.resources import Image
from kognic.io.model.scene.sensor_specification import SensorSpecification


class CamerasSequence(BaseScene):
    external_id: str
    frames: List[Frame]
    sensor_specification: Optional[SensorSpecification] = None
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, Image]:
        mappings = [frame.resources for frame in self.frames]
        superset = {}
        for mapping in mappings:
            superset = {**superset, **mapping}
        return superset

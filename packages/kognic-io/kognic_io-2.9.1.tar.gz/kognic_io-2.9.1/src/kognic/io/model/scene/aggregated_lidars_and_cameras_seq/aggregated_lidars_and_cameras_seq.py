from typing import List, Mapping, Optional

from kognic.io.model.scene.abstract import BaseSceneWithIMUData
from kognic.io.model.scene.aggregated_lidars_and_cameras_seq.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData
from kognic.io.model.scene.resources.resource import Resource
from kognic.io.model.scene.sensor_specification import SensorSpecification


class AggregatedLidarsAndCamerasSequence(BaseSceneWithIMUData):
    external_id: str
    frames: List[Frame]
    calibration_id: str
    sensor_specification: Optional[SensorSpecification] = None
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, Resource]:
        mappings = [frame.resources for frame in self.frames]
        superset = {}
        for mapping in mappings:
            superset = {**superset, **mapping}
        return superset

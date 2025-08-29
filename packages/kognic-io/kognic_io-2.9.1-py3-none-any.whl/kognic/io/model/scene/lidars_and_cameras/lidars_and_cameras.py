from typing import Mapping, Optional

from kognic.io.model.scene.abstract import BaseSceneWithIMUData
from kognic.io.model.scene.lidars_and_cameras.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData
from kognic.io.model.scene.resources.resource import Resource
from kognic.io.model.scene.sensor_specification import SensorSpecification


class LidarsAndCameras(BaseSceneWithIMUData):
    external_id: str
    frame: Frame
    calibration_id: str
    sensor_specification: Optional[SensorSpecification] = None
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, Resource]:
        return self.frame.resources

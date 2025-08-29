from typing import Mapping

from kognic.io.model import PointCloud
from kognic.io.model.scene.abstract import BaseSceneWithIMUData
from kognic.io.model.scene.lidars.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData


class Lidars(BaseSceneWithIMUData):
    external_id: str
    frame: Frame
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, PointCloud]:
        return self.frame.resources

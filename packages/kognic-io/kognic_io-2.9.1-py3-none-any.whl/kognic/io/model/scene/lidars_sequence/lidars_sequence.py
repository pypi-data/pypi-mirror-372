from typing import List, Mapping

from kognic.io.model import PointCloud
from kognic.io.model.scene.abstract import BaseSceneWithIMUData
from kognic.io.model.scene.lidars_sequence.frame import Frame
from kognic.io.model.scene.metadata.metadata import MetaData


class LidarsSequence(BaseSceneWithIMUData):
    external_id: str
    frames: List[Frame]
    metadata: MetaData = MetaData()

    @property
    def resources(self) -> Mapping[str, PointCloud]:
        mappings = [frame.resources for frame in self.frames]
        superset = {}
        for mapping in mappings:
            superset = {**superset, **mapping}
        return superset

from abc import ABC

from kognic.io.model.scene.abstract.base_frame import BaseFrame
from kognic.io.model.scene.metadata.metadata import FrameMetaData


class SequenceFrame(BaseFrame, ABC):
    frame_id: str
    relative_timestamp: int
    metadata: FrameMetaData = FrameMetaData()

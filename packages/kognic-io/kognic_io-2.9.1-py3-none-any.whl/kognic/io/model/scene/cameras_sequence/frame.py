from typing import List, Mapping

from kognic.io.model.scene.abstract.sequence_frame import SequenceFrame
from kognic.io.model.scene.resources import Image, VideoFrame


class Frame(SequenceFrame):
    images: List[Image] = []
    video_frames: List[VideoFrame] = []

    @property
    def resources(self) -> Mapping[str, Image]:
        # Video is not included as of 2022-10; currently unused and unsupported.
        return {i.resource_id: i for i in self.images}

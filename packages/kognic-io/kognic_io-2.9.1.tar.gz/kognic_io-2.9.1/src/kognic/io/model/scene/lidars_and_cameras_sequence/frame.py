from typing import List, Mapping, Optional

from kognic.io.model.ego import EgoVehiclePose
from kognic.io.model.ego.utils import UnixTimestampNs
from kognic.io.model.scene.abstract.sequence_frame import SequenceFrame
from kognic.io.model.scene.resources import Image, PointCloud, VideoFrame


class Frame(SequenceFrame):
    point_clouds: List[PointCloud]
    images: List[Image] = []
    video_frames: List[VideoFrame] = []
    ego_vehicle_pose: Optional[EgoVehiclePose] = None
    unix_timestamp: Optional[UnixTimestampNs] = None

    @property
    def resources(self) -> Mapping[str, Image]:
        # Video is not included as of 2022-10; currently unused and unsupported.
        img_mappings = {i.resource_id: i for i in self.images}
        pc_mappings = {p.resource_id: p for p in self.point_clouds}
        return {**img_mappings, **pc_mappings}

from typing import List, Mapping, Optional

from kognic.io.model import UnixTimestampNs
from kognic.io.model.ego import EgoVehiclePose
from kognic.io.model.scene.abstract.sequence_frame import SequenceFrame
from kognic.io.model.scene.resources import PointCloud


class Frame(SequenceFrame):
    point_clouds: List[PointCloud]
    ego_vehicle_pose: Optional[EgoVehiclePose] = None
    unix_timestamp: Optional[UnixTimestampNs] = None

    @property
    def resources(self) -> Mapping[str, PointCloud]:
        return {p.resource_id: p for p in self.point_clouds}

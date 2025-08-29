from typing import List, Mapping, Optional

from kognic.io.model import UnixTimestampNs
from kognic.io.model.scene.abstract.base_frame import BaseFrame
from kognic.io.model.scene.resources.point_cloud import PointCloud


class Frame(BaseFrame):
    point_clouds: List[PointCloud]
    unix_timestamp: Optional[UnixTimestampNs] = None

    @property
    def resources(self) -> Mapping[str, PointCloud]:
        return {p.resource_id: p for p in self.point_clouds}

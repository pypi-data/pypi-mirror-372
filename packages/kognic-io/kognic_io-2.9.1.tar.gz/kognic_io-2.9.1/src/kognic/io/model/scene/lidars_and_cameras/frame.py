from typing import List, Mapping, Optional

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.ego.utils import UnixTimestampNs
from kognic.io.model.scene.resources.image import Image
from kognic.io.model.scene.resources.point_cloud import PointCloud


class Frame(BaseSerializer):
    point_clouds: List[PointCloud]
    images: List[Image]
    unix_timestamp: Optional[UnixTimestampNs] = None

    @property
    def resources(self) -> Mapping[str, Image]:
        img_mappings = {i.resource_id: i for i in self.images}
        pc_mappings = {p.resource_id: p for p in self.point_clouds}
        return {**img_mappings, **pc_mappings}

from typing import List, Optional

from kognic.io.model.base_serializer import BaseSerializer


class InputFromSceneRequest(BaseSerializer):
    scene_uuid: str
    annotation_types: List[str]
    project: str
    batch: Optional[str] = None

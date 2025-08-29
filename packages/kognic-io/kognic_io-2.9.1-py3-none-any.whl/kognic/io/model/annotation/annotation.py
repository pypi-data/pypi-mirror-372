from datetime import datetime
from typing import Optional

from kognic.io.model.base_serializer import BaseSerializer


class Annotation(BaseSerializer):
    input_uuid: str
    scene_uuid: str
    request_uid: str
    created: datetime
    content: Optional[dict] = None


class PartialAnnotation(BaseSerializer):
    input_uuid: str
    scene_uuid: str
    request_uid: str
    created: datetime
    uri: str

    def to_annotation(self, content: dict) -> Annotation:
        return Annotation(
            input_uuid=self.input_uuid,
            scene_uuid=self.scene_uuid,
            request_uid=self.request_uid,
            created=self.created,
            content=content,
        )

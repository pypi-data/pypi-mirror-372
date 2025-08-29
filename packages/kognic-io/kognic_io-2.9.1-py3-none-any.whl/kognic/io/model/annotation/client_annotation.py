from datetime import datetime
from typing import Optional

from deprecated import deprecated
from pydantic import Field

from kognic.io.model.base_serializer import BaseSerializer


class Annotation(BaseSerializer):
    scene_uuid: str = Field(alias="inputUuid")
    annotation_type: str
    created: datetime
    content: Optional[dict] = None

    @property
    @deprecated(reason="This is deprecated is favor of `scene_uuid`")
    def input_uuid(self) -> str:
        return self.scene_uuid


class PartialAnnotation(BaseSerializer):
    scene_uuid: str = Field(alias="inputUuid")
    annotation_type: str
    created: datetime
    uri: str

    @deprecated(reason="This is deprecated in favor of `scene_uuid`")
    def input_uuid(self) -> str:
        return self.scene_uuid

    def to_annotation(self, content: dict) -> Annotation:
        return Annotation(scene_uuid=self.scene_uuid, annotation_type=self.annotation_type, created=self.created, content=content)

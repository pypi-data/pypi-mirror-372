from datetime import datetime
from enum import Enum
from typing import List, Optional

from deprecated import deprecated
from pydantic import Field

from kognic.io.model.base_serializer import BaseSerializer


@deprecated(reason="This has been deprecated in favour of SceneStatus and will be removed in the future")
class InputStatus(str, Enum):
    Pending = "pending"
    Processing = "processing"
    Created = "created"
    Failed = "failed"
    InvalidatedBadContent = "invalidated:broken-input"
    InvalidatedSlamRerun = "invalidated:slam-rerun"
    InvalidatedDuplicate = "invalidated:duplicate"
    InvalidatedIncorrectlyCreated = "invalidated:incorrectly-created"


@deprecated(
    reason="This has been deprecated in favour of kognic.io.model.input.input.Input or kognic.io.model.scene.Scene and "
    "will be removed in the future"
)
class Input(BaseSerializer):
    scene_uuid: str = Field(alias="internalId")
    external_id: str
    batch: str = Field(alias="batchId")
    scene_type: str = Field(alias="inputType")
    status: InputStatus
    created: datetime
    annotation_types: List[str]
    calibration_id: Optional[str] = None
    view_link: Optional[str] = None
    error_message: Optional[str] = None

    @property
    @deprecated(reason="This is deprecated. Use `scene_uuid` instead of `uuid`")
    def uuid(self) -> str:
        return self.scene_uuid

    @property
    @deprecated(reason="This is deprecated. Use `scene_type` instead of `input_type`")
    def input_type(self) -> str:
        return self.scene_type

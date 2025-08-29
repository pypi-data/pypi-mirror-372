from datetime import datetime
from enum import Enum
from typing import Optional

from kognic.io.model.base_serializer import BaseSerializer


class SceneStatus(str, Enum):
    Pending = "pending"
    Processing = "processing"
    Created = "created"
    Failed = "failed"
    Indexed = "indexed"
    InvalidatedBadContent = "invalidated:broken-input"
    InvalidatedDuplicate = "invalidated:duplicate"
    InvalidatedIncorrectlyCreated = "invalidated:incorrectly-created"


class Scene(BaseSerializer):
    uuid: str
    workspace_id: str
    external_id: str
    scene_type: str
    status: SceneStatus
    created: datetime
    calibration_id: Optional[str] = None
    view_link: Optional[str] = None
    error_message: Optional[str] = None

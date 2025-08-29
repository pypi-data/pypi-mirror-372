from datetime import datetime
from enum import Enum

from kognic.io.model.base_serializer import BaseSerializer


class ProjectBatchStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    READY = "ready"
    INPROGESS = "in-progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBatch(BaseSerializer):
    project: str
    batch: str
    title: str
    status: ProjectBatchStatus
    created: datetime
    updated: datetime

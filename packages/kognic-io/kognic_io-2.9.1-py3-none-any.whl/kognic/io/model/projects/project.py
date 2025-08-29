from datetime import datetime

from kognic.io.model.base_serializer import BaseSerializer


class Project(BaseSerializer):
    created: datetime
    title: str
    description: str
    status: str
    project: str

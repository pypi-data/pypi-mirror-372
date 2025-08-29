from datetime import datetime

from kognic.io.model.base_serializer import BaseSerializer
from kognic.openlabel.models.models import OpenLabelAnnotation


class ResolvedPreAnnotation(BaseSerializer):
    uuid: str
    scene_uuid: str
    external_id: str
    created: datetime
    content: OpenLabelAnnotation

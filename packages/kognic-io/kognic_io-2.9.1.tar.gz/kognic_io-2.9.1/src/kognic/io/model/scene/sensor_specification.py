from typing import Dict, List, Optional

from kognic.io.model.base_serializer import BaseSerializer


class CameraSettings(BaseSerializer):
    width: int
    height: int


class SensorSpecification(BaseSerializer):
    sensor_to_pretty_name: Optional[Dict[str, str]] = None
    sensor_order: Optional[List[str]] = None

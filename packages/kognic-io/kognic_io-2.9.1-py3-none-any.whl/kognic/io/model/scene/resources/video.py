from abc import ABC

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.scene.resources.resource import Resource

camera_sensor_default = "CAM"


class VideoTS(ABC, BaseSerializer):
    video_timestamp: int


class VideoFrame(Resource, VideoTS):
    sensor_name: str = camera_sensor_default
    video_timestamp: int

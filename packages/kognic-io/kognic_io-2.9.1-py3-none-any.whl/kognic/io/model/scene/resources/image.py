from typing import Optional

from pydantic import field_validator

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.scene.resources.resource import Resource

camera_sensor_default = "CAM"


class ImageMetadata(BaseSerializer):
    shutter_time_start_ns: int
    shutter_time_end_ns: int


class Image(Resource):
    sensor_name: str = camera_sensor_default
    metadata: Optional[ImageMetadata] = None

    @field_validator("file_data", mode="before")
    @classmethod
    def cannot_be_pointcloud(cls, value):
        if not value.format.is_image:
            raise ValueError(f"Invalid format for image data: {value.format}")
        return value

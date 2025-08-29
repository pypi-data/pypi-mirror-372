import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from kognic.base_clients.cloud_storage.upload_spec import Callback


@dataclass
class SensorSpecification:
    sensorToPrettyName: Dict[str, str]
    sensorOrder: List[str]


@dataclass
class LocalFile:
    filename: str
    data: Optional[bytes] = None
    callback: Optional[Callback] = None


@dataclass
class Resource:
    external_resource_uri: Optional[str]
    local_file: Optional[LocalFile]

    def __post_init__(self):
        if bool(self.external_resource_uri) == bool(self.local_file):
            raise ValueError("Exactly one of external_resource_uri or local_file must be provided")

    def to_dict(self):
        if self.external_resource_uri:
            return {
                "externalResourceUri": self.external_resource_uri,
            }
        else:
            return {
                "localFilename": self.local_file.filename,
            }


@dataclass
class SensorResource(Resource):
    sensor_name: str

    def to_dict(self):
        return {"sensorName": self.sensor_name, **super().to_dict()}


@dataclass
class ImageResource(SensorResource):
    start_shutter_timestamp_ns: Optional[int] = None
    end_shutter_timestamp_ns: Optional[int] = None

    def __post_init__(self):
        if bool(self.start_shutter_timestamp_ns) != bool(self.end_shutter_timestamp_ns):
            raise ValueError("start_shutter_timestamp_ns and end_shutter_timestamp_ns must be both None or both not None")
        if self.start_shutter_timestamp_ns is not None and self.start_shutter_timestamp_ns >= self.end_shutter_timestamp_ns:
            raise ValueError("start_shutter_timestamp_ns must be less than end_shutter_timestamp_ns")

    def to_dict(self):
        resource_dict = super().to_dict()
        if self.start_shutter_timestamp_ns:
            return {
                "resource": resource_dict,
                "metadata": {
                    "startShutterTimestampNs": self.start_shutter_timestamp_ns,
                    "endShutterTimestampNs": self.end_shutter_timestamp_ns,
                },
            }
        else:
            return {"resource": resource_dict}


@dataclass
class EgoVehiclePose:
    x: float
    y: float
    z: float
    rotation_x: float
    rotation_y: float
    rotation_z: float
    rotation_w: float


@dataclass
class Frame:
    frame_id: str
    timestamp_ns: int
    images: List[ImageResource]
    pointclouds: Optional[List[SensorResource]] = None
    ego_vehicle_pose: Optional[EgoVehiclePose] = None
    metadata: Optional[dict] = None

    def __post_init__(self):
        if not self.images:
            raise ValueError("Frame must contain at least one image")

    def to_dict(self):
        result = {
            "id": self.frame_id,
            "timestampNs": self.timestamp_ns,
            "images": [image.to_dict() for image in self.images],
        }

        if self.pointclouds:
            pointclouds = {
                "resources": [pointcloud.to_dict() for pointcloud in self.pointclouds],
                "egoVehiclePose": {
                    "position": {"x": self.ego_vehicle_pose.x, "y": self.ego_vehicle_pose.y, "z": self.ego_vehicle_pose.z},
                    "rotation": {
                        "x": self.ego_vehicle_pose.rotation_x,
                        "y": self.ego_vehicle_pose.rotation_y,
                        "z": self.ego_vehicle_pose.rotation_z,
                        "w": self.ego_vehicle_pose.rotation_w,
                    },
                },
            }
            result["pointClouds"] = pointclouds
        if self.metadata:
            result["metadata"] = self.metadata

        return result


@dataclass
class SceneRequest:
    workspace_id: str
    external_id: str
    frames: List[Frame]
    sensor_specification: Optional[SensorSpecification] = None
    calibration_id: Optional[str] = None
    metadata: Optional[dict] = None
    imudata_resource: Optional[Resource] = None
    should_motion_compensate: Optional[bool] = None
    postpone_external_resource_import: Optional[bool] = None

    def __post_init__(self):
        if not self.frames:
            raise ValueError("Scene must contain at least one frame")

    def get_files(self) -> Dict[str, LocalFile]:
        files = {}
        for frame in self.frames:
            for image in frame.images:
                if image.local_file:
                    files[image.local_file.filename] = image.local_file
            for pointcloud in frame.pointclouds or []:
                if pointcloud.local_file:
                    files[pointcloud.local_file.filename] = pointcloud.local_file
        if self.imudata_resource and self.imudata_resource.local_file:
            files[self.imudata_resource.local_file.filename] = self.imudata_resource
        return files

    def to_json(self):
        json.dumps(self.to_dict())

    def to_dict(self):
        d = {"workspaceId": self.workspace_id, "externalId": self.external_id}
        converted_spec = {"frames": [frame.to_dict() for frame in self.frames]}

        if self.sensor_specification:
            converted_spec["sensorSpecification"] = {
                "sensorToPrettyName": self.sensor_specification.sensorToPrettyName,
                "sensorOrder": self.sensor_specification.sensorOrder,
            }
        if self.calibration_id:
            d["calibrationId"] = self.calibration_id
        if self.metadata:
            converted_spec["metadata"] = self.metadata
        if self.imudata_resource:
            converted_spec["imuData"] = self.imudata_resource.to_dict()
        if self.should_motion_compensate:
            converted_spec["shouldMotionCompensate"] = self.should_motion_compensate
        if self.postpone_external_resource_import is not None:
            d["postponeExternalResourceImport"] = self.postpone_external_resource_import

        d["convertedSpecification"] = converted_spec
        return d

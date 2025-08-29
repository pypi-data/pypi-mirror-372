from enum import Enum

from kognic.io.model.base_serializer import BaseSerializer


class CalibrationType(str, Enum):
    PINHOLE = "pinhole"
    FISHEYE = "fisheye"
    KANNALA = "kannala"
    LIDAR = "lidar"
    PRINCIPALPOINTDIST = "principal_point_distortion"
    FUSEDCYLINDRICAL = "fused_cylindrical"
    CYLINDRICAL = "cylindrical"
    PRINCIPALPOINTFISHEYE = "principal_point_fisheye"
    CUSTOM = "custom"


class RotationQuaternion(BaseSerializer):
    w: float
    x: float
    y: float
    z: float


class Position(BaseSerializer):
    x: float
    y: float
    z: float


class BaseCalibration(BaseSerializer):
    calibration_type: CalibrationType
    position: Position
    rotation_quaternion: RotationQuaternion

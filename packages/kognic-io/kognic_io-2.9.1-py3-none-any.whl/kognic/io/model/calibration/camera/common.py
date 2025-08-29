from typing import Optional

from kognic.io.model.calibration.common import BaseCalibration, BaseSerializer


class CameraMatrix(BaseSerializer):
    fx: float
    fy: float
    cx: float
    cy: float


class DistortionCoefficients(BaseSerializer):
    k1: float
    k2: float
    p1: float
    p2: float
    k3: float


class BaseCameraCalibration(BaseCalibration):
    image_height: int
    image_width: int


class BaseStandardCameraCalibration(BaseCameraCalibration):
    camera_matrix: CameraMatrix
    field_of_view: Optional[float] = None

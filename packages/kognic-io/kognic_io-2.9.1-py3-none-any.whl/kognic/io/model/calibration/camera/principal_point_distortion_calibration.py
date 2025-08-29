from typing import List, Optional

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration
from kognic.io.model.calibration.common import CalibrationType


class PrincipalPointDistortionCoefficients(BaseSerializer):
    k1: float
    k2: float


class PrincipalPoint(BaseSerializer):
    x: float
    y: float


class DistortionCenter(BaseSerializer):
    x: float
    y: float


class LensProjectionCoefficients(BaseSerializer):
    c1: float
    c2: float
    c3: float
    c4: float
    c5: float
    c6: float

    def get_coefficients(self) -> List[float]:
        return [self.c1, self.c2, self.c3, self.c4, self.c5, self.c6]


class PrincipalPointDistortionCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.PRINCIPALPOINTDIST
    principal_point_distortion_coefficients: PrincipalPointDistortionCoefficients
    distortion_center: DistortionCenter
    principal_point: PrincipalPoint
    lens_projection_coefficients: Optional[LensProjectionCoefficients] = None

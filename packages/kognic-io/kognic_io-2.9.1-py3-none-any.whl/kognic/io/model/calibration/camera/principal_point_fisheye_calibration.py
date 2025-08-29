from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration
from kognic.io.model.calibration.common import CalibrationType


class PrincipalPointFisheyeCoefficients(BaseSerializer):
    alpha_l: float
    alpha_r: float
    beta_u: float
    beta_l: float


class PrincipalPointFisheyeCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.PRINCIPALPOINTFISHEYE
    principal_point_fisheye_coefficients: PrincipalPointFisheyeCoefficients

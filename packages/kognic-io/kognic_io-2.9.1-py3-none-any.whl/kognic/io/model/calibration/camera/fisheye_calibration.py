from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration, DistortionCoefficients
from kognic.io.model.calibration.common import CalibrationType


class FisheyeCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.FISHEYE
    distortion_coefficients: DistortionCoefficients
    xi: float

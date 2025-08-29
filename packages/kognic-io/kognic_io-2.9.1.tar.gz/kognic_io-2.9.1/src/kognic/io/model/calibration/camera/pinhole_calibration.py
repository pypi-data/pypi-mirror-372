from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration, DistortionCoefficients
from kognic.io.model.calibration.common import CalibrationType


class PinholeCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.PINHOLE
    distortion_coefficients: DistortionCoefficients

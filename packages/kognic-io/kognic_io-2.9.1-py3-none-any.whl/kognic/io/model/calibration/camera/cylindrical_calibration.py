from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration
from kognic.io.model.calibration.common import CalibrationType


class CylindricalCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.CYLINDRICAL

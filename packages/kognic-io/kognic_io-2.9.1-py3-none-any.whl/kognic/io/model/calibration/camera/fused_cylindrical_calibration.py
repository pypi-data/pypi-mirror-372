from typing import Optional

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration.camera.common import BaseStandardCameraCalibration
from kognic.io.model.calibration.common import CalibrationType


class CutAngles(BaseSerializer):
    upper: float
    lower: float


class FusedCylindricalCalibration(BaseStandardCameraCalibration):
    calibration_type: CalibrationType = CalibrationType.FUSEDCYLINDRICAL
    cut_angles_degree: CutAngles
    vertical_fov_degree: Optional[float] = 72.5
    horizontal_fov_degree: Optional[float] = 93
    max_altitude_angle_degree: Optional[float] = 90.0

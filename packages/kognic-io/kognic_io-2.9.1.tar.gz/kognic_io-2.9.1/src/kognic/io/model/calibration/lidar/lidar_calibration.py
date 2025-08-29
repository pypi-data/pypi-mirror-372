from typing import Optional

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration.common import BaseCalibration, CalibrationType


class LidarFieldOfView(BaseSerializer):
    start_angle_deg: float
    stop_angle_deg: float
    depth: Optional[float] = None


class LidarCalibration(BaseCalibration):
    calibration_type: CalibrationType = CalibrationType.LIDAR
    field_of_view: Optional[LidarFieldOfView] = None

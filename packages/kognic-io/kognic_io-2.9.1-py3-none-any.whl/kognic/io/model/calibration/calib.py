from datetime import datetime
from typing import Dict, Mapping, Optional

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration.camera.custom_camera_calibration import CustomCameraCalibration
from kognic.io.model.calibration.camera.cylindrical_calibration import CylindricalCalibration
from kognic.io.model.calibration.camera.fisheye_calibration import FisheyeCalibration
from kognic.io.model.calibration.camera.fused_cylindrical_calibration import FusedCylindricalCalibration
from kognic.io.model.calibration.camera.kannala_calibration import KannalaCalibration
from kognic.io.model.calibration.camera.pinhole_calibration import PinholeCalibration
from kognic.io.model.calibration.camera.principal_point_distortion_calibration import PrincipalPointDistortionCalibration
from kognic.io.model.calibration.camera.principal_point_fisheye_calibration import PrincipalPointFisheyeCalibration
from kognic.io.model.calibration.common import BaseCalibration, CalibrationType
from kognic.io.model.calibration.lidar.lidar_calibration import LidarCalibration
from kognic.io.util import ts_to_dt

calibration_factory = {
    CalibrationType.LIDAR: LidarCalibration,
    CalibrationType.PINHOLE: PinholeCalibration,
    CalibrationType.KANNALA: KannalaCalibration,
    CalibrationType.FISHEYE: FisheyeCalibration,
    CalibrationType.PRINCIPALPOINTDIST: PrincipalPointDistortionCalibration,
    CalibrationType.FUSEDCYLINDRICAL: FusedCylindricalCalibration,
    CalibrationType.CYLINDRICAL: CylindricalCalibration,
    CalibrationType.PRINCIPALPOINTFISHEYE: PrincipalPointFisheyeCalibration,
    CalibrationType.CUSTOM: CustomCameraCalibration,
}


class SensorCalibration(BaseSerializer):
    external_id: str
    calibration: Dict[str, BaseCalibration]

    def to_dict(self):
        return {"externalId": self.external_id, "calibration": {k: v.to_dict(by_alias=False) for (k, v) in self.calibration.items()}}


class SensorCalibrationEntry(BaseSerializer):
    id: str
    external_id: str
    created: datetime
    workspace_id: Optional[str] = None
    calibration: Optional[Mapping[str, BaseCalibration]] = None

    @classmethod
    def from_json(cls, js: dict):
        calibrations = js.get("calibration", {})

        calibration = {}
        for sensor, calib in calibrations.items():
            calibration[sensor] = cls._parse_calibration(calib)
        return SensorCalibrationEntry(
            id=js["id"],
            external_id=js["externalId"],
            workspace_id=js.get("workspaceId"),
            created=ts_to_dt(js["created"]),
            calibration=calibration,
        )

    @staticmethod
    def _parse_calibration(calibration: dict) -> BaseCalibration:
        calibration_type = calibration.get("calibration_type")
        CalibrationModel = calibration_factory.get(calibration_type)
        if CalibrationModel is None:
            raise TypeError(f"Unable to parse calibration type: {calibration_type}")

        return CalibrationModel(**calibration)

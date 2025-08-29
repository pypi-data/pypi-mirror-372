from typing import List, Optional

from kognic.io.model import IMUData
from kognic.io.model.calibration.common import BaseSerializer


class ValidatedIMUData(BaseSerializer):
    resource_id: str
    signed_url: Optional[str] = None
    imu_data: List[IMUData]

    def serialize_imu_data(self):
        return [imud.to_dict() for imud in self.imu_data]


class ValidateIMUDataRequest(BaseSerializer):
    imu_data: List[IMUData]
    internal_id: str

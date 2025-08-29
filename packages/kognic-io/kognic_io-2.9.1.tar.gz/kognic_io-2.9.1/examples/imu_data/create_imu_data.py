import random
from typing import List

from kognic.io.model import IMUData
from kognic.io.model.calibration.common import Position, RotationQuaternion


def create_dummy_imu_data(
    start_timestamp: int = 123000000000, end_timestamp: int = 130000000000, samples_per_sec: int = 1
) -> List[IMUData]:
    def randfloat():
        return random.uniform(0, 1)

    sample_ns = 1_000_000_000 // int(samples_per_sec)

    imu_datas = []
    for idx in range(start_timestamp, end_timestamp + 1, sample_ns):
        pos = Position(x=randfloat(), y=randfloat(), z=randfloat())
        rotation = RotationQuaternion(x=randfloat(), y=randfloat(), z=randfloat(), w=randfloat())
        imu_datas.append(IMUData(position=pos, rotation_quaternion=rotation, timestamp=idx))

    return imu_datas

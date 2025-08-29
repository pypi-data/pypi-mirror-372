from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model import SensorCalibrationEntry


def run(client: KognicIOClient) -> List[SensorCalibrationEntry]:
    print("Get One Calibration...")

    calibrations = client.calibration.get_calibrations()
    calibrations = client.calibration.get_calibrations(external_id=calibrations[0].external_id)

    return calibrations[0]


if __name__ == "__main__":
    client = KognicIOClient()
    run(client)

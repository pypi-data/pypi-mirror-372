from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model import SensorCalibrationEntry


def run(client: KognicIOClient) -> List[SensorCalibrationEntry]:
    print("Listing Calibration...")

    return client.calibration.get_calibrations()


if __name__ == "__main__":
    client = KognicIOClient()
    run(client)

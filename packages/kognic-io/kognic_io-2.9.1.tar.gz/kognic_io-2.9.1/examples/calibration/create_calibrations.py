from examples.calibration.calibration import create_sensor_calibration
from kognic.io.client import KognicIOClient
from kognic.io.model import SensorCalibrationEntry


def run(client: KognicIOClient, calibration_identifier: str) -> SensorCalibrationEntry:
    print("Listing Calibration...")

    lidar_sensor1 = "lidar"
    cam_sensors = [f"RFC0{i}" for i in range(1, 9)]

    # Create calibration
    calibration_spec = create_sensor_calibration(calibration_identifier, [lidar_sensor1], cam_sensors)
    return client.calibration.create_calibration(calibration_spec)


if __name__ == "__main__":
    from datetime import datetime

    client = KognicIOClient()
    calibration_identifier = f"calibration-{datetime.now()}"
    run(client, calibration_identifier)

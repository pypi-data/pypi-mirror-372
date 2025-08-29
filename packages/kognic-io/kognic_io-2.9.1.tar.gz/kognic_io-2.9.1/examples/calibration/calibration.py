from typing import List, Optional

import kognic.io.model.calibration as CalibrationModel
from examples.calibration.create_custom_camera_calibration import example_custom_camera_calibration
from examples.calibration.create_cylindrical_calibration import example_cylindrical_calibration
from examples.calibration.create_fisheye_calibration import unity_fisheye_calibration
from examples.calibration.create_fused_cylindrical_calibration import example_fused_cylindrical_calibration
from examples.calibration.create_kannala_calibration import unity_kannala_calibration
from examples.calibration.create_lidar_calibration import unity_lidar_calibration
from examples.calibration.create_pinhole_calibration import unity_pinhole_calibration
from examples.calibration.create_principal_point_distortion_calibration import unity_principal_point_distortion_calibration
from examples.calibration.create_principal_point_fisheye_calibration import unity_principal_point_fisheye_calibration
from kognic.io.client import KognicIOClient


def create_sensor_calibration(external_id, lidar_sources: Optional[List[str]] = None, camera_sources: Optional[List[str]] = None):
    if lidar_sources is None:
        lidar_sources = []

    if camera_sources is None:
        camera_sources = []

    # Create calibration for the scene
    camera_calibrations = [
        unity_kannala_calibration(),
        unity_pinhole_calibration(),
        unity_fisheye_calibration(),
        unity_principal_point_distortion_calibration(),
        unity_principal_point_fisheye_calibration(),
        example_cylindrical_calibration(),
        example_fused_cylindrical_calibration(),
        example_custom_camera_calibration(),
    ]
    calibration_dict = {
        **{lidar_source: unity_lidar_calibration() for lidar_source in lidar_sources},
        **{camera_source: camera_calibrations.pop() for camera_source in camera_sources},
    }
    calibration_external_id = external_id
    sensor_calibration = CalibrationModel.SensorCalibration(external_id=calibration_external_id, calibration=calibration_dict)

    return sensor_calibration


if __name__ == "__main__":
    print("Creating Calibration...")

    client = KognicIOClient()

    calibration = create_sensor_calibration("2020-06-16", ["lidar"], ["RFC01"])

    # Create the calibration using the Input API client
    created_calibration = client.calibration.create_calibration(sensor_calibration=calibration)

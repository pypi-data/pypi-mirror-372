from examples.calibration.create_custom_camera_calibration import example_custom_camera_calibration
from examples.calibration.create_cylindrical_calibration import example_cylindrical_calibration
from examples.calibration.create_fisheye_calibration import unity_fisheye_calibration
from examples.calibration.create_kannala_calibration import unity_kannala_calibration
from examples.calibration.create_lidar_calibration import unity_lidar_calibration
from examples.calibration.create_pinhole_calibration import unity_pinhole_calibration
from examples.calibration.create_principal_point_distortion_calibration import unity_principal_point_distortion_calibration
from examples.calibration.create_principal_point_fisheye_calibration import unity_principal_point_fisheye_calibration
from kognic.io.model.calibration.calib import SensorCalibration


def test_serialize_sensor_calibration():
    content = {
        "kannala": unity_kannala_calibration(),
        "fisheye": unity_fisheye_calibration(),
        "pinhole": unity_pinhole_calibration(),
        "lidar": unity_lidar_calibration(),
        "cylindrical": example_cylindrical_calibration(),
        "principal_point_distortion": unity_principal_point_distortion_calibration(),
        "principal_point_fisheye": unity_principal_point_fisheye_calibration(),
        "custom": example_custom_camera_calibration(),
    }
    sensor_calibration = SensorCalibration(external_id="the-external-id", calibration=content)

    try:
        sensor_calibration.to_dict()
        assert True
    except Exception as e:
        raise AssertionError(f"Got the following error when serializing sensor calibration: {e}")

from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.kannala_calibration import (
    KannalaCalibration,
    KannalaDistortionCoefficients,
    UndistortionCoefficients,
)
from kognic.io.model.calibration.common import Position, RotationQuaternion


def unity_kannala_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)  # similar to Lidar
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)  # similar to Lidar
    camera_camera_matrix = CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
    camera_distortion_coefficients = KannalaDistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0)
    camera_undistortion_coefficients = UndistortionCoefficients(l1=0.0, l2=0.0, l3=0.0, l4=0.0)
    return KannalaCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        distortion_coefficients=camera_distortion_coefficients,
        undistortion_coefficients=camera_undistortion_coefficients,
        image_height=1080,
        image_width=1920,
        field_of_view=180.0,
    )

from kognic.io.model.calibration.camera.common import CameraMatrix, DistortionCoefficients
from kognic.io.model.calibration.camera.fisheye_calibration import FisheyeCalibration
from kognic.io.model.calibration.common import Position, RotationQuaternion


def unity_fisheye_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    camera_camera_matrix = CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
    camera_distortion_coefficients = DistortionCoefficients(k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.1)
    return FisheyeCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        distortion_coefficients=camera_distortion_coefficients,
        image_height=1080,
        image_width=1920,
        xi=123.456,
        field_of_view=190.0,
    )

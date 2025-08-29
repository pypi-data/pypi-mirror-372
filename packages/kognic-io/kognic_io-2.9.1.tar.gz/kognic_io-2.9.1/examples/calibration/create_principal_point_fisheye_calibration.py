from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.principal_point_fisheye_calibration import (
    PrincipalPointFisheyeCalibration,
    PrincipalPointFisheyeCoefficients,
)
from kognic.io.model.calibration.common import Position, RotationQuaternion


def unity_principal_point_fisheye_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    camera_camera_matrix = CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
    principal_point_fisheye_coefficients = PrincipalPointFisheyeCoefficients(alpha_l=0.0, alpha_r=0.0, beta_u=0.0, beta_l=0.0)
    return PrincipalPointFisheyeCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        principal_point_fisheye_coefficients=principal_point_fisheye_coefficients,
        image_height=1080,
        image_width=1920,
        field_of_view=180.0,
    )

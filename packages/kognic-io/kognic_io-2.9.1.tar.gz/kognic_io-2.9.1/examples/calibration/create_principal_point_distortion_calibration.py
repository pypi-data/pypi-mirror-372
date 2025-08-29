from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.principal_point_distortion_calibration import (
    DistortionCenter,
    LensProjectionCoefficients,
    PrincipalPoint,
    PrincipalPointDistortionCalibration,
    PrincipalPointDistortionCoefficients,
)
from kognic.io.model.calibration.common import Position, RotationQuaternion


def unity_principal_point_distortion_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    camera_camera_matrix = CameraMatrix(fx=3450, fy=3250, cx=622, cy=400)
    camera_distortion_coefficients = PrincipalPointDistortionCoefficients(k1=0.0, k2=0.0)
    principal_point = PrincipalPoint(x=0.0, y=0.0)
    distortion_center = DistortionCenter(x=0.0, y=0.0)
    lens_projection_coefficients = LensProjectionCoefficients(c1=0.0, c2=0.0, c3=0.0, c4=0.0, c5=0.0, c6=0.0)
    return PrincipalPointDistortionCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        principal_point_distortion_coefficients=camera_distortion_coefficients,
        lens_projection_coefficients=lens_projection_coefficients,
        principal_point=principal_point,
        distortion_center=distortion_center,
        image_height=1080,
        image_width=1920,
        field_of_view=180.0,
    )

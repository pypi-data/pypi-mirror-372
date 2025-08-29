from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.fused_cylindrical_calibration import CutAngles, FusedCylindricalCalibration
from kognic.io.model.calibration.common import Position, RotationQuaternion


def example_fused_cylindrical_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    camera_camera_matrix = CameraMatrix(fx=400, fy=400, cx=600, cy=450)
    cut_angles_degree = CutAngles(upper=-40.0, lower=30.0)
    return FusedCylindricalCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        image_height=1080,
        image_width=1920,
        cut_angles_degree=cut_angles_degree,
        vertical_fov_degree=70,
        horizontal_fov_degree=90.0,
        max_altitude_angle_degree=90.0,
    )

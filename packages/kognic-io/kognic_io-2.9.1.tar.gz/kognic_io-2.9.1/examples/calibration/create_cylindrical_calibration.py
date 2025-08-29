from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.cylindrical_calibration import CylindricalCalibration
from kognic.io.model.calibration.common import Position, RotationQuaternion


def example_cylindrical_calibration():
    camera_position = Position(x=0.0, y=0.0, z=0.0)
    camera_rotation = RotationQuaternion(w=1.0, x=0.0, y=0.0, z=0.0)
    camera_camera_matrix = CameraMatrix(fx=400, fy=400, cx=600, cy=450)
    return CylindricalCalibration(
        position=camera_position,
        rotation_quaternion=camera_rotation,
        camera_matrix=camera_camera_matrix,
        image_height=1080,
        image_width=1920,
    )

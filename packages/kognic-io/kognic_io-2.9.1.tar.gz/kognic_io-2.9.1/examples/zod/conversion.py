from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd
from pandas import DataFrame
from scipy.spatial.transform import Rotation as R
from utils import seconds_to_ns
from zod.constants import Camera as ZodCamera
from zod.constants import Lidar as ZodLidar
from zod.data_classes.calibration import Calibration as ZodCalibration
from zod.data_classes.calibration import CameraCalibration as ZodCameraCalibration
from zod.data_classes.calibration import LidarCalibration as ZodLidarCalibration
from zod.data_classes.geometry import Pose as ZodPose
from zod.data_classes.sensor import CameraFrame as ZodCameraFrame
from zod.data_classes.sensor import SensorFrame as ZodSensorFrame

from kognic.io.model import Image, ImageMetadata, PointCloud
from kognic.io.model.calibration import KannalaCalibration, LidarCalibration, Position, RotationQuaternion, SensorCalibration
from kognic.io.model.calibration.camera.common import CameraMatrix
from kognic.io.model.calibration.camera.kannala_calibration import KannalaDistortionCoefficients, UndistortionCoefficients
from kognic.io.model.ego import EgoVehiclePose
from kognic.io.resources.scene.file_data import FileData


def get_pos(extrinsic: list[list[float]]) -> Position:
    return Position(x=extrinsic[0][3], y=extrinsic[1][3], z=extrinsic[2][3])


def get_quat(extrinsic: list[list[float]]) -> RotationQuaternion:
    extrinsic = np.asarray(extrinsic)
    rot = R.from_matrix(extrinsic[:3, :3]).as_quat()
    return RotationQuaternion(w=rot[3], x=rot[0], y=rot[1], z=rot[2])


def zod_pose_to_position(pose: ZodPose) -> Position:
    return Position(x=pose.translation[0], y=pose.translation[1], z=pose.translation[2])


def zod_pose_to_rotation(pose: ZodPose) -> RotationQuaternion:
    return RotationQuaternion(w=pose.rotation.w, x=pose.rotation.x, y=pose.rotation.y, z=pose.rotation.z)


""" Ego motion conversion functions """


def convert_to_ego_vehicle_pose(transform: np.array) -> EgoVehiclePose:
    return EgoVehiclePose(position=get_pos(transform), rotation=get_quat(transform))


""" Calibration conversion functions """


def convert_lidar_calibration(calibration: ZodLidarCalibration) -> LidarCalibration:
    return LidarCalibration(
        position=zod_pose_to_position(calibration.extrinsics),
        rotation_quaternion=zod_pose_to_rotation(calibration.extrinsics),
    )


def convert_camera_calibration(calibration: ZodCameraCalibration) -> KannalaCalibration:
    dist = calibration.distortion
    undist = calibration.undistortion
    intrinsics = calibration.intrinsics
    dist_coeff = KannalaDistortionCoefficients(k1=dist[0], k2=dist[1], p1=dist[2], p2=dist[3])
    undist_coeff = UndistortionCoefficients(l1=undist[0], l2=undist[1], l3=undist[2], l4=undist[3])
    camera_matrix = CameraMatrix(fx=intrinsics[0][0], fy=intrinsics[1][1], cx=intrinsics[0][2], cy=intrinsics[1][2])
    return KannalaCalibration(
        position=zod_pose_to_position(calibration.extrinsics),
        rotation_quaternion=zod_pose_to_rotation(calibration.extrinsics),
        camera_matrix=camera_matrix,
        image_width=calibration.image_dimensions[0],
        image_height=calibration.image_dimensions[1],
        distortion_coefficients=dist_coeff,
        undistortion_coefficients=undist_coeff,
    )


def convert_calibration(zod_calibration: ZodCalibration) -> SensorCalibration:
    lidar_calib = convert_lidar_calibration(zod_calibration.lidars[ZodLidar.VELODYNE])
    camera_calib = convert_camera_calibration(zod_calibration.cameras[ZodCamera.FRONT])

    calibrations = {
        ZodLidar.VELODYNE: lidar_calib,
        ZodCamera.FRONT: camera_calib,
    }
    external_id = "zod_calibration_" + str(uuid4())[:8]
    return SensorCalibration(calibration=calibrations, external_id=external_id)


""" Frame conversion functions """


def convert_zod_camera_frame_to_image(camera_frame: ZodCameraFrame) -> Image:
    camera_timestamp_ns = seconds_to_ns(camera_frame.time.timestamp())
    return Image(
        filename=camera_frame.filepath,
        sensor_name=ZodCamera.FRONT,
        metadata=ImageMetadata(
            shutter_time_start_ns=camera_timestamp_ns,
            shutter_time_end_ns=camera_timestamp_ns + 1,
        ),
    )


def convert_zod_lidar_frame_to_point_cloud(lidar_frame: ZodSensorFrame, timestamp_ns: int) -> PointCloud:
    pc_bytes = convert_pointcloud_to_bytes(Path(lidar_frame.filepath), timestamp_ns)
    return PointCloud(
        filename=lidar_frame.filepath,
        sensor_name=ZodLidar.VELODYNE,
        file_data=FileData(format=FileData.Format.CSV, data=pc_bytes),
    )


def convert_pointcloud_to_bytes(filepath: Path, timestamp_ns: int) -> bytes:
    pc = np.load(filepath)
    cols = ["ts_gps", "x", "y", "z", "intensity"]
    df = create_pc_dataframe(pc, timestamp_ns)
    return df[cols].to_csv(index=False).encode()


def create_pc_dataframe(pc: np.array, timestamp_ns: int) -> pd.DataFrame:
    df = DataFrame(pc, columns=["x", "y", "z", "timestamp", "intensity", "diode_index"])
    df["timestamp"] = df["timestamp"] + timestamp_ns
    df.columns = df.columns.str.replace("timestamp", "ts_gps")
    return df

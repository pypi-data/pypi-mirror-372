from __future__ import absolute_import

import time
from uuid import uuid4

import numpy as np
import pytest
from scipy.spatial.transform import Rotation as R

import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job, wait_for_scene_job_status
from kognic.io.model import SceneStatus
from kognic.io.model.calibration.camera.kannala_calibration import KannalaDistortionCoefficients, UndistortionCoefficients


@pytest.mark.integration
class TestCreateSceneWithExternalResources:
    def test_create_scene_with_external_resources(self, client: IOC.KognicIOClient):
        calibration = TestCreateSceneWithExternalResources.create_calibration(client)

        # Create indexed scene
        request = IAM.scene.SceneRequest(
            workspace_id="557ca28f-c405-4dd3-925f-ee853d858e4b",
            external_id=f"scene_with_external_resources_{uuid4()}",
            frames=[
                IAM.scene.Frame(
                    frame_id="1",
                    timestamp_ns=1644841412,
                    pointclouds=[
                        IAM.scene.SensorResource(
                            external_resource_uri="s3://jesper-test-chain-of-trust-2/zod/000000/lidar_velodyne/000000_quebec_2022-02-14T13:23:32_251875Z.csv",
                            sensor_name="lidar_velodyne",
                            local_file=None,
                        )
                    ],
                    images=[
                        IAM.scene.ImageResource(
                            external_resource_uri="s3://jesper-test-chain-of-trust-2/zod/000000/camera_front_blur/000000_quebec_2022-02-14T13:23:32_140954Z.jpg",
                            sensor_name="camera_front_blur",
                            start_shutter_timestamp_ns=1644841411,
                            end_shutter_timestamp_ns=1644841412,
                            local_file=None,
                        )
                    ],
                    ego_vehicle_pose=IAM.scene.EgoVehiclePose(
                        x=0.0, y=0.0, z=0.0, rotation_x=0.0, rotation_y=0.0, rotation_z=0.0, rotation_w=1.0
                    ),
                    metadata={},
                )
            ],
            calibration_id=calibration.id,
            should_motion_compensate=False,
            postpone_external_resource_import=True,
        )

        response = client.scene.create_scene(request)
        scene_uuid = response.scene_uuid
        print(f"Scene created with uuid: {scene_uuid}")
        status = wait_for_scene_job_status(client, scene_uuid, [SceneStatus.Indexed], [SceneStatus.Failed])
        assert status == IAM.SceneStatus.Indexed, f"Scene creation failed with status: {status}"

        # import scene
        client.scene.import_indexed_scene(scene_uuid)
        wait_for_scene_job(client, scene_uuid, fail_on_failed=True)

        # reindex scene
        client.scene.reindex_scene(scene_uuid)
        time.sleep(5)
        response = client.scene.get_scenes_by_uuids(scene_uuids=[scene_uuid])
        scene = response[0]
        assert scene.status == IAM.SceneStatus.Indexed, f"Scene creation failed with status: {scene.status}"

    @staticmethod
    def create_calibration(client: IOC.KognicIOClient):
        client_calibration_json = {
            "camera_type": "kannala",
            "intrinsics": [
                [1882.142659676832, 0.0, 1954.268438554445, 0.0],
                [0.0, 1882.142659676832, 1106.649560144672, 0.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
            "extrinsics": [
                [-0.006578063444850836, 0.011680349828714453, 0.9999101452176573, 1.97495012757181],
                [-0.9999592598357662, -0.006257788104694723, -0.006505286830381105, 0.008773226558988063],
                [0.006181241786591635, -0.9999122009036181, 0.011721038096521249, 1.146968753440465],
                [0.0, 0.0, 0.0, 1.0],
            ],
            "lidar_extrinsics": [
                [-0.032289624163532364, 0.9994571432704946, -0.006542089647840243, 1.111913518244068],
                [-0.999478067346448, -0.032282456610745226, 0.001198285685977399, -0.00062770090551047],
                [0.0009864404633288875, 0.00657736731207132, 0.999977882342632, 1.739287665799535],
                [0.0, 0.0, 0.0, 1.0],
            ],
            "image_dimensions": [3848, 2168],
            "distortion": [-0.05083535441904471, 0.08950956369713539, -0.09153590890283082, 0.0338247357937785],
            "undistortion": [0.05201553428790375, -0.09327421448035254, 0.09890785919928619, -0.03781140026596332],
            "field_of_view": [119.5122557575978, 66.66830114693289],
            "xi": None,
        }
        lidar_extrinsics = np.array(client_calibration_json.get("lidar_extrinsics"))
        lidar_rot = R.from_matrix(lidar_extrinsics[:3, :3]).as_quat()
        camer_extrinsics = np.array(client_calibration_json.get("extrinsics"))
        camera_rot = R.from_matrix(camer_extrinsics[:3, :3]).as_quat()
        camer_intrinsics = np.array(client_calibration_json.get("intrinsics"))
        dist = client_calibration_json.get("distortion")
        undist = client_calibration_json.get("undistortion")

        dist_coeff = KannalaDistortionCoefficients(k1=dist[0], k2=dist[1], p1=dist[2], p2=dist[3])
        undist_coeff = UndistortionCoefficients(l1=undist[0], l2=undist[1], l3=undist[2], l4=undist[3])

        calibration_dict = {
            "lidar_velodyne": IAM.LidarCalibration(
                position=IAM.Position(x=lidar_extrinsics[0][3], y=lidar_extrinsics[1][3], z=lidar_extrinsics[2][3]),
                rotation_quaternion=IAM.RotationQuaternion(w=lidar_rot[3], x=lidar_rot[0], y=lidar_rot[1], z=lidar_rot[2]),
            ),
            "camera_front_blur": IAM.KannalaCalibration(
                position=IAM.Position(x=camer_extrinsics[0][3], y=camer_extrinsics[1][3], z=camer_extrinsics[2][3]),
                rotation_quaternion=IAM.RotationQuaternion(w=camera_rot[3], x=camera_rot[0], y=camera_rot[1], z=camera_rot[2]),
                camera_matrix=IAM.CameraMatrix(
                    fx=camer_intrinsics[0][0], fy=camer_intrinsics[1][1], cx=camer_intrinsics[0][2], cy=camer_intrinsics[1][2]
                ),
                image_width=client_calibration_json.get("image_dimensions")[0],
                image_height=client_calibration_json.get("image_dimensions")[1],
                distortion_coefficients=dist_coeff,
                undistortion_coefficients=undist_coeff,
            ),
        }

        calibration = IAM.SensorCalibration(calibration=calibration_dict, external_id="zod_calibration_" + str(uuid4()))

        return client.calibration.create_calibration(calibration)

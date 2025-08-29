from __future__ import absolute_import

import os.path
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

import pytest

import kognic.io.model.scene.lidars_and_cameras_sequence as LCSM
import kognic.io.model.scene.resources as ResourceModel
from examples.calibration.calibration import create_sensor_calibration
from examples.imu_data.create_imu_data import create_dummy_imu_data
from examples.utils import wait_for_scene_job
from kognic.io.client import KognicIOClient
from kognic.io.model import EgoVehiclePose, IMUData, Project
from tests.utils import TestProjects

EXAMPLES_PATH = str(Path(os.path.dirname(__file__)).parent / "examples")

BatchWithMultiSensorConfig = "copyId"

LIDAR1 = "RFL01"
LIDAR2 = "RFL02"
CAMERA1 = "RFC01"
CAMERA2 = "RFC02"

# Generate IMU data
ONE_MILLISECOND = 1000000  # one millisecond, expressed in nanos
start_ts = 1648200140000000000
end_ts = start_ts + 10 * ONE_MILLISECOND
IMU_DATA = create_dummy_imu_data(start_timestamp=start_ts, end_timestamp=end_ts, samples_per_sec=1000)


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeqForMultiSensorConfiguration:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject]

    def run_test_with_multi_sensor(
        self,
        client: KognicIOClient,
        use_imu_data: bool = False,
        use_ego_poses: bool = False,
        use_unix_timestamps: bool = False,
        use_shutter_timestamps: bool = False,
    ):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project

        # Create calibration
        calibration_spec = create_sensor_calibration(f"Collection {datetime.now()}", [LIDAR1, LIDAR2], [CAMERA1, CAMERA2])
        created_calibration = client.calibration.create_calibration(calibration_spec)

        # Create scene
        lidars_and_cameras_seq = build_scene(
            calibration_id=created_calibration.id,
            use_imu_data=use_imu_data,
            use_ego_poses=use_ego_poses,
            use_unix_timestamps=use_unix_timestamps,
            use_shutter_timestamps=use_shutter_timestamps,
        )

        return client.lidars_and_cameras_sequence.create(
            lidars_and_cameras_seq, project=project, batch=BatchWithMultiSensorConfig, dryrun=False
        )

    def test_with_all_resources(self, client: KognicIOClient):
        resp = self.run_test_with_multi_sensor(
            client=client,
            use_imu_data=True,
            use_ego_poses=True,
            use_unix_timestamps=True,
            use_shutter_timestamps=True,
        )
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)
        assert isinstance(resp.scene_uuid, str)

    def test_with_imu_data_but_no_timestamps(self, client: KognicIOClient):
        with pytest.raises(RuntimeError) as exc_info:
            self.run_test_with_multi_sensor(
                client=client,
                use_imu_data=True,
                use_ego_poses=False,
                use_unix_timestamps=False,
                use_shutter_timestamps=False,
            )
        assert exc_info.value.args[0] == "Validation failed: If imu data is provided, all frames must have unix timestamps"

    def test_without_imu_data(self, client: KognicIOClient):
        with pytest.raises(RuntimeError) as exc_info:
            self.run_test_with_multi_sensor(
                client=client,
                use_imu_data=False,
                use_ego_poses=True,
                use_unix_timestamps=True,
                use_shutter_timestamps=True,
            )
        assert exc_info.value.args[0] == "Validation failed: Required multi-sensor resource is missing: imu data"

    def test_without_ego_poses(self, client: KognicIOClient):
        with pytest.raises(RuntimeError) as exc_info:
            self.run_test_with_multi_sensor(
                client=client,
                use_imu_data=True,
                use_ego_poses=False,
                use_unix_timestamps=True,
                use_shutter_timestamps=True,
            )
        assert exc_info.value.args[0] == "Validation failed: Required multi-sensor resource is missing: ego poses"

    def test_without_shutter_timestamps(self, client: KognicIOClient):
        with pytest.raises(RuntimeError) as exc_info:
            self.run_test_with_multi_sensor(
                client=client,
                use_imu_data=True,
                use_ego_poses=True,
                use_unix_timestamps=True,
                use_shutter_timestamps=False,
            )
        assert exc_info.value.args[0] == "Validation failed: Required multi-sensor resource is missing: image shutter times"


def imu_to_ego(imu: IMUData) -> EgoVehiclePose:
    return EgoVehiclePose(position=imu.position, rotation=imu.rotation_quaternion)


def create_calibration(client: KognicIOClient) -> str:
    # Create calibration
    calibration_spec = create_sensor_calibration(
        f"Collection {datetime.now()}",
        [LIDAR1, LIDAR2],
        [CAMERA1, CAMERA2],
    )
    created_calibration = client.calibration.create_calibration(calibration_spec)
    return created_calibration.id


def build_scene(
    calibration_id: str,
    use_imu_data: bool = False,
    use_ego_poses: bool = False,
    use_unix_timestamps: bool = False,
    use_shutter_timestamps: bool = False,
) -> LCSM.LidarsAndCamerasSequence:
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicleId": "abg"}

    return LCSM.LidarsAndCamerasSequence(
        external_id=f"LCS-full-with-imu-and-shutter-example-{uuid4()}",
        frames=[
            LCSM.Frame(
                frame_id="1",
                unix_timestamp=start_ts + ONE_MILLISECOND if use_unix_timestamps else None,
                relative_timestamp=0,
                ego_vehicle_pose=imu_to_ego(IMU_DATA[1]) if use_ego_poses else None,
                point_clouds=[
                    ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL01.csv", sensor_name=LIDAR1),
                    ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL02.csv", sensor_name=LIDAR2),
                ],
                images=[
                    ResourceModel.Image(
                        filename=EXAMPLES_PATH + "/resources/img_RFC01.jpg",
                        sensor_name=CAMERA1,
                        metadata=(
                            ResourceModel.ImageMetadata(
                                shutter_time_start_ns=start_ts + 0.5 * ONE_MILLISECOND, shutter_time_end_ns=start_ts + 1.5 * ONE_MILLISECOND
                            )
                            if use_shutter_timestamps
                            else None
                        ),
                    ),
                    ResourceModel.Image(
                        filename=EXAMPLES_PATH + "/resources/img_RFC02.jpg",
                        sensor_name=CAMERA2,
                        metadata=(
                            ResourceModel.ImageMetadata(
                                shutter_time_start_ns=start_ts + 0.5 * ONE_MILLISECOND, shutter_time_end_ns=start_ts + 1.5 * ONE_MILLISECOND
                            )
                            if use_shutter_timestamps
                            else None
                        ),
                    ),
                ],
            ),
            LCSM.Frame(
                frame_id="2",
                unix_timestamp=start_ts + 5 * ONE_MILLISECOND if use_unix_timestamps else None,
                relative_timestamp=4,
                ego_vehicle_pose=imu_to_ego(IMU_DATA[5]) if use_ego_poses else None,
                point_clouds=[
                    ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL11.csv", sensor_name=LIDAR1),
                    ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL12.csv", sensor_name=LIDAR2),
                ],
                images=[
                    ResourceModel.Image(
                        filename=EXAMPLES_PATH + "/resources/img_RFC11.jpg",
                        sensor_name=CAMERA1,
                        metadata=(
                            ResourceModel.ImageMetadata(
                                shutter_time_start_ns=start_ts + 4.5 * ONE_MILLISECOND, shutter_time_end_ns=start_ts + 5.5 * ONE_MILLISECOND
                            )
                            if use_shutter_timestamps
                            else None
                        ),
                    ),
                    ResourceModel.Image(
                        filename=EXAMPLES_PATH + "/resources/img_RFC12.jpg",
                        sensor_name=CAMERA2,
                        metadata=(
                            ResourceModel.ImageMetadata(
                                shutter_time_start_ns=start_ts + 4.5 * ONE_MILLISECOND, shutter_time_end_ns=start_ts + 5.5 * ONE_MILLISECOND
                            )
                            if use_shutter_timestamps
                            else None
                        ),
                    ),
                ],
            ),
        ],
        calibration_id=calibration_id,
        metadata=metadata,
        imu_data=IMU_DATA if use_imu_data else list(),
    )

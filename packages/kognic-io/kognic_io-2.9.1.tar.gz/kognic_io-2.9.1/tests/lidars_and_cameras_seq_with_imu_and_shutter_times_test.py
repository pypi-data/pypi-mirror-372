from __future__ import absolute_import

from typing import List

import pytest

import examples.lidars_and_cameras_seq_with_imu_and_shutter_times as lidars_cameras_seq_with_imu_and_shutter_times_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeqWithImuAndShutterTimes:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject]

    def test_validate_lidars_cameras_seq_with_imu_and_shutter_times_example(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        resp = lidars_cameras_seq_with_imu_and_shutter_times_example.run(client=client, project=project)
        assert resp is None

    def test_create_lidars_cameras_seq_with_imu_and_shutter_times_example(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        resp = lidars_cameras_seq_with_imu_and_shutter_times_example.run(client=client, project=project, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)
        assert isinstance(resp.scene_uuid, str)

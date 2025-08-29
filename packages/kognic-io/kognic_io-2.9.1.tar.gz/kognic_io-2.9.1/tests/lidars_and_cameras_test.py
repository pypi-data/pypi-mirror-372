from __future__ import absolute_import, annotations

from typing import List

import pytest

import examples.lidars_and_cameras as lidars_cameras_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeq:
    @staticmethod
    def filter_lidar_and_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasProject]

    def test_get_lidars_and_cameras_project(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_project(projects)
        assert len(project) == 1

    def test_validate_lidars_and_cameras_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_project(projects)[0].project
        resp = lidars_cameras_example.run(client=client, project=project)
        assert resp is None

    def test_create_lidars_and_cameras_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_project(projects)[0].project
        resp = lidars_cameras_example.run(client=client, project=project, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

    def test_validate_lidars_and_cameras_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_project(projects)[0].project

        annotation_types = ["object-detection", "signs"]
        resp = lidars_cameras_example.run(client=client, project=project, annotation_types=annotation_types)
        assert resp is None

    def test_create_lidars_and_cameras_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_project(projects)[0].project

        annotation_types = ["object-detection", "signs"]
        resp = lidars_cameras_example.run(client=client, project=project, annotation_types=annotation_types, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

    def test_create_dangling_lidars_and_cameras_input(self, client: IOC.KognicIOClient):
        resp = lidars_cameras_example.run(client=client, project=None, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

from __future__ import absolute_import

from typing import List

import pytest

import examples.cameras_seq_images as cameras_seq_images_example
import examples.cameras_seq_videos as cameras_seq_videos_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCameras:
    @staticmethod
    def filter_cameras_seq_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasSequenceProject]

    def test_get_cameras_project(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_seq_project(projects)
        assert len(project) == 1

    def test_validate_cameras_sequence_images_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_seq_project(projects)[0].project

        resp = cameras_seq_images_example.run(client=client, project=project)
        assert resp is None

    def test_create_cameras_sequence_images_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_seq_project(projects)[0].project
        resp = cameras_seq_images_example.run(client=client, project=project, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

    def test_validate_cameras_sequence_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_seq_project(projects)[0].project

        annotation_types = ["object-detection", "signs"]

        resp = cameras_seq_images_example.run(client=client, project=project, annotation_types=annotation_types)
        assert resp is None

    def test_create_cameras_sequence_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_seq_project(projects)[0].project
        annotation_types = ["object-detection", "signs"]

        resp = cameras_seq_images_example.run(client=client, project=project, annotation_types=annotation_types, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)
        assert isinstance(resp.scene_uuid, str)

    @pytest.mark.skip("videos are currently unsupported")
    def test_create_dangling_cameras_sequence_videos_input(self, client: IOC.KognicIOClient):
        resp = cameras_seq_videos_example.run(client=client, project=None, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)
        assert isinstance(resp.scene_uuid, str)

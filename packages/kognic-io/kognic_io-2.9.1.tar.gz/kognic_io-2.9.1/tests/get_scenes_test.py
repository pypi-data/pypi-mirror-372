from typing import List

import pytest

import examples.cameras as cameras_example
import examples.get_scenes_by_uuids as get_scenes_by_uuids_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestInput:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_get_scenes_with_uuid(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        resp = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = resp.scene_uuid

        assert isinstance(scene_uuid, str)

        scenes = get_scenes_by_uuids_example.run(client=client, scene_uuids=[scene_uuid])

        assert isinstance(scenes, list)
        assert len(scenes) == 1

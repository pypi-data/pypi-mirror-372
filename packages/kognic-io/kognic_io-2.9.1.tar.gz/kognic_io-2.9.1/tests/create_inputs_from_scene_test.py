from __future__ import absolute_import

from typing import List

import pytest

import examples.cameras as cameras_example
import examples.create_inputs_from_scene as create_inputs_from_scene_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCameras:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def get_project(self, client: IOC.KognicIOClient) -> str:
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)
        assert len(project) == 1
        return project[0].project

    def create_scene(self, client: IOC.KognicIOClient, dryrun: bool = True) -> str:
        resp = cameras_example.run(client=client, project=None, dryrun=dryrun)
        scene_uuid = resp.scene_uuid
        assert isinstance(scene_uuid, str)
        wait_for_scene_job(client, scene_uuid, fail_on_failed=True)
        return scene_uuid

    def test_validate_input_from_scene(self, client: IOC.KognicIOClient):
        project = self.get_project(client)
        scene_uuid = self.create_scene(client, dryrun=False)
        resp = create_inputs_from_scene_example.run(client=client, scene_uuid=scene_uuid, project=project, dryrun=True)
        assert resp is None

    def test_create_one_input_from_scene(self, client: IOC.KognicIOClient):
        project = self.get_project(client)
        scene_uuid = self.create_scene(client, dryrun=False)
        inputs = create_inputs_from_scene_example.run(client=client, scene_uuid=scene_uuid, project=project)
        assert len(inputs) == 1
        assert isinstance(inputs[0], Input)

    def test_create_multiple_inputs_from_scene(self, client: IOC.KognicIOClient):
        project = self.get_project(client)
        scene_uuid = self.create_scene(client, dryrun=False)
        inputs = create_inputs_from_scene_example.run(
            client=client, scene_uuid=scene_uuid, project=project, batch="batch-2"
        )  # "batch-2" has 2 requests
        assert len(inputs) == 2
        assert isinstance(inputs[0], Input)

    def test_create_multiple_inputs_from_scene_two_steps(self, client: IOC.KognicIOClient):
        project = self.get_project(client)
        scene_uuid = self.create_scene(client, dryrun=False)
        inputs = create_inputs_from_scene_example.run(client=client, scene_uuid=scene_uuid, project=project, batch="batch-1")
        assert len(inputs) == 1
        assert isinstance(inputs[0], Input)

        inputs = create_inputs_from_scene_example.run(client=client, scene_uuid=scene_uuid, project=project, batch="batch-4")
        assert len(inputs) == 1
        assert isinstance(inputs[0], Input)

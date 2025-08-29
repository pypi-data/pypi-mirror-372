from time import sleep
from typing import List

import pytest

import examples.cameras as cameras_example
import examples.get_inputs as get_inputs_example
import examples.get_inputs_by_uuids as get_inputs_by_uuids_example
import kognic.io.client as IOC
from examples.utils import wait_for_scene_job
from kognic.io.model import Project
from kognic.io.model.input.input_entry import Input as InputEntry
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestInput:
    @staticmethod
    def filter_cameras_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_get_inputs_for_project(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        project_inputs = get_inputs_example.run(client=client, project=project)

        assert isinstance(project_inputs, list)
        assert len(project_inputs) >= 1
        assert all(isinstance(input, InputEntry) for input in project_inputs)

    def test_get_inputs_with_uuid(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        resp = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = resp.scene_uuid

        wait_for_scene_job(client=client, scene_uuid=scene_uuid, fail_on_failed=True)
        assert isinstance(scene_uuid, str)
        sleep(2)  # Input creation may still be ongoing.
        inputs = get_inputs_by_uuids_example.run(client=client, scene_uuids=[scene_uuid])

        assert isinstance(inputs, list)
        assert len(inputs) == 1
        assert all(isinstance(input, InputEntry) for input in inputs)

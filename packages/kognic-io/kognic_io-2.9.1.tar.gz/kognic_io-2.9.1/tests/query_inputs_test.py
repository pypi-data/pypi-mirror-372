from typing import List

import pytest

import examples.query_inputs as query_inputs_example
from kognic.io.client import KognicIOClient
from kognic.io.model import Project
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestQueryInputs:
    @staticmethod
    def filter_cameras_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_query_inputs_for_project(self, client: KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        project_inputs = query_inputs_example.run(client=client, project=project)

        assert isinstance(project_inputs, list)
        assert len(project_inputs) >= 1
        assert all(isinstance(input, Input) for input in project_inputs)

    def test_query_inputs_for_scene_uuid(self, existing_lacs_scene_uuid: str, client: KognicIOClient):
        inputs = query_inputs_example.run(client=client, scene_uuids=[existing_lacs_scene_uuid])

        assert isinstance(inputs, list)
        assert len(inputs) == 1
        assert all(isinstance(input, Input) for input in inputs)

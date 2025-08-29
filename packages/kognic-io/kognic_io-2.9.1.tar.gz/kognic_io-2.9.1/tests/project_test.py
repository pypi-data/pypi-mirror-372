from typing import List

import pytest

import examples.get_project_batches as get_project_batches_example
import examples.get_projects as get_projects_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.get_annotation_types import run as get_annotation_types
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestProject:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_get_projects(self, client: IOC.KognicIOClient):
        projects = get_projects_example.run(client=client)
        assert isinstance(projects, list)

        assert len(projects) >= 1

    def test_get_project_batches(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        cameras_project = self.filter_cameras_project(projects)[0].project
        project_batches = get_project_batches_example.run(client=client, project=cameras_project)

        assert isinstance(project_batches, list)

        assert len(project_batches) >= 1

        assert all([cameras_project == batch.project for batch in project_batches])

    def test_get_project_annotation_types(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()

        project = self.filter_cameras_project(projects)[0].project
        annotation_types = get_annotation_types(client=client, project=project)

        assert isinstance(annotation_types, list)

        assert len(annotation_types) >= 1

        # assert "QA" not in annotation_types

    def test_get_project_batch_annotation_types(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        batch = client.project.get_project_batches(project)[0].batch

        annotation_types = get_annotation_types(client=client, project=project, batch=batch)

        assert isinstance(annotation_types, list)

        assert len(annotation_types) >= 1

        assert "QA" not in annotation_types

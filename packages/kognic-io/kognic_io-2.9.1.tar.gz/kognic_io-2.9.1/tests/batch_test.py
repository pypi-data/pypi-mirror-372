from datetime import datetime
from typing import List

import pytest

import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.create_batch import run as create_batch
from examples.get_projects import run as get_projects
from examples.publish_batch import run as publish_batch
from kognic.io.model.projects.project_batch import ProjectBatch
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestProject:
    @staticmethod
    def filter_batch_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.BatchProject][0]

    def test_create_batch(self, client: IOC.KognicIOClient):
        projects = get_projects(client=client)
        project = self.filter_batch_project(projects)

        assert isinstance(project, IAM.Project)

        now_time = str(datetime.now()).replace(" ", "_")
        project_batch = create_batch(client, project.project, f"Batch-{now_time}")

        assert isinstance(project_batch, ProjectBatch)

        assert project_batch.status == "open"

    def test_publish_batch(self, client: IOC.KognicIOClient):
        projects = get_projects(client=client)
        project = self.filter_batch_project(projects)

        now_time = str(datetime.now()).replace(" ", "_")
        created_batch = create_batch(client, project.project, f"Batch-{now_time}")

        published_batch = publish_batch(client, project.project, created_batch.batch)

        assert published_batch.status == "ready"

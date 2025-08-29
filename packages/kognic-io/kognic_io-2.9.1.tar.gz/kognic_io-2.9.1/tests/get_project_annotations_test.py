from __future__ import absolute_import

from typing import List

import pytest

import examples.get_project_annotations as get_project_annotations_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestGetAnnotations:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_get_project_annotations(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        annotations = get_project_annotations_example.run(client=client, project=project, annotation_type="signs")
        annotation_list = list(annotations)
        assert len(annotation_list) > 0

    def test_get_project_annotations_incorrect_at(self, client: IOC.KognicIOClient):
        allowed_ats = sorted(["object-detection", "signs", "QA", "2DBB"])
        with pytest.raises(Exception) as exception_info:
            projects = client.project.get_projects()
            project = self.filter_cameras_project(projects)[0].project
            a = get_project_annotations_example.run(client=client, project=project, annotation_type="object")
            list(a)
        assert (
            exception_info.value.args[0].startswith("Validation failed: Invalid annotation type sent: object. Allowed values in project:")
            and sorted(exception_info.value.args[0].split("project: [")[1].strip()[:-1].split(", ")) == allowed_ats
        )

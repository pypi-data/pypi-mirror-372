from __future__ import absolute_import

from typing import List

import pytest

import examples.tools_scene_input as tools_scene_input_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from kognic.io.tools.input_creation import InputCreationStatus
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestToolsSceneInput:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[IAM.Project]):
        return next(p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject)

    def test_tools_scene_input_without_pre_annotations(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects).project

        nr_scenes = 0
        for resp in tools_scene_input_example.run(client=client, project=project, dryrun=False, include_preannotations=False):
            assert resp.status is InputCreationStatus.CREATED
            assert resp.error is None
            nr_scenes += 1
        assert nr_scenes == 2, f"Should have created 2 scenes, not {nr_scenes}"

    def test_tools_scene_input_with_pre_annotations(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects).project

        nr_scenes = 0
        for resp in tools_scene_input_example.run(client=client, project=project, dryrun=False, include_preannotations=True):
            assert resp.status is InputCreationStatus.CREATED
            assert resp.error is None
            nr_scenes += 1
        assert nr_scenes == 2, f"Should have created 2 scenes, not {nr_scenes}"

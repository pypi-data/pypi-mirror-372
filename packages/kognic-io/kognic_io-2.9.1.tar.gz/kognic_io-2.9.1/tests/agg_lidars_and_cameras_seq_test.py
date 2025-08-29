from __future__ import absolute_import

from typing import List

import pytest

import examples.agg_lidars_and_cameras_seq as alcs_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestAggregatedLidarsAndCamerasSeq:
    @staticmethod
    def filter_alcs_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.AggregatedLidarsAndCamerasSequenceProject]

    def test_get_agg_lidars_and_cameras_seq_project(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_alcs_project(projects)
        assert len(project) == 1

    def test_validate_agg_lidars_and_cameras_seq_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_alcs_project(projects)[0].project
        resp = alcs_example.run(client=client, project=project)
        assert resp is None

    def test_create_agg_lidars_and_cameras_seq_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_alcs_project(projects)[0].project
        resp = alcs_example.run(client=client, project=project, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

    def test_validate_agg_lidars_and_cameras_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_alcs_project(projects)[0].project

        annotation_types = ["object-detection", "signs"]
        resp = alcs_example.run(client=client, project=project, annotation_types=annotation_types)
        assert resp is None

    def test_create_agg_lidars_and_cameras_with_at_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_alcs_project(projects)[0].project

        annotation_types = ["object-detection", "signs"]
        resp = alcs_example.run(client=client, project=project, annotation_types=annotation_types, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

    def test_create_dangling_agg_lidars_and_cameras_seq_input(self, client: IOC.KognicIOClient):
        resp = alcs_example.run(client=client, project=None, dryrun=False)
        assert isinstance(resp.scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

from __future__ import absolute_import

from time import sleep
from typing import List

import pytest

import examples.cameras as cameras_example
import examples.delete_input as delete_input_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestDeleteInput:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_delete_inputs(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        scene_response = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = scene_response.scene_uuid

        assert isinstance(scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=scene_uuid, fail_on_failed=True)
        sleep(2)  # Input creation may still be ongoing.
        inputs_for_scene = client.input.query_inputs(scene_uuids=[scene_uuid])
        assert len(inputs_for_scene) > 0
        nr_inputs_before = len(inputs_for_scene)

        input_uuid = inputs_for_scene[0].uuid
        delete_input_example.run(client=client, input_uuid=input_uuid)

        inputs_for_scene = client.input.query_inputs(scene_uuids=[scene_uuid])
        assert len(inputs_for_scene) == nr_inputs_before - 1

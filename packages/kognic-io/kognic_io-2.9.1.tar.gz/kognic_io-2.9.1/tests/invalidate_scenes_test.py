from __future__ import absolute_import

from time import sleep
from typing import List

import pytest

import examples.cameras as cameras_example
import examples.get_scenes_by_uuids as get_scenes_example
import examples.invalidate_scenes as invalidate_scenes_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from kognic.io.model import SceneInvalidatedReason
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestInvalidateScenes:
    @staticmethod
    def filter_cameras_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_invalidate_scenes(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        scene_response = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = scene_response.scene_uuid

        assert isinstance(scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=scene_uuid, fail_on_failed=True)

        invalidate_scenes_example.run(client=client, scene_uuid=scene_uuid, reason=SceneInvalidatedReason.BAD_CONTENT)
        sleep(2)

        # Verify that the scene was invalidated
        scenes = get_scenes_example.run(client=client, scene_uuids=[scene_uuid])
        assert scenes[0].status == "invalidated:broken-input"
        sleep(3)

        # Verify that inputs for the scene were deleted
        inputs_for_scene = client.input.query_inputs(scene_uuids=[scene_uuid])
        assert len(inputs_for_scene) == 0

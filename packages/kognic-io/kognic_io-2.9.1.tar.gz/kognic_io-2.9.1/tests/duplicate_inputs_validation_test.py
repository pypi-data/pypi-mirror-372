from typing import List
from uuid import uuid4

import pytest

import kognic.io.client as IOC
import kognic.io.model.scene.cameras as CamerasModel
from examples.cameras import base_dir
from examples.utils import wait_for_scene_job
from kognic.io.model import InputStatus
from kognic.io.model.projects import Project
from kognic.io.model.scene.resources import Image
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestDuplicateInputsValidation:
    """
    Tests that validation of duplication of inputs works correctly
    """

    @staticmethod
    def filter_cameras_project(projects: List[Project]):
        return next(p for p in projects if p.project == TestProjects.CamerasProject)

    @staticmethod
    def build_scene(external_id: str):
        metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}
        return CamerasModel.Cameras(
            external_id=external_id,
            frame=CamerasModel.Frame(
                images=[
                    Image(
                        filename=str(base_dir) + "/resources/img_RFC01.jpg",
                        sensor_name="RFC01",
                    ),
                    Image(
                        filename=str(base_dir) + "/resources/img_RFC02.jpg",
                        sensor_name="RFC02",
                    ),
                ]
            ),
            metadata=metadata,
        )

    def test_sync_validation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects).project
        external_id = f"duplicate-inputs-sync-validation-{uuid4()}"
        scene = self.build_scene(external_id=external_id)

        # Create first input
        resp = client.cameras.create(scene, project=project, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)

        # Create second input
        with pytest.raises(RuntimeError) as excinfo:
            client.cameras.create(scene, project=project, dryrun=False)
        assert "Duplicate inputs for external id" in str(excinfo.value)

    def test_async_validation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects).project
        external_id = f"duplicate-inputs-async-validation-{uuid4()}"
        scene = self.build_scene(external_id=external_id)

        # Create both inputs
        resp1 = client.cameras.create(scene, project=project, dryrun=False)
        resp2 = client.cameras.create(scene, project=project, dryrun=False)

        # Wait
        status1 = wait_for_scene_job(client=client, scene_uuid=resp1.scene_uuid, fail_on_failed=False)
        status2 = wait_for_scene_job(client=client, scene_uuid=resp2.scene_uuid, fail_on_failed=False)

        assert {status1, status2} == {InputStatus.Created, InputStatus.Failed}  # One scene should be created, the other should fail

        failed_scene_uuid = resp1.scene_uuid if status1 == InputStatus.Failed else resp2.scene_uuid
        failed_scene = client.scene.get_scenes_by_uuids(scene_uuids=[failed_scene_uuid])[0]
        assert "Duplicate inputs for external id" in failed_scene.error_message

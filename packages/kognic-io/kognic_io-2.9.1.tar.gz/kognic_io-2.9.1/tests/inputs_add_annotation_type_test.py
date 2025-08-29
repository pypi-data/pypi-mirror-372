from __future__ import absolute_import

import time
from typing import List

import pytest

import examples.add_annotation_type as add_annotation_type
import examples.cameras as cameras_example
import examples.get_inputs_by_uuids as get_inputs_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCameras:
    @staticmethod
    def filter_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.AnnotationTypeProject]

    def test_invalidate_inputs(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_project(projects)[0].project
        resp = cameras_example.run(client=client, project=project, annotation_types=["first"], dryrun=False)

        assert isinstance(resp.scene_uuid, str)
        scene_uuid = resp.scene_uuid

        inputs = None
        for _ in range(12):
            inputs = get_inputs_example.run(client=client, scene_uuids=[scene_uuid])

            if len(inputs) == 1 and inputs[0].status == "created":
                print("Input created")
                break

            time.sleep(1)

        assert isinstance(inputs, list)
        assert len(inputs) == 1
        assert inputs[0].status == "created", f"Input has not been created, has status {inputs[0].status}"

        add_annotation_type.run(client=client, scene_uuid=scene_uuid, annotation_type="second")

        updated_input = get_inputs_example.run(client=client, scene_uuids=[scene_uuid])[0]

        assert "second" in updated_input.annotation_types

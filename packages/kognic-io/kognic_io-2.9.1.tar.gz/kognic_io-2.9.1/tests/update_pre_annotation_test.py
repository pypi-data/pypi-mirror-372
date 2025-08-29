from __future__ import absolute_import

import pytest

import examples.update_pre_annotation as update_pre_annotation_example
import kognic.io.client as IOC
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration
class TestUpdatePreAnnotation:
    """
    Test that pre-annotation UUIDs on existing inputs can be updated when the scene has multiple pre-annotations.
    """

    def test_update_pre_annotation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        cameras_sequence_project = [p for p in projects if p.project == TestProjects.CamerasSequenceProject][0].project

        created_input = update_pre_annotation_example.run(client=client, cameras_sequence_project=cameras_sequence_project)
        assert isinstance(created_input, Input)

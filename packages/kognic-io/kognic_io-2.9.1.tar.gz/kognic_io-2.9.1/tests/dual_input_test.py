from __future__ import absolute_import

from typing import List

import pytest

import examples.dual_input as dual_input_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeqWithDualInputs:
    """
    This is a test for dual-purpose use of a single scene, with different pre-annotations: once as LCS and once
    as an ALCS, across two requests in the same workspace.
    """

    @staticmethod
    def filter_project(projects: List[IAM.Project], t: TestProjects):
        return [p for p in projects if p.project == t][0].project

    def test_create_dual_inputs(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        lcs_project = self.filter_project(projects, TestProjects.LidarsAndCamerasSequenceProject)
        alcs_project = self.filter_project(projects, TestProjects.AggregatedLidarsAndCamerasSequenceProject)

        created_inputs = dual_input_example.run(client=client, sequence_project=lcs_project, aggregated_sequence_project=alcs_project)
        assert isinstance(created_inputs, list) and len(created_inputs) == 2
        assert isinstance(created_inputs[0], Input)
        assert isinstance(created_inputs[1], Input)
        assert created_inputs[0] != created_inputs[1]

from typing import List, Optional

import pytest

from examples.add_review import run as run_add_review_example
from kognic.io.client import KognicIOClient
from kognic.io.model import Project
from kognic.io.model.review.review import (
    Review,
    ReviewErrorType,
    ReviewResponse,
)
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestReview:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject]

    def _get_open_label_uuid(self, client: KognicIOClient) -> Optional[str]:
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        annotation_type = "object-detection"

        for a in client.annotation.get_project_annotations(project=project, annotation_type=annotation_type):
            return a.content["openlabel"]["metadata"]["uuid"]

    def test_post_empty_review(self, client: KognicIOClient):
        # Specific to the organization
        error_type_id = "21038f00-e105-4738-88b4-ef210cf4bdfc"

        # The annotation needs to belong to a request that has a review policy
        delivery_ready_open_label_uuid = self._get_open_label_uuid(client)
        review = run_add_review_example(client, delivery_ready_open_label_uuid, error_type_id)
        assert isinstance(review, ReviewResponse)

    def test_get_review(self, client: KognicIOClient):
        review_id = "a6f644da-f89e-492a-a58c-0d9f4140742a"
        review = client.review.get_review(review_id)
        assert isinstance(review, Review)

    def test_get_error_types(self, client: KognicIOClient):
        error_types = client.review.get_error_types()
        assert len(error_types) > 0
        for error_type in error_types:
            assert isinstance(error_type, ReviewErrorType)

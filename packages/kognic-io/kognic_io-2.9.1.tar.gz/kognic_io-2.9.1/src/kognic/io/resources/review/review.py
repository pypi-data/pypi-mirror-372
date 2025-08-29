import logging
from typing import List

from kognic.base_clients.http_client import HttpClient
from kognic.io.model.review.review import Review, ReviewErrorType, ReviewRequest, ReviewResponse

log = logging.getLogger(__name__)


class ReviewResource:
    def __init__(self, client: HttpClient):
        self._client = client

    def create_review(self, open_label_uuid: str, body: ReviewRequest) -> ReviewResponse:
        """
        Create a review for an annotation.
        Depending on the review request, this might reject the annotation and create a correction task.

        :param open_label_uuid: The UUID of the OpenLABEL
        :param body: The review content
        :returns ReviewResponse:
        """
        response = self._client.post(f"v1/annotations/{open_label_uuid}/review", json=body.to_dict())
        return ReviewResponse.from_json(response)

    def get_review(self, review_id: str) -> Review:
        """
        Get a review by ID

        :param review_id: The ID of the specific review
        :returns Review: The content of the review
        """
        response = self._client.get(f"v1/reviews/{review_id}")
        return Review.from_json(response)

    def get_error_types(self) -> List[ReviewErrorType]:
        """
        Get all available error types to use when creating a review

        :returns List[ReviewErrorType]: List of error types
        """
        response = self._client.get("v1/reviews/error-types")
        return [ReviewErrorType.from_json(entry) for entry in response]

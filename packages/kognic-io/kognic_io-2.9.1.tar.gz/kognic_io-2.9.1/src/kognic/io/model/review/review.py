from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from kognic.base_clients.models import BaseSerializer


class AddFeedbackItemPin(BaseSerializer):
    x: float
    y: float
    z: Optional[float]


class AddFeedbackItemSuggestedProperty(BaseSerializer):
    property_name: str
    suggested_property_value: str


class AddFeedbackItem(BaseSerializer):
    sensor_id: Optional[str] = None
    frame_id: Optional[str] = None  # in our OpenLabel files this is frame.frame_properties.external_id
    object_id: Optional[str] = None
    pin: Optional[AddFeedbackItemPin] = None
    description: Optional[str] = None
    suggested_property: Optional[AddFeedbackItemSuggestedProperty] = None
    error_type_id: str
    metadata: Optional[Dict[str, str]] = None


class ReviewWorkflowEnum(str, Enum):
    CORRECT = "correct"


class ReviewRequest(BaseSerializer):
    feedback_items: List[AddFeedbackItem]
    workflow: ReviewWorkflowEnum
    accepted: bool


class ReviewResponse(BaseSerializer):
    created_review_id: str


class ReviewMember(BaseSerializer):
    sensor_id: Optional[str] = None
    frame_id: Optional[str] = None  # in our OpenLabel files this is frame.frame_properties.external_id
    object_id: Optional[str] = None
    comments: Optional[List[str]] = None
    pin: Optional[AddFeedbackItemPin] = None
    description: Optional[str] = None
    suggested_properties: Optional[List[AddFeedbackItemSuggestedProperty]] = None
    error_type_id: str
    error_type_name: str
    invalid: bool
    metadata: Optional[Dict[str, str]] = None
    corrected: bool
    resolved: bool
    created_at: datetime


class Review(BaseSerializer):
    id: str
    members: List[ReviewMember]
    input_uuid: str
    phase_id: Optional[str] = None


class ReviewErrorType(BaseSerializer):
    error_type_id: str
    name: str
    pin_allowed: bool
    object_allowed: bool

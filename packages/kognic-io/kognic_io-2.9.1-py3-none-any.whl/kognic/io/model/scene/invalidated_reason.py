from enum import Enum


class SceneInvalidatedReason(str, Enum):
    BAD_CONTENT = "bad-content"
    DUPLICATE = "duplicate"
    INCORRECTLY_CREATED = "incorrectly-created"

from typing import Dict

from deprecated import deprecated
from pydantic import Field

from kognic.io.model.base_serializer import BaseSerializer


class InitializedSceneJob(BaseSerializer):
    scene_uuid: str


class SceneJobCreated(BaseSerializer):
    scene_uuid: str = Field(alias="internalId")
    files: Dict[str, str]

    def __str__(self):
        return f"{self.__class__.__name__}(scene_uuid={self.scene_uuid}, files={{...}})"


class CreateSceneResponse(BaseSerializer):
    scene_uuid: str

    @staticmethod
    def from_scene_job_created(scene_job: SceneJobCreated):
        return CreateSceneResponse(scene_uuid=scene_job.scene_uuid)

    @property
    @deprecated(reason="This is deprecated. Use `scene_uuid` instead of `input_uuid`")
    def input_uuid(self):
        return self.scene_uuid

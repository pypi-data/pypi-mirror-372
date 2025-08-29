from deprecated import deprecated

from kognic.io.model.scene.scene_job import CreateSceneResponse


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class CreateInputResponse(CreateSceneResponse):
    pass

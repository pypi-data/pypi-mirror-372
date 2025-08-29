from deprecated import deprecated

from kognic.io.model.scene.resources.resource import MissingFileError as SceneMissingFileError
from kognic.io.model.scene.resources.resource import Resource as SceneResource


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class MissingFileError(SceneMissingFileError):
    pass


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class Resource(SceneResource):
    pass

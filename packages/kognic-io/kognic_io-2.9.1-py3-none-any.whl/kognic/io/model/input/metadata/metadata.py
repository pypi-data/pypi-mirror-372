from deprecated import deprecated

from kognic.io.model.scene.metadata.metadata import FrameMetaData as SceneFrameMetaData
from kognic.io.model.scene.metadata.metadata import MetaData as SceneMetaData


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class MetaData(SceneMetaData):
    pass


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class FrameMetaData(SceneFrameMetaData):
    pass

from deprecated import deprecated

from kognic.io.model.scene.resources.video import VideoFrame as SceneVideoFrame
from kognic.io.model.scene.resources.video import VideoTS as SceneVideoTS


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class VideoTS(SceneVideoTS):
    pass


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class VideoFrame(SceneVideoFrame):
    pass

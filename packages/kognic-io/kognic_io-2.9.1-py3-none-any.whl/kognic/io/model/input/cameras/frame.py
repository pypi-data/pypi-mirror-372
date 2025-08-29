from deprecated import deprecated

from kognic.io.model.scene.cameras.frame import Frame as SceneFrame


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class Frame(SceneFrame):
    pass

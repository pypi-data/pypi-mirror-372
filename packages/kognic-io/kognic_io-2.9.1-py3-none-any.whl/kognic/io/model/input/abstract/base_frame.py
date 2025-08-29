from deprecated import deprecated

from kognic.io.model.scene.abstract.base_frame import BaseFrame as BaseSceneFrame


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class BaseFrame(BaseSceneFrame):
    pass

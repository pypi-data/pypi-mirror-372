from deprecated import deprecated

from kognic.io.model.scene.abstract.base_scene import BaseScene


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class BaseInput(BaseScene):
    pass

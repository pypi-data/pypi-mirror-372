from deprecated import deprecated

from kognic.io.model.scene import LidarsAndCameras as LidarsAndCamerasScene

from .frame import Frame  # noqa: F401


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class LidarsAndCameras(LidarsAndCamerasScene):
    pass

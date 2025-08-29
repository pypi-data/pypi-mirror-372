from deprecated import deprecated

from kognic.io.model.scene.resources.point_cloud import PointCloud as ScenePointCloud


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class PointCloud(ScenePointCloud):
    pass

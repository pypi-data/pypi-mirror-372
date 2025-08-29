from deprecated import deprecated

from kognic.io.model.scene.resources.image import Image as SceneImage
from kognic.io.model.scene.resources.image import ImageMetadata as SceneImageMetadata


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class ImageMetadata(SceneImageMetadata):
    pass


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class Image(SceneImage):
    pass

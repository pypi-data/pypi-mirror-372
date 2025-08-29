from deprecated import deprecated

from kognic.io.model.scene.abstract.sequence_frame import SequenceFrame as SceneSequenceFrame


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class SequenceFrame(SceneSequenceFrame):
    pass

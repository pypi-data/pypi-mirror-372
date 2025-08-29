from deprecated import deprecated

from kognic.io.model.scene.feature_flags import FeatureFlags as SceneFeatureFlags


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class FeatureFlags(SceneFeatureFlags):
    pass

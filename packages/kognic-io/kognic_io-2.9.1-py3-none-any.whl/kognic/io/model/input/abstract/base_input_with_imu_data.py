from deprecated import deprecated

from kognic.io.model.scene.abstract.base_scene_with_imu_data import BaseSceneWithIMUData


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class BaseInputWithIMUData(BaseSceneWithIMUData):
    pass

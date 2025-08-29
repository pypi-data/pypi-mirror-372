from deprecated import deprecated

from kognic.io.model.scene.sensor_specification import CameraSettings as SceneCameraSettings
from kognic.io.model.scene.sensor_specification import SensorSpecification as SceneSensorSpecification


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class CameraSettings(SceneCameraSettings):
    pass


@deprecated(reason="This has been moved to kognic.io.model.scene and will be removed in the future")
class SensorSpecification(SceneSensorSpecification):
    pass

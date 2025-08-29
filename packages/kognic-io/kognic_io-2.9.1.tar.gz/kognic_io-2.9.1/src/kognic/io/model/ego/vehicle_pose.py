from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.calibration import Position, RotationQuaternion


class EgoVehiclePose(BaseSerializer):
    """Both `position` and `rotation` are with respect to the local coordinate system (LCS)."""

    position: Position
    rotation: RotationQuaternion

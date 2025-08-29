from __future__ import annotations

from enum import Enum, EnumMeta
from typing import Dict, Set


class FeatureFlags:
    """
    Holds a set of flags to control optional features of the input creation process.
    """

    class PointCloudFeatures(Enum):
        MOTION_COMPENSATION = "shouldMotionCompensate"

    def __init__(self, *flags):
        self.flags = set(flags)

    @staticmethod
    def defaults() -> FeatureFlags:
        return FeatureFlags(FeatureFlags.PointCloudFeatures.MOTION_COMPENSATION)

    @staticmethod
    def _all() -> Set[Enum]:
        all_flags = set()
        for flag_set in FeatureFlags.__dict__.values():
            if isinstance(flag_set, EnumMeta):
                all_flags.update([flag_set[m] for m in flag_set.__members__])
        return all_flags

    def to_dict(self) -> Dict[str, bool]:
        return dict([(a.value, a in self.flags) for a in FeatureFlags._all()])

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([type(f).__name__ + '.' + f.name for f in self.flags])})"

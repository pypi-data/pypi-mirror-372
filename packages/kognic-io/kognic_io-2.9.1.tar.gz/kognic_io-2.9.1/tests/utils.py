from enum import Enum


class TestProjects(str, Enum):
    BatchProject = "batch-project"
    AnnotationTypeProject = "annotation-types"
    CamerasProject = "cameras-project"
    CamerasSequenceProject = "cameras_sequence-project"
    LidarsAndCamerasProject = "lidars_and_cameras-project"
    LidarsAndCamerasSequenceProject = "lidars_and_cameras_sequence-project"
    LidarsProject = "lidars-project"
    LidarsSequenceProject = "lidars_sequence-project"
    AggregatedLidarsAndCamerasSequenceProject = "aggregated_lidars_and_cameras_sequence-project"


TestProjects.__test__ = False

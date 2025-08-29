from __future__ import absolute_import

import os.path
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

import pytest

import kognic.io.model.scene.lidars_and_cameras_sequence as LCSM
import kognic.io.model.scene.resources as ResourceModel
import kognic.openlabel.models as OLM
from examples.calibration.calibration import create_sensor_calibration
from examples.utils import wait_for_scene_job
from kognic.io.client import KognicIOClient
from kognic.io.model import Project
from kognic.io.model.input.input import Input
from tests.utils import TestProjects

LIDAR1 = "RFL01"
LIDAR2 = "RFL02"
CAMERA1 = "RFC01"
CAMERA2 = "RFC02"
EXAMPLES_PATH = str(Path(os.path.dirname(__file__)).parent / "examples")

BBOX_NAME = "Bbox-1"
CUBOID_NAME = "Cuboid-1"


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeqWithSparsePreAnnotations:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject]

    def run_test_with_sparse_pre_annotation(self, client: KognicIOClient, pre_annotation: OLM.OpenLabelAnnotation):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project

        # Create calibration
        calibration_spec = create_sensor_calibration(f"Collection {datetime.now()}", [LIDAR1, LIDAR2], [CAMERA1, CAMERA2])
        created_calibration = client.calibration.create_calibration(calibration_spec)
        lidars_and_cameras_seq = build_lcs_scene(created_calibration.id)

        # Create Scene but not input since we don't provide project or batch
        scene_response = client.lidars_and_cameras_sequence.create(lidars_and_cameras_seq, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=scene_response.scene_uuid, fail_on_failed=True)

        client.pre_annotation.create(scene_uuid=scene_response.scene_uuid, pre_annotation=pre_annotation, dryrun=False)
        created_inputs = client.lidars_and_cameras_sequence.create_from_scene(
            scene_uuid=scene_response.scene_uuid, annotation_types=None, project=project, dryrun=False
        )
        assert isinstance(created_inputs, list) and len(created_inputs) >= 1
        assert isinstance(created_inputs[0], Input)

    def test_create_lcs_with_sparse_pre_annotation_interpolated(self, client: KognicIOClient):
        # Test for creating sparse pre-annotation with interpolated property
        pre_annotation = build_sparse_pre_annotation_with_interpolated()
        self.run_test_with_sparse_pre_annotation(client, pre_annotation)

    def test_create_lcs_with_sparse_pre_annotation_od_pointers(self, client: KognicIOClient):
        # Test for creating sparse pre-annotations with object data pointers
        pre_annotation = build_sparse_pre_annotation_with_od_pointers()
        self.run_test_with_sparse_pre_annotation(client, pre_annotation)


def build_sparse_pre_annotation_with_interpolated() -> OLM.OpenLabelAnnotation:
    object_uuid1 = str(uuid4())
    object_uuid2 = str(uuid4())

    frame0 = OLM.Frame(
        frame_properties=OLM.FrameProperties(streams={LIDAR1: OLM.Stream(), CAMERA1: OLM.Stream()}, timestamp=0, external_id=str(100 * 0)),
        objects={
            object_uuid1: build_frame_object_interpolated(0, False, "Medium"),
            object_uuid2: OLM.Objects(
                object_data=OLM.ObjectData(point2d=build_point_container(CAMERA1, [OLM.Boolean(name="interpolated", val=False)])),
            ),
        },
    )
    frame1 = OLM.Frame(
        frame_properties=OLM.FrameProperties(
            streams={LIDAR1: OLM.Stream(), CAMERA1: OLM.Stream()}, timestamp=100, external_id=str(100 * 100)
        ),
        objects={
            object_uuid1: build_frame_object_interpolated(5, True, "Light"),
            object_uuid2: OLM.Objects(
                object_data=OLM.ObjectData(point2d=build_point_container(CAMERA1, [OLM.Boolean(name="interpolated", val=True)])),
            ),
        },
    )
    frame2 = OLM.Frame(
        frame_properties=OLM.FrameProperties(
            streams={LIDAR1: OLM.Stream(), CAMERA1: OLM.Stream()}, timestamp=200, external_id=str(100 * 200)
        ),
        objects={
            object_uuid1: build_frame_object_interpolated(10, True, "Light"),
            object_uuid2: OLM.Objects(
                object_data=OLM.ObjectData(point2d=build_point_container(CAMERA1, [OLM.Boolean(name="interpolated", val=True)])),
            ),
        },
    )
    frame3 = OLM.Frame(
        frame_properties=OLM.FrameProperties(
            streams={LIDAR1: OLM.Stream(), CAMERA1: OLM.Stream()}, timestamp=300, external_id=str(100 * 300)
        ),
        objects={
            object_uuid1: build_frame_object_interpolated(5, False, "Light"),
            object_uuid2: OLM.Objects(
                object_data=OLM.ObjectData(point2d=build_point_container(CAMERA1, [OLM.Boolean(name="interpolated", val=False)])),
            ),
        },
    )

    return OLM.OpenLabelAnnotation(
        openlabel=OLM.Openlabel(
            metadata=OLM.Metadata(name="empty pre-annotation", schema_version=OLM.SchemaVersion.field_1_0_0),
            objects={
                object_uuid1: OLM.Object(
                    name="MyNameIsBox", type="SpaceShip", object_data=OLM.ObjectData(text=[OLM.Text(name="faction", val="empire")])
                ),
                object_uuid2: OLM.Object(name="PointContainer", type="Moons"),
            },
            frames={
                "0": frame0,
                "1": frame1,
                "2": frame2,
                "3": frame3,
            },
            frame_intervals=[OLM.FrameInterval(frame_start=0, frame_end=2)],
            streams={LIDAR1: OLM.Stream(type=OLM.StreamTypes.lidar), CAMERA1: OLM.Stream(type=OLM.StreamTypes.camera)},
        )
    )


def build_sparse_pre_annotation_with_od_pointers() -> OLM.OpenLabelAnnotation:
    object_uuid = str(uuid4())
    od_pointers = {
        CUBOID_NAME: OLM.ElementDataPointer(
            type=OLM.DataTypes.cuboid,
            frame_intervals=[OLM.FrameInterval(frame_start=0, frame_end=3)],
        ),
        BBOX_NAME: OLM.ElementDataPointer(
            type=OLM.DataTypes.bbox,
            frame_intervals=[OLM.FrameInterval(frame_start=0, frame_end=3)],
        ),
    }

    root_object = OLM.Object(
        name="MyNameIsBox",
        type="SpaceShip",
        object_data=OLM.ObjectData(text=[OLM.Text(name="faction", val="empire")]),
        object_data_pointers=od_pointers,
    )

    return OLM.OpenLabelAnnotation(
        openlabel=OLM.Openlabel(
            metadata=OLM.Metadata(name="empty pre-annotation", schema_version=OLM.SchemaVersion.field_1_0_0),
            objects={object_uuid: root_object},
            frames={
                "0": build_frame(0, object_uuid, build_frame_object_od_pointer(0, False, "Medium")),
                "1": build_frame(100, object_uuid, build_frame_object_od_pointer(5, True, "Light")),
                "2": build_frame(200, object_uuid, build_frame_object_od_pointer(10, True, "Light")),
                "3": build_frame(300, object_uuid, build_frame_object_od_pointer(5, False, "Light")),
            },
            frame_intervals=[OLM.FrameInterval(frame_start=0, frame_end=2)],
            streams={LIDAR1: OLM.Stream(type=OLM.StreamTypes.lidar), CAMERA1: OLM.Stream(type=OLM.StreamTypes.camera)},
        )
    )


def build_frame(timestamp: int, object_uuid: str, frame_object: OLM.Objects) -> OLM.Frame:
    return OLM.Frame(
        frame_properties=OLM.FrameProperties(
            streams={LIDAR1: OLM.Stream(), CAMERA1: OLM.Stream()}, timestamp=timestamp, external_id=str(100 * timestamp)
        ),
        objects={object_uuid: frame_object},
    )


def build_frame_object_interpolated(offset: int, interpolated: bool, occlusion: str) -> OLM.Objects:
    return OLM.Objects(
        object_data=OLM.ObjectData(
            cuboid=[build_cuboid(offset, [OLM.Boolean(name="interpolated", val=interpolated)])], bbox=[build_bbox(offset, occlusion)]
        ),
    )


def build_frame_object_od_pointer(offset: int, interpolated: bool, occlusion: str) -> OLM.Objects:
    return OLM.Objects(
        object_data=OLM.ObjectData(
            cuboid=[build_cuboid(offset, [])] if not interpolated else [],
            bbox=[build_bbox(offset, occlusion)],
        ),
    )


def build_cuboid(offset: int, boolean_props: List[OLM.Boolean]) -> OLM.Cuboid:
    return OLM.Cuboid(
        attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=LIDAR1)], boolean=boolean_props),
        name=CUBOID_NAME,
        val=[
            -0.37240600585938 + offset,
            -0.776424407958984 + offset,
            0.0018768074223771691 + offset,
            -0.008678210841102768,
            0.011558858557049027,
            0.2286106806721516,
            0.9734106215406072,
            1.767102435869269,
            4.099334155319101,
            1.3691029802958168,
        ],
    )


def build_bbox(offset: int, occlusion: str) -> OLM.Bbox:
    return OLM.Bbox(
        attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=CAMERA1), OLM.Text(name="occlusion_ratio", val=occlusion)]),
        name=BBOX_NAME,
        val=[100 + 10 * offset, 100 + 10 * offset, 100, 200],
    )


def build_point_container(camera: str, boolean_props: List[OLM.Boolean]) -> List[OLM.Point2d]:
    return [
        OLM.Point2d(
            attributes=OLM.Attributes(
                text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="LeftShoulder")], boolean=boolean_props
            ),
            name="point-1234",
            val=[910.3, 635.1],
        ),
        OLM.Point2d(
            attributes=OLM.Attributes(
                text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="RightShoulder")], boolean=boolean_props
            ),
            name="point-5678",
            val=[920.3, 623.1],
        ),
        OLM.Point2d(
            attributes=OLM.Attributes(
                text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="Head")], boolean=boolean_props
            ),
            name="point-2468",
            val=[920.3, 639.1],
        ),
    ]


def build_scene_frame(relative_timestamp: int) -> LCSM.Frame:
    return LCSM.Frame(
        frame_id=str(relative_timestamp),
        relative_timestamp=relative_timestamp,
        point_clouds=[
            ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL01.csv", sensor_name=LIDAR1),
            ResourceModel.PointCloud(filename=EXAMPLES_PATH + "/resources/point_cloud_RFL02.csv", sensor_name=LIDAR2),
        ],
        images=[
            ResourceModel.Image(filename=EXAMPLES_PATH + "/resources/img_RFC01.jpg", sensor_name=CAMERA1),
            ResourceModel.Image(filename=EXAMPLES_PATH + "/resources/img_RFC02.jpg", sensor_name=CAMERA2),
        ],
    )


def build_lcs_scene(calibration_id: str) -> LCSM.LidarsAndCamerasSequence:
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicleId": "abg"}

    return LCSM.LidarsAndCamerasSequence(
        external_id=f"LCS-with-sparse-pre-annotation-example-{str(uuid4())[:8]}",
        frames=[build_scene_frame(ts) for ts in [0, 100, 200, 300]],
        calibration_id=calibration_id,
        metadata=metadata,
    )

from __future__ import absolute_import

from typing import List
from uuid import uuid4

import pytest

import kognic.io.model as KOM
import kognic.openlabel.models as OLM
from examples import create_preannotation_with_confidence
from kognic.io.client import KognicIOClient
from tests.utils import TestProjects


def build_cuboid(lidar: str) -> OLM.Cuboid:
    return OLM.Cuboid(
        attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=lidar)]),
        name="Cuboid-1",
        val=[
            -0.37240600585938,
            -0.776424407958984,
            0.0018768074223771691,
            -0.008678210841102768,
            0.011558858557049027,
            0.2286106806721516,
            0.9734106215406072,
            1.767102435869269,
            4.099334155319101,
            1.3691029802958168,
        ],
    )


def build_pre_annotation() -> OLM.OpenLabelAnnotation:
    lidar_sensor1 = "RFL01"
    cam_sensor1 = "RFC01"
    cam_sensor2 = "RFC02"

    object_uuid1 = str(uuid4())

    return OLM.OpenLabelAnnotation(
        openlabel=OLM.Openlabel(
            metadata=OLM.Metadata(name="empty pre-annotation", schema_version=OLM.SchemaVersion.field_1_0_0),
            objects={
                object_uuid1: OLM.Object(name="MultiPolygon", type="SpaceShip"),
            },
            frames={
                "0": OLM.Frame(
                    frame_properties=OLM.FrameProperties(
                        streams={
                            lidar_sensor1: OLM.Stream(),
                            cam_sensor1: OLM.Stream(),
                            cam_sensor2: OLM.Stream(),
                        },
                        timestamp=0,
                        external_id="1",
                    ),
                    objects={
                        object_uuid1: OLM.Objects(
                            object_data=OLM.ObjectData(
                                cuboid=[build_cuboid(lidar_sensor1)],
                                text=[OLM.Text(name="ship_type", val="star_destroyer")],
                                boolean=[
                                    OLM.Boolean(
                                        name="hasNestedProperties",
                                        val=True,
                                        attributes=OLM.Attributes(
                                            num=[OLM.Num(name="confidence", val=1.0)],
                                        ),
                                    )
                                ],
                            )
                        ),
                    },
                )
            },
            frame_intervals=[
                OLM.FrameInterval(frame_start=0, frame_end=0),
            ],
            streams={
                lidar_sensor1: OLM.Stream(type=OLM.StreamTypes.lidar),
                cam_sensor1: OLM.Stream(type=OLM.StreamTypes.camera),
                cam_sensor2: OLM.Stream(type=OLM.StreamTypes.camera),
            },
        )
    )


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasWithPreAnnotations:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[KOM.Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasProject]

    def test_create_lidars_cameras_with_pre_annotation(self, client: KognicIOClient):
        pre_annotation = build_pre_annotation()

        create_preannotation_with_confidence.run(
            client=client,
            dryrun=False,
            pre_annotation=pre_annotation,
        )

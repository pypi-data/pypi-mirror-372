from __future__ import absolute_import

from typing import List
from uuid import uuid4

import pytest

import examples.lidars_and_cameras_seq_with_pre_annotations as lidars_cameras_seq_with_pre_annotations_example
import kognic.io.client as IOC
import kognic.io.model as IAM
import kognic.openlabel.models as OLM
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeqWithPreAnnotations:
    @staticmethod
    def filter_lidar_and_cameras_seq_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.LidarsAndCamerasSequenceProject]

    def test_create_lidars_cameras_seq_with_pre_annotation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project

        object_uuid = str(uuid4())
        lidar_sensor = "RFL01"
        cam_sensor = "RFC01"

        pre_annotation = OLM.OpenLabelAnnotation(
            openlabel=OLM.Openlabel(
                metadata=OLM.Metadata(name="empty pre-annotation", schema_version=OLM.SchemaVersion.field_1_0_0),
                objects={object_uuid: OLM.Object(name="MyNameIsBox", type="SpaceShip")},
                frames={
                    "0": OLM.Frame(
                        frame_properties=OLM.FrameProperties(streams={lidar_sensor: OLM.Stream()}, timestamp=0, external_id="1"),
                        objects={
                            object_uuid: OLM.Objects(
                                object_data=OLM.ObjectData(
                                    cuboid=[
                                        OLM.Cuboid(
                                            attributes=OLM.Attributes(
                                                text=[
                                                    OLM.Text(name="stream", val=lidar_sensor),
                                                ]
                                            ),
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
                                    ],
                                    bbox=[
                                        OLM.Bbox(
                                            attributes=OLM.Attributes(
                                                text=[
                                                    OLM.Text(name="stream", val=cam_sensor),
                                                    OLM.Text(name="occlusion_ratio", val="Light"),
                                                ]
                                            ),
                                            name="Bounding-box-1",
                                            val=[1.0, 1.0, 4.0, 3.0],
                                        )
                                    ],
                                    text=[OLM.Text(name="ship_type", val="star_destroyer")],
                                )
                            )
                        },
                    )
                },
                frame_intervals=[
                    OLM.FrameInterval(frame_start=0, frame_end=0),
                ],
                streams={
                    lidar_sensor: OLM.Stream(type=OLM.StreamTypes.lidar),
                    cam_sensor: OLM.Stream(type=OLM.StreamTypes.camera),
                },
            )
        )
        created_inputs = lidars_cameras_seq_with_pre_annotations_example.run(
            client=client, project=project, dryrun=False, pre_annotation=pre_annotation
        )
        assert isinstance(created_inputs, list) and len(created_inputs) >= 1
        assert isinstance(created_inputs[0], Input)

    def test_validate_lidars_cameras_seq_with_empty_pre_annotation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        resp = lidars_cameras_seq_with_pre_annotations_example.run(client=client, project=project)
        assert resp is None

    def test_create_lidars_cameras_seq_with_empty_pre_annotation(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        created_inputs = lidars_cameras_seq_with_pre_annotations_example.run(
            client=client,
            project=project,
            dryrun=False,
        )

        assert isinstance(created_inputs, list) and len(created_inputs) >= 1
        assert isinstance(created_inputs[0], Input)

from __future__ import absolute_import

from typing import List
from uuid import uuid4

import pytest

import examples.lidars_and_cameras_with_pre_annotations as lidars_cameras_with_pre_annotations_example
import kognic.io.model as KOM
import kognic.openlabel.models as OLM
from kognic.io.client import KognicIOClient
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


def build_point2d(camera: str, coordinates: List[float]) -> OLM.Point2d:
    return OLM.Point2d(
        attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="LineGeometricTypePoint")]),
        name="point-1234",
        val=coordinates,
    )


def build_point_container(camera: str) -> List[OLM.Point2d]:
    return [
        OLM.Point2d(
            attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="LeftShoulder")]),
            name="point-1234",
            val=[910.3, 635.1],
        ),
        OLM.Point2d(
            attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="RightShoulder")]),
            name="point-5678",
            val=[920.3, 623.1],
        ),
        OLM.Point2d(
            attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=camera), OLM.Text(name="point_class", val="Head")]),
            name="point-2468",
            val=[920.3, 639.1],
        ),
    ]


def build_polygon_no_hole(camera: str, include_polygon_id: bool) -> OLM.Poly2d:
    return OLM.Poly2d(
        attributes=OLM.Attributes(
            boolean=[OLM.Boolean(name="is_hole", val=False), OLM.Boolean(name="unclear", val=False)],
            text=[OLM.Text(name="stream", val=camera)] + ([OLM.Text(name="polygon_id", val="40cb6053")] if include_polygon_id else []),
        ),
        closed=True,
        mode="MODE_POLY2D_ABSOLUTE",
        name="poly2d-40cb6053-0",
        val=[
            992.5485,
            497.0066,
            1086.9169,
            525.98517,
            1238.1129,
            578.45197,
            1370.3975,
            638.23444,
            1498.929,
            698.4786,
            1661.6973,
            804.6463,
            1692.9056,
            765.0586,
            1717.2573,
            730.47906,
            1742.4459,
            688.0849,
            1756.8639,
            657.91815,
            1710.0581,
            632.3194,
            1625.6958,
            597.80176,
            1515.3823,
            564.9269,
            1407.7733,
            540.72064,
            1310.0101,
            522.7003,
            1269.0992,
            517.3429,
            1201.1145,
            511.01147,
            1125.6571,
            504.01138,
            1064.682,
            499.02698,
            1064.258,
            515.88055,
            1060.2301,
            515.9865,
            1060.9722,
            499.133,
            1024.4031,
            496.69504,
            1024.1373,
            502.25134,
            1020.11926,
            502.19046,
            1019.93665,
            496.1634,
            1013.42255,
            495.73724,
            1013.42255,
            501.15552,
            1011.83966,
            501.15552,
            1011.9006,
            495.43286,
            1005.20386,
            495.12845,
            1005.20386,
            499.93793,
            1003.8645,
            499.87704,
            1003.98627,
            495.37198,
            989.5578,
            494.0935,
            989.3752,
            495.06757,
            987.67053,
            494.88492,
            987.6097,
            493.7282,
            980.6162,
            493.1103,
            992.5485,
            497.0066,
        ],
    )


def build_polygon_with_hole(camera: str, include_polygon_id: bool) -> List[OLM.Poly2d]:
    return [
        OLM.Poly2d(
            attributes=OLM.Attributes(
                boolean=[OLM.Boolean(name="is_hole", val=False), OLM.Boolean(name="unclear", val=False)],
                text=[OLM.Text(name="stream", val=camera)] + ([OLM.Text(name="polygon_id", val="86c18a7e")] if include_polygon_id else []),
            ),
            closed=True,
            mode="MODE_POLY2D_ABSOLUTE",
            name="poly2d-86c18a7e-0",
            val=[
                950.391,
                493.6201,
                926.5495,
                491.24237,
                860.5003,
                489.8094,
                742.8483,
                493.9866,
                657.3286,
                503.6263,
                573.7845,
                517.1219,
                492.24054,
                530.29614,
                398.90833,
                549.89685,
                304.30035,
                575.85187,
                209.50993,
                609.5908,
                148.45848,
                640.5768,
                143.3173,
                650.2165,
                158.41951,
                703.23486,
                176.73494,
                754.4642,
                198.26361,
                788.84576,
                245.63704,
                856.89417,
                302.18997,
                909.5912,
                366.4206,
                958.36975,
                647.034,
                714.2116,
                871.07025,
                555.4381,
                931.60333,
                517.933,
                971.119,
                493.1103,
                960.32135,
                493.48022,
                960.32135,
                498.9349,
                959.3423,
                498.9349,
                958.78284,
                493.34033,
                950.391,
                493.6201,
            ],
        ),
        OLM.Poly2d(
            attributes=OLM.Attributes(
                boolean=[OLM.Boolean(name="is_hole", val=True), OLM.Boolean(name="unclear", val=False)],
                text=[OLM.Text(name="stream", val=camera)] + ([OLM.Text(name="polygon_id", val="86c18a7e")] if include_polygon_id else []),
            ),
            closed=True,
            mode="MODE_POLY2D_ABSOLUTE",
            name="poly2d-86c18a7e-1",
            val=[
                927.0357,
                495.00296,
                928.3077,
                495.63895,
                928.6257,
                509.3126,
                927.4597,
                509.94858,
                926.7177,
                510.05457,
                925.44574,
                509.5246,
                924.80975,
                495.74493,
                927.0357,
                495.00296,
            ],
        ),
    ]


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


def build_curve(camera: str, interpolation_method: str, offset: int) -> OLM.Poly2d:
    return OLM.Poly2d(
        attributes=OLM.Attributes(
            text=[OLM.Text(name="stream", val=camera), OLM.Text(name="interpolation_method", val=interpolation_method)]
        ),
        closed=False,
        mode="MODE_POLY2D_ABSOLUTE",
        name="curve-40cb6053",
        val=[
            x + offset for x in [992.5485, 497.0066, 1086.9169, 525.98517, 1238.1129, 578.45197, 1370.3975, 638.23444, 1498.929, 698.4786]
        ],
    )


def build_pre_annotation() -> OLM.OpenLabelAnnotation:
    lidar_sensor1 = "RFL01"
    cam_sensor1 = "RFC01"
    cam_sensor2 = "RFC02"

    object_uuid1 = str(uuid4())
    object_uuid2 = str(uuid4())
    object_uuid3 = str(uuid4())
    object_uuid4 = str(uuid4())
    object_uuid5 = str(uuid4())
    object_uuid6 = str(uuid4())
    object_uuid7 = str(uuid4())
    object_uuid8 = str(uuid4())

    polygon = build_polygon_with_hole(cam_sensor1, False)
    multi_polygon = [build_polygon_no_hole(cam_sensor2, True)] + build_polygon_with_hole(cam_sensor2, True)

    return OLM.OpenLabelAnnotation(
        openlabel=OLM.Openlabel(
            metadata=OLM.Metadata(name="empty pre-annotation", schema_version=OLM.SchemaVersion.field_1_0_0),
            objects={
                object_uuid1: OLM.Object(name="MultiPolygon", type="SpaceShip"),
                object_uuid2: OLM.Object(name="Polygon", type="Jedi"),
                object_uuid3: OLM.Object(name="Curve (natural cubic)", type="NaturalCurve"),
                object_uuid4: OLM.Object(name="Curve (catmull)", type="CatmullCurve"),
                object_uuid5: OLM.Object(name="Curve (polyline)", type="PolylineCurve"),
                object_uuid6: OLM.Object(name="Keypoint (point)", type="LineGeometricTypePoint"),
                object_uuid7: OLM.Object(name="PointContainer(3) (point)", type="BodyPose"),
                object_uuid8: OLM.Object(name="PointContainer(1) (point)", type="BodyPose"),
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
                                poly2d=multi_polygon,
                                text=[OLM.Text(name="ship_type", val="star_destroyer")],
                            )
                        ),
                        object_uuid2: OLM.Objects(
                            object_data=OLM.ObjectData(
                                poly2d=polygon,
                                text=[OLM.Text(name="light_saber", val="blue")],
                            )
                        ),
                        object_uuid3: OLM.Objects(
                            object_data=OLM.ObjectData(
                                poly2d=[build_curve(cam_sensor1, "natural-cubic-spline", 0)],
                                text=[OLM.Text(name="light_saber", val="blue")],
                            )
                        ),
                        object_uuid4: OLM.Objects(
                            object_data=OLM.ObjectData(
                                poly2d=[build_curve(cam_sensor1, "catmull-rom-0.5", 100)],
                                text=[OLM.Text(name="light_saber", val="red")],
                            )
                        ),
                        object_uuid5: OLM.Objects(
                            object_data=OLM.ObjectData(
                                poly2d=[build_curve(cam_sensor1, "polyline", 200)],
                                text=[OLM.Text(name="light_saber", val="green")],
                            )
                        ),
                        object_uuid6: OLM.Objects(
                            object_data=OLM.ObjectData(
                                point2d=[build_point2d(cam_sensor1, [902.3, 643.1])],
                                text=[OLM.Text(name="light_saber", val="green")],
                            )
                        ),
                        object_uuid7: OLM.Objects(
                            object_data=OLM.ObjectData(
                                point2d=build_point_container(cam_sensor1),
                                text=[OLM.Text(name="light_saber", val="green")],
                            )
                        ),
                        object_uuid8: OLM.Objects(
                            object_data=OLM.ObjectData(
                                point2d=[build_point2d(cam_sensor1, [902.3, 743.1])],
                                text=[OLM.Text(name="light_saber", val="green")],
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
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project

        pre_annotation = build_pre_annotation()

        created_inputs = lidars_cameras_with_pre_annotations_example.run(
            client=client,
            project=project,
            dryrun=False,
            pre_annotation=pre_annotation,
        )

        assert isinstance(created_inputs, list) and len(created_inputs) >= 1
        assert isinstance(created_inputs[0], Input)

    def test_validate_lidars_cameras_with_empty_pre_annotation(self, client: KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        resp = lidars_cameras_with_pre_annotations_example.run(client=client, project=project)
        assert resp is None

    def test_create_lidars_cameras_with_empty_pre_annotation(self, client: KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_and_cameras_seq_project(projects)[0].project
        created_inputs = lidars_cameras_with_pre_annotations_example.run(client=client, project=project, dryrun=False)

        assert isinstance(created_inputs, list) and len(created_inputs) >= 1
        assert isinstance(created_inputs[0], Input)

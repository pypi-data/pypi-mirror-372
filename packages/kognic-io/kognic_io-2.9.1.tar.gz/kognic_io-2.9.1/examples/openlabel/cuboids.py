from uuid import UUID, uuid4

import kognic.openlabel.models as OLM
from kognic.openlabel.models import OpenLabelAnnotation


def example_ola_with_cuboids() -> OpenLabelAnnotation:
    # Object ids must be valid uuids
    object_uuid1, object_uuid2 = str(uuid4()), str(uuid4())

    # Frame ids must be numbers represented as strings
    frame_id1, frame_id2 = "1", "2"

    # Stream names must match the stream names in the scene
    streams = build_streams(lidars=["RFL01", "RFL02"], cameras=["RFC01", "RFC02"])

    object1 = build_object(object_name="object1", object_class="SpaceShip")
    object2 = build_object(object_name="object2", object_class="SpaceShip")

    cuboid11 = build_cuboid(stream="RFL01", val=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    cuboid12 = build_cuboid(stream="RFL02", val=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    cuboid21 = build_cuboid(stream="RFL01", val=[19, 20, 21, 22, 23, 24, 25, 26, 27, 28])
    cuboid22 = build_cuboid(stream="RFL02", val=[28, 29, 30, 31, 32, 33, 34, 35, 36, 37])

    frame_object11 = build_frame_object_with_cuboid(cuboid=cuboid11)
    frame_object12 = build_frame_object_with_cuboid(cuboid=cuboid12)
    frame_object21 = build_frame_object_with_cuboid(cuboid=cuboid21)
    frame_object22 = build_frame_object_with_cuboid(cuboid=cuboid22)

    frame1 = build_frame(
        timestamp=0,
        objects={object_uuid1: frame_object11, object_uuid2: frame_object12},
        streams=streams,
    )

    frame2 = build_frame(
        timestamp=4,
        objects={object_uuid1: frame_object21, object_uuid2: frame_object22},
        streams=streams,
    )

    objects = {object_uuid1: object1, object_uuid2: object2}
    frames = {frame_id1: frame1, frame_id2: frame2}

    return build_openlabel(objects=objects, frames=frames, streams=streams)


def build_cuboid(stream: str, val: list[float]) -> OLM.Cuboid:
    return OLM.Cuboid(attributes=OLM.Attributes(text=[OLM.Text(name="stream", val=stream)]), name="does-not-matter", val=val)


def build_object(object_name: str, object_class: str) -> OLM.Object:
    return OLM.Object(name=object_name, type=object_class)  # Any static properties would go here


def build_frame_object_with_cuboid(cuboid: OLM.Cuboid) -> OLM.Objects:
    return OLM.Objects(object_data=OLM.ObjectData(cuboid=[cuboid]))  # Any dynamic properties would go here


def build_frame(timestamp: int, objects: dict[UUID, OLM.Objects], streams: dict[str, OLM.Stream]) -> OLM.Frame:
    # The timestamp should match the relative timestamp of the frame in the scene
    return OLM.Frame(
        frame_properties=OLM.FrameProperties(timestamp=timestamp, streams=streams, external_id="does-not-matter"),
        objects=objects,
    )


def build_streams(lidars: list[str], cameras: list[str]) -> dict[str, OLM.Stream]:
    # Stream names should be the same as in the scene
    lidar_streams = {ls: OLM.Stream(type=OLM.StreamTypes.lidar) for ls in lidars}
    camera_streams = {cs: OLM.Stream(type=OLM.StreamTypes.camera) for cs in cameras}
    return dict(**lidar_streams, **camera_streams)


def build_openlabel(
    objects: dict[str, OLM.Object], frames: dict[str, OLM.Frame], streams: dict[str, OLM.Stream]
) -> OLM.OpenLabelAnnotation:
    return OLM.OpenLabelAnnotation(
        openlabel=OLM.Openlabel(
            metadata=OLM.Metadata(schema_version=OLM.SchemaVersion.field_1_0_0),
            objects=objects,
            frames=frames,
            streams=streams,
        )
    )


if __name__ == "__main__":
    openlabel = example_ola_with_cuboids()

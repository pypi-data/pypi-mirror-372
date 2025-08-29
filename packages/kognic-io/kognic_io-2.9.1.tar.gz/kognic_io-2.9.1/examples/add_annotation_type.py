from kognic.io.client import KognicIOClient


def run(client: KognicIOClient, scene_uuid: str, annotation_type: str):
    print("Adding annotation types to scene...")
    client.input.add_annotation_type(scene_uuid=scene_uuid, annotation_type=annotation_type)


if __name__ == "__main__":
    client = KognicIOClient()

    scene_uuid = "<scene-identifier>"
    annotation_type = "annotation-type"
    run(client, scene_uuid, annotation_type)

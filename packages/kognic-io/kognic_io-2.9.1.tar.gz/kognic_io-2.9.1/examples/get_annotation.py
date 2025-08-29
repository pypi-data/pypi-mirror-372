from __future__ import absolute_import

from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model.annotation.client_annotation import Annotation


def run(client: KognicIOClient, scene_uuid: str, annotation_type: str) -> Annotation:
    return client.annotation.get_annotation(scene_uuid=scene_uuid, annotation_type=annotation_type)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    scene_uuid = "<scene-uuid>"
    annotation_type = "<annotation-type>"
    annotation = run(client, scene_uuid, annotation_type)

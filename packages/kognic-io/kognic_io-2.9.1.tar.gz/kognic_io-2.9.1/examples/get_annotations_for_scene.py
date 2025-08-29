from __future__ import absolute_import

from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model.annotation.annotation import Annotation


def run(client: KognicIOClient, scene_uuid: str) -> List[Annotation]:
    return client.annotation.get_annotations_for_scene(scene_uuid=scene_uuid)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    scene_uuid = "<scene-uuid>"
    annotations = run(client, scene_uuid)

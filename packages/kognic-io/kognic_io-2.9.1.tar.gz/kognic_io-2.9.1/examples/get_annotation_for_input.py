from __future__ import absolute_import

from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model.annotation.annotation import Annotation


def run(client: KognicIOClient, input_uuid: str) -> Annotation:
    return client.annotation.get_annotation_for_input(input_uuid=input_uuid)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    input_uuid = "<input-uuid>"
    annotation = run(client, input_uuid)

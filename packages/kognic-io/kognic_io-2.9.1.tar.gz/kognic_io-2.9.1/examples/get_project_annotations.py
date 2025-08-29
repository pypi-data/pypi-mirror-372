from __future__ import absolute_import

from typing import Generator, Optional

from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model.annotation.client_annotation import Annotation


def run(client: KognicIOClient, project: str, annotation_type: str, batch: Optional[str] = None) -> Generator[Annotation, None, None]:
    yield from client.annotation.get_project_annotations(project=project, batch=batch, annotation_type=annotation_type)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-idenfitier>"
    annotation_type = "<annotation-type>"
    annotation_generator = run(client, project, annotation_type)
    for annotation in annotation_generator:
        print(annotation)

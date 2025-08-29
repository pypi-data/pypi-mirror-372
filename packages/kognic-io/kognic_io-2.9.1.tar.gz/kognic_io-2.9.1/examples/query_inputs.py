from typing import List, Optional

from kognic.io.client import KognicIOClient
from kognic.io.model.input import Input


def run(client: KognicIOClient, project: Optional[str] = None, scene_uuids: Optional[List[str]] = None) -> List[Input]:
    print("Listing inputs...")
    return client.input.query_inputs(project=project, scene_uuids=scene_uuids)


if __name__ == "__main__":
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "Project-identifier"
    scene_uuids = ["scene-identifier"]
    run(client, project=project, scene_uuids=scene_uuids)

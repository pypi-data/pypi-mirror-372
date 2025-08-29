from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model.input.input_entry import Input as InputEntry


def run(client: KognicIOClient, project: str, include_invalidated: bool = False) -> List[InputEntry]:
    print("Listing inputs...")
    return client.input.get_inputs(project=project, include_invalidated=include_invalidated)


if __name__ == "__main__":
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "Project-identifier"
    run(client, project)

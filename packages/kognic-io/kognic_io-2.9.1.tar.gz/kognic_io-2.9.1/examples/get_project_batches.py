from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model import ProjectBatch


def run(client: KognicIOClient, project: str) -> List[ProjectBatch]:
    print("Listing project batches...")
    return client.project.get_project_batches(project)


if __name__ == "__main__":
    client = KognicIOClient()

    project = "Project-Identifier"
    project_batches = run(client, project=project)

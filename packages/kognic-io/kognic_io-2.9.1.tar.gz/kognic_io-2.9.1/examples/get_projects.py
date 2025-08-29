from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model import Project


def run(client: KognicIOClient) -> List[Project]:
    print("Listing projects...")
    return client.project.get_projects()


if __name__ == "__main__":
    client = KognicIOClient()
    projects = run(client)

    for project in projects:
        print(f"Project: {project.external_id}")
        batches = client.project.get_project_batches(project.external_id)

        print(", ".join([batch.external_id for batch in batches]))

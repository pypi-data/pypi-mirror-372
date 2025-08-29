from typing import List, Optional

from kognic.io.client import KognicIOClient


def run(client: KognicIOClient, project: str, batch: Optional[str] = None) -> List[str]:
    print("Listing projects annotation types...")
    return client.project.get_annotation_types(project=project, batch=batch)


if __name__ == "__main__":
    client = KognicIOClient()

    project = "Project-Identifier"
    annotation_types = run(client, project)

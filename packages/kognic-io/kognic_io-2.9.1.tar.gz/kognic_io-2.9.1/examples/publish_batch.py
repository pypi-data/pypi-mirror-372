from kognic.io.client import KognicIOClient
from kognic.io.model import ProjectBatch


def run(client: KognicIOClient, project: str, batch: str) -> ProjectBatch:
    print(f"Publish batch {batch} in project {project}")

    return client.project.publish_batch(project, batch)


if __name__ == "__main__":
    client = KognicIOClient()

    project = "Project-Identifier"
    batch = "New-Batch-Identifier"
    annotation_types = run(client, project, batch)

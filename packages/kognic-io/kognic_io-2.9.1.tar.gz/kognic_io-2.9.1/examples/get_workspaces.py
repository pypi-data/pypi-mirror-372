from typing import List, Optional

from kognic.io.client import KognicIOClient
from kognic.io.model import Workspace


def run(client: KognicIOClient, organization_id: Optional[int] = None) -> List[Workspace]:
    print("Listing workspaces...")
    return client.workspace.get_workspaces(organization_ids=organization_id or None)


if __name__ == "__main__":
    # If your credentials grant access to multiple organizations' workspaces , you must provide a client organization
    # ID or a specific workspace ID, or both, otherwise we are unable to determine which workspace to use for writes.
    client_organization_id = None
    write_workspace_id = None
    client = KognicIOClient(client_organization_id=client_organization_id, write_workspace_id=write_workspace_id)
    workspaces = run(client, organization_id=client_organization_id)

    print(f"Got {len(workspaces)} workspaces")
    for workspace in workspaces:
        print(f"Workspace: {workspace.external_id} ({workspace.id})")

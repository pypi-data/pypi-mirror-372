import pytest

import examples.get_workspaces as get_workspaces_example
import kognic.io.client as IOC


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestWorkspaces:

    def test_get_workspaces(self, client: IOC.KognicIOClient):
        workspaces = get_workspaces_example.run(client=client)
        assert isinstance(workspaces, list)
        assert len(workspaces) >= 1
        orgs = set(map(lambda ws: ws.organization_name, workspaces))
        assert len(orgs) > 1

    def test_get_workspaces_for_org(self, client: IOC.KognicIOClient):
        workspaces = get_workspaces_example.run(client=client, organization_id=1)
        assert isinstance(workspaces, list)
        assert len(workspaces) >= 1
        orgs = set(map(lambda ws: ws.organization_name, workspaces))
        assert orgs == {"Kognic"}

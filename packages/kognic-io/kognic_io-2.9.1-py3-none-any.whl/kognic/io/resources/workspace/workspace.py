import logging
import urllib.parse
from typing import List, Optional

from kognic.base_clients.http_client import HttpClient
from kognic.io.model.workspace.workspace import Workspace

log = logging.getLogger(__name__)


class WorkspaceResource:
    """
    Resource exposing Kognic Workspaces
    """

    def __init__(self, client: HttpClient):
        self._client = client

    def get_workspaces(self, roles: Optional[List[str]] = None, organization_ids: Optional[List[int]] = None) -> List[Workspace]:
        """
        Lists the workspaces that you have the developer role in.

        :param roles: an optional list of workspace role names to filter on.
        :param organization_ids: an optional filter for which organizations that you would like to list workspaces.
        :return List[Workspace]:
        """
        params = {"anyRoleIn": "developer" if roles is None else roles}
        if organization_ids is not None:
            params["organizationIds"] = organization_ids
        responses = self._client.get("/v1/workspaces?" + urllib.parse.urlencode(params, doseq=True))
        return [Workspace.from_json(r) for r in responses]

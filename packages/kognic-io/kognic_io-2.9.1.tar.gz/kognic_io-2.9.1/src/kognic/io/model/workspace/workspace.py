from dataclasses import dataclass
from datetime import datetime


@dataclass
class Workspace:
    created: datetime
    external_id: str
    id: str
    name: str
    organization_name: str

    def from_json(res: dict):
        return Workspace(
            created=datetime.strptime(res.get("created"), "%Y-%m-%dT%H:%M:%S.%fZ"),
            external_id=res.get("externalId"),
            id=res.get("id"),
            name=res.get("name"),
            organization_name=res.get("organization", {}).get("name"),
        )

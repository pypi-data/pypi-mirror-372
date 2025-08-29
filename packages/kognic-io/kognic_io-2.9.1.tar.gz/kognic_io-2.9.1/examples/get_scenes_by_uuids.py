from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model import Scene


def run(client: KognicIOClient, scene_uuids: List[str]) -> List[Scene]:
    print("Listing scenes...")
    return client.scene.get_scenes_by_uuids(scene_uuids=scene_uuids)


if __name__ == "__main__":
    client = KognicIOClient()

    scene_uuids = ["scene-identifier"]
    run(client, scene_uuids)

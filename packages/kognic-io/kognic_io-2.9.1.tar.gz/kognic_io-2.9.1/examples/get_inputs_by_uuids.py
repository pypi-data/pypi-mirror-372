from typing import List

from kognic.io.client import KognicIOClient
from kognic.io.model.input.input_entry import Input as InputEntry


def run(client: KognicIOClient, scene_uuids: List[str]) -> List[InputEntry]:
    print("Listing inputs...")
    return client.input.get_inputs_by_uuids(scene_uuids=scene_uuids)


if __name__ == "__main__":
    client = KognicIOClient()

    scene_uuids = ["scene-identifier"]
    run(client, scene_uuids)

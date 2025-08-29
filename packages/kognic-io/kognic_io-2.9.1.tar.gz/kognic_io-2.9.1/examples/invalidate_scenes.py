from kognic.io.client import KognicIOClient
from kognic.io.model import SceneInvalidatedReason


def run(client: KognicIOClient, scene_uuid: str, reason: SceneInvalidatedReason) -> None:
    print("Invalidating scenes...")
    client.scene.invalidate_scenes(scene_uuids=[scene_uuid], reason=reason)


if __name__ == "__main__":
    client = KognicIOClient()

    scene_uuid = "Scene-identifier"
    invalidated_reason = SceneInvalidatedReason.INCORRECTLY_CREATED
    run(client, scene_uuid, invalidated_reason)

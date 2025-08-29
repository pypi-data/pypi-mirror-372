import logging
import mimetypes
from typing import List

import kognic.io.model.scene as SceneModel
from kognic.base_clients.cloud_storage.upload_spec import UploadSpec
from kognic.io.model import Scene, SceneInvalidatedReason
from kognic.io.model.scene import SceneRequest
from kognic.io.resources.abstract import IOResource

log = logging.getLogger(__name__)


class SceneResource(IOResource):
    """
    Resource exposing Kognic Scenes
    """

    def get_scenes_by_uuids(self, scene_uuids: List[str]) -> List[Scene]:
        """
        Gets scenes using scene uuids. A NotFound exception will be raised if any of the scenes doesn't exist.

        :param scene_uuids: A UUID to filter scenes on
        :return List: List of Scenes
        """

        body = dict(sceneUuids=scene_uuids)
        json_resp = self._client.post("v2/scenes/query", json=body)
        return [Scene.from_json(js) for js in json_resp]

    def invalidate_scenes(self, scene_uuids: List[str], reason: SceneInvalidatedReason) -> None:
        """
        Invalidates scenes. This is a destructive operation, and it's important to be aware of the consequences.
        Read more about it here:
            https://docs.kognic.com/api-guide/working-with-scenes-and-inputs#jK-0z

        :param scene_uuids: The scene uuids to invalidate
        :param reason: The reason for invalidating the scene
        """
        body = dict(sceneUuids=scene_uuids, reason=reason.value)
        self._client.post("v2/scenes/actions/invalidate", json=body, discard_response=True)

    def create_scene(self, scene_request: SceneRequest):
        resp = self._client.post("v2/scenes", json=scene_request.to_dict())

        signed_upload_urls = resp.get("signedUploadUrls")
        if signed_upload_urls:
            uploadSpecs = {}
            files = scene_request.get_files()
            for filename, resource_id in signed_upload_urls:
                content_type = mimetypes.guess_type(filename)[0]
                # Handles lidar case
                content_type = content_type if content_type is not None else "application/octet-stream"

                file = files[filename]
                uploadSpecs[filename] = UploadSpec(
                    destination=resource_id,
                    content_type=content_type,
                    filename=filename,
                    callback=file.callback,
                    data=file.data,
                )

            self._file_client.upload_files(uploadSpecs)

            self._client.post(f"v1/inputs/{resp.get('id')}/actions/commit", discard_response=True)

        return SceneModel.CreateSceneResponse(scene_uuid=resp["id"])

    def import_indexed_scene(self, scene_uuid: str):
        """
        Imports an indexed scene.

        :param scene_uuid: The scene uuid to import
        """

        self._client.patch(f"v2/scenes/{scene_uuid}", json={"status": "created"}, discard_response=True)

    def reindex_scene(self, scene_uuid: str):
        """
        Reindexes a scene. This is the oppositie of importing an indexed scene.
        Inputs created from this scene will not be deleted but won't be possible to view.

        :param scene_uuid: The scene uuid to reindex
        """

        self._client.patch(f"v2/scenes/{scene_uuid}", json={"status": "indexed"}, discard_response=True)

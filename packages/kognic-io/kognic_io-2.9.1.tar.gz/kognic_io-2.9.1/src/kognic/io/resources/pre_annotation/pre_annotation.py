from typing import List, Optional
from urllib.parse import urlencode

from requests.exceptions import HTTPError

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.pre_annotation import CreatedPreAnnotation, ResolvedPreAnnotation
from kognic.io.resources.abstract import IOResource
from kognic.openlabel.models.models import OpenLabelAnnotation


class CreatePreannotationRequest(BaseSerializer):
    scene_uuid: str
    external_id: Optional[str]
    pre_annotation: OpenLabelAnnotation


class PreAnnotationResource(IOResource):
    """
    Resource exposing Kognic Pre-Annotations
    """

    def create(
        self, scene_uuid: str, pre_annotation: OpenLabelAnnotation, dryrun: bool, external_id: Optional[str] = None
    ) -> CreatedPreAnnotation:
        """
        Create a pre-annotation for a previously created scene. A scene may have multiple pre-annotations.
        The id of the returned PreAnnotation can be used to select this pre-annotation when creating an input.

        :param scene_uuid: the uuid of an existing scene.
        :param pre_annotation: The PreAnnotation content in the OpenLabel format
        :param external_id: Optional external identifier string for the pre-annotation. Must be unique per scene.
        :param dryrun: If True the files/metadata will be validated but no pre-annotation will be created
        """
        pre_anno_request = CreatePreannotationRequest(scene_uuid=scene_uuid, external_id=external_id, pre_annotation=pre_annotation)
        resp = self._client.post("v1/pre-annotations", json=pre_anno_request.to_dict(), dryrun=dryrun)
        return CreatedPreAnnotation.from_json(resp)

    def list(
        self,
        ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        scene_uuids: Optional[List[str]] = None,
        scene_external_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        List pre-annotations.

        :param scene_uuids: The uuids of the scenes.
        :param status: The status of the pre-annotations to filter on. If None, all pre-annotations will be returned.

        :return: A page of the pre-annotations matching the query.
        """
        params = {
            "offset": 0,
            "limit": 1000,
        }
        if ids:
            params["uuids"] = ids
        if external_ids:
            params["externalIds"] = external_ids
        if scene_uuids:
            params["sceneUuids"] = scene_uuids
        if scene_external_ids:
            params["sceneExternalIds"] = scene_external_ids
        if statuses:
            params["statuses"] = statuses

        has_next = True
        offset = 0
        data = []

        while has_next:
            url = f"{self._client.host}/v2/pre-annotations?{urlencode(params, doseq=True)}"
            resp = self._client.session.get(
                url,
                headers=self._client.headers,
                timeout=self._client.timeout,
            )

            if 400 <= resp.status_code < 500:
                try:
                    message = resp.json()["message"]
                except ValueError:
                    message = resp.text
                raise HTTPError(f"Client error: {resp.status_code} - {message}", response=resp)
            elif resp.status_code >= 300:
                resp.raise_for_status()

            json_resp = resp.json()
            data += json_resp.get("data", [])
            has_next = json_resp.get("hasNext")
            offset += 1000

        return data

    def create_from_cloud_resource(
        self, scene_uuid: str, external_id: str, cloud_resource_uri: str, postpone_import: Optional[bool] = True
    ) -> str:
        """
        Create pre-annotation to a previously created scene. The pre-annotation will be created in the same workspace as the scene.


        :param scene_uuid: The uuid for the scene.
        :param external_id: A human readable unique identifier of the pre-annotation.
        :param cloud_resource_uri: The cloud resource uri of the pre-annotation
        :param postpone_import: If True, the pre-annotation will be created but not imported to the kognic platform.
            So no data will leave you cloud yet.
            If False, the pre-annotation will be created and imported to the kognic platform
            and kognic will read the cloud_resource_uri from your bucket.

        :return: The uuid of the created pre-annotation.
        """
        body = dict(
            sceneUuid=scene_uuid,
            externalId=external_id,
            externalResourceId=cloud_resource_uri,
            postponeExternalResourceImport=postpone_import,
        )
        resp = self._client.post("v2/pre-annotations", json=body)
        return resp.get("id")

    def make_indexed_pre_annotation_available(self, id: str):
        """
        Import the cloud resource to kognics platform.

        :param id: The uuid of the pre-annotation.
        """
        body = dict(status="processing")
        self._client.patch(f"v2/pre-annotations/{id}", json=body, discard_response=True)

    def delete(self, id: str):
        """
        Delete the pre-annotation.

        :param id: The uuid of the pre-annotation.
        """
        self._client.delete(f"v2/pre-annotations/{id}", discard_response=True)

    def get_with_content(
        self, uuid: Optional[str] = None, scene_uuid: Optional[str] = None, external_id: Optional[str] = None
    ) -> ResolvedPreAnnotation:
        """
        Get a pre-annotation with content by UUID or by external ID and scene UUID.
        The pre-annotation must have been populated with OpenLabel data in order to be resolved.

        :param uuid: The UUID of the pre-annotation to retrieve. Used instead of scene_uuid/external_id.
        :param external_id: The external ID of the pre-annotation within the scene. Used with scene_uuid.
        :param scene_uuid: The UUID of the scene (required when using external_id). Used with external_id
        :return: The resolved pre-annotation with full content.
        """
        if uuid:
            if external_id or scene_uuid:
                raise ValueError("Cannot specify uuid together with other parameters")
            target_uuid = uuid
        elif external_id:
            if not scene_uuid:
                raise ValueError("scene_uuid is required when using external_id")
            target_uuid = self._look_up_uuid(external_id, scene_uuid)
        else:
            raise ValueError("Must specify either uuid or (external_id and scene_uuid)")

        resp = self._client.get(f"v2/pre-annotations/{target_uuid}/resolved")
        return ResolvedPreAnnotation.from_json(resp)

    def _look_up_uuid(self, external_id: str, scene_uuid: str) -> str:
        """
        Get pre-annotation UUID by external ID and scene UUID.

        :param external_id: The external ID of the pre-annotation within the scene.
        :param scene_uuid: The UUID of the scene.
        :return: The UUID of the pre-annotation.
        """
        list_params = {"external_ids": [external_id], "scene_uuids": [scene_uuid]}
        pre_annotations = self.list(**list_params)

        if len(pre_annotations) == 0:
            raise ValueError(f"No pre-annotation {external_id} found in scene {scene_uuid}")
        elif len(pre_annotations) > 1:
            raise ValueError(f"Multiple pre-annotations found with external_id '{external_id}' in scene {scene_uuid}")
        return pre_annotations[0]["id"]

import logging
from typing import List, Optional

from deprecated import deprecated

from kognic.io.model.input.input import Input
from kognic.io.model.input.input_entry import Input as InputEntry
from kognic.io.model.scene.invalidated_reason import SceneInvalidatedReason
from kognic.io.resources.abstract import IOResource
from kognic.io.util import deprecated_parameter, filter_none

log = logging.getLogger(__name__)


class InputResource(IOResource):
    """
    Resource exposing Kognic Inputs
    """

    def delete_input(self, input_uuid: str) -> None:
        """
        Deletes an input, which removes the scene from the request. This is a destructive operation, and it's
        important to be aware of the consequences. Read more about it here:
            https://docs.kognic.com/api-guide/working-with-scenes-and-inputs#JTRDb

        :param input_uuid: The input uuid to invalidate
        """
        self._client.delete(f"v2/inputs/{input_uuid}", discard_response=True)

    def query_inputs(
        self,
        *,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        scene_uuids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
    ) -> List[Input]:
        """
        Queries inputs from the Kognic Platform. Each entry in the list is an Input object.

        :param project: Project (identifier) to filter
        :param batch: Batch (identifier) to filter
        :param scene_uuids: The scene UUIDs to filter inputs on
        :param external_ids: External ID to filter input on
        :return List: List of Input
        """
        payload = {
            "project": project,
            "batch": batch,
            "sceneUuids": scene_uuids,
            "externalIds": external_ids,
        }

        endpoint = "v2/inputs/query"

        inputs = list()
        for js in self._paginate_post(endpoint, json=filter_none(payload)):
            inputs.append(Input.from_json(js))
        return inputs

    def create_from_scene(
        self,
        scene_uuid: str,
        pre_annotation_uuid: Optional[str],
        project: Optional[str] = None,
        batch: Optional[str] = None,
        request_uuid: Optional[str] = None,
        dryrun: bool = False,
    ) -> Optional[Input]:
        """
        Creates a Request Input from a scene. The target Request can be specified by project/batch external ids or
        by request UUID. A pre-annotation UUID is optional; if omitted then the scene will be annotated without any
        of its pre-annotations. This behavior differs from the scene's own `create_from_scene` e.g.
        `client.cameras.create_from_scene`, which always use the latest available
        pre-annotation for the scene, if one exists.
        """
        return self._internal_create_from(scene_uuid, pre_annotation_uuid, project, batch, request_uuid, dryrun)

    def create_from_pre_annotation(
        self,
        pre_annotation_uuid: str,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        request_uuid: Optional[str] = None,
        dryrun: bool = False,
    ) -> Optional[Input]:
        """
        Creates a Request Input from a pre-annotation. The target Request can be specified by project/batch external ids
        or by request UUID. The scene to use is defined by the pre-annotation.
        """
        return self._internal_create_from(None, pre_annotation_uuid, project, batch, request_uuid, dryrun)

    def _internal_create_from(
        self,
        scene_uuid: Optional[str],
        pre_annotation_uuid: Optional[str],
        project: Optional[str],
        batch: Optional[str],
        request_uuid: Optional[str],
        dryrun: bool,
    ) -> Optional[Input]:
        if (request_uuid is None) == (project is None):
            raise ValueError("Either request_uuid or project must be specified.")
        payload = {
            "sceneUuid": scene_uuid,
            "preAnnotationUuid": pre_annotation_uuid,
        }
        if request_uuid:
            payload["requestUuid"] = request_uuid
        else:
            payload["projectExtId"] = project
            payload["batchExtId"] = batch
        resp = self._client.post("v2/inputs", json=filter_none(payload), dryrun=dryrun, discard_response=dryrun)
        if dryrun:
            return None
        return Input.from_json(resp)

    @deprecated(reason="This is deprecated in favour of `invalidate_scenes` or `delete_input` and will be removed in the future")
    @deprecated_parameter("input_uuids", "scene_uuids", end_version="3.0.0")
    def invalidate_inputs(self, scene_uuids: List[str], invalidated_reason: SceneInvalidatedReason) -> None:
        """
        Invalidates inputs, and removes them from all input lists

        :param scene_uuids: The scene uuids to invalidate
        :param invalidated_reason: An Enum describing why inputs were invalidated
        """
        invalidated_json = dict(inputIds=scene_uuids, invalidatedReason=invalidated_reason)
        self._client.post("v1/inputs/actions/invalidate", json=invalidated_json, discard_response=True)

    @deprecated(reason="This is deprecated in favour of `query_inputs` and will be removed in the future")
    def get_inputs(
        self,
        project: str,
        batch: Optional[str] = None,
        include_invalidated: bool = False,
        external_ids: Optional[List[str]] = None,
    ) -> List[InputEntry]:
        """
        Gets inputs for project, with option to filter for invalidated inputs

        :param project: Project (identifier) to filter
        :param batch: Batch (identifier) to filter
        :param include_invalidated: Returns invalidated inputs if True, otherwise valid inputs
        :param external_ids: External ID to filter input on
        :return List: List of Inputs
        """

        payload = {
            "project": project,
            "batch": batch,
            "includeInvalidated": include_invalidated,
            "externalIds": external_ids,
        }

        endpoint = "v1/inputs/fetch"

        inputs = list()
        for js in self._paginate_post(endpoint, json=filter_none(payload)):
            inputs.append(InputEntry.from_json(js))
        return inputs

    @deprecated_parameter("input_uuid", "scene_uuid", end_version="3.0.0")
    def add_annotation_type(self, scene_uuid: str, annotation_type: str) -> None:
        """
        Adds annotation-type to the input, which informs the Kognic Platform
        to produce a corresponding annotation for the annotation-type. Only
        possible if the annotation-type is available in the corresponding batch
        of the input (use method `get_annotation_types` to check).
        """

        self._client.post(f"v1/inputs/{scene_uuid}/actions/add-annotation-type/{annotation_type}", discard_response=True)

    def update_pre_annotation(self, request_input_uuid: str, pre_annotation_uuid: str) -> None:
        """
        Replace the pre-annotation used by an existing request input. This is only possible before annotation starts.
        """
        payload = {"uuid": pre_annotation_uuid}
        self._client.patch(f"v2/inputs/{request_input_uuid}/pre-annotation", json=payload, discard_response=True)

    @deprecated(reason="This is deprecated in favour of `delete_input` and will be removed in the future")
    @deprecated_parameter("input_uuid", "scene_uuid", end_version="3.0.0")
    def remove_annotation_types(self, scene_uuid: str, annotation_types: List[str]) -> None:
        """
        Removes annotation types from the input, which informs the Kognic Platform
        that a corresponding annotation should not be produced for the annotation types. Only
        possible if the annotation type is available for the input (use method `get_inputs_by_uuids` to check).
        Note: If multiple annotation types are configured to be annotated at the same time, i.e. on the same request,
        all of these annotation types need to be provided.
        """
        body = dict(annotationTypes=annotation_types)
        self._client.post(f"v1/inputs/{scene_uuid}/annotation-types/actions/remove", json=body, discard_response=True)

    @deprecated(reason="This is deprecated in favour of `get_scenes_by_uuids` and will be removed in the future")
    @deprecated_parameter("input_uuids", "scene_uuids", end_version="3.0.0")
    def get_inputs_by_uuids(self, scene_uuids: List[str]) -> List[InputEntry]:
        """
        Gets inputs using input uuids

        :param scene_uuids: A UUID to filter inputs on
        :return List: List of Inputs
        """

        body = dict(uuids=scene_uuids)
        json_resp = self._client.post("v1/inputs/query", json=body)
        return [InputEntry.from_json(js) for js in json_resp]

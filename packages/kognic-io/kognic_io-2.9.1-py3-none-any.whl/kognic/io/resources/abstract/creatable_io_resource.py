import io
import json
import logging
from typing import Dict, List, Mapping, Optional, Tuple

import kognic.io.model as IOM
from kognic.base_clients.cloud_storage import FileResourceClient, UploadSpec
from kognic.base_clients.http_client import HttpClient
from kognic.io.model.ego import IMUData
from kognic.io.model.ego.validated_imu_data import ValidatedIMUData, ValidateIMUDataRequest
from kognic.io.model.input.input import Input
from kognic.io.model.input.input_from_scene_request import InputFromSceneRequest
from kognic.io.model.scene.feature_flags import FeatureFlags
from kognic.io.model.scene.resources.resource import Resource
from kognic.io.model.scene.scene_job import InitializedSceneJob

log = logging.getLogger(__name__)

INPUTS_ROUTE = "v1/inputs"


class CreateableIOResource:
    def __init__(self, client: HttpClient, file_resource_client: FileResourceClient, workspace_id: str):
        super().__init__()
        self._client = client
        self._file_resource_client = file_resource_client
        self._workspace_id = workspace_id

    def _post_input_request(
        self,
        resource_path: str,
        body: dict,
        project: Optional[str],
        batch: Optional[str],
        annotation_types: Optional[List[str]] = None,
        imu_data: Optional[List[IMUData]] = None,
        resources: Optional[Mapping[str, Resource]] = None,
        dryrun: bool = False,
        feature_flags: Optional[FeatureFlags] = None,
    ) -> Optional[IOM.SceneJobCreated]:
        """
        Send scene to API. if dryrun is true, only validation is performed
        Otherwise, returns `SceneJobCreated`
        """

        scene_uuid = self._get_scene_uuid()
        body["internalId"] = scene_uuid

        body, validated_imu_data = self._validate_imu_data(body, imu_data, scene_uuid, dryrun)

        body = self._append_annotation_types(body, annotation_types)

        feature_flags = feature_flags if feature_flags is not None else FeatureFlags.defaults()

        body = self._append_feature_flags(body, feature_flags)

        scene_job_json = self._validate_and_create_scene(
            resource_path=resource_path, body=body, project=project, batch=batch, dryrun=dryrun
        )

        if not dryrun:
            response = IOM.SceneJobCreated.from_json(scene_job_json)

            local_files_uploaded = self._upload_local_files(resources, response)

            local_files_uploaded += self._upload_imu_data(validated_imu_data)

            if local_files_uploaded:
                self._client.post(f"{INPUTS_ROUTE}/{response.scene_uuid}/actions/commit", discard_response=True)

            return response

    def _get_scene_uuid(self) -> str:
        json_resp = self._client.post(INPUTS_ROUTE + "/initialize", json={"workspaceId": self._workspace_id})
        init_input = InitializedSceneJob.from_json(json_resp)

        return init_input.scene_uuid

    def _validate_imu_data(
        self, body: Dict, imu_data: Optional[List[IMUData]], input_uuid: str, dryrun: bool
    ) -> Tuple[Dict, Optional[ValidatedIMUData]]:
        if imu_data is None or len(imu_data) == 0:
            return body, None

        imu_request = ValidateIMUDataRequest(imu_data=imu_data, internal_id=input_uuid)
        json_resp = self._client.post(
            f"v1/imu?workspaceId={self._workspace_id}", json=imu_request.to_dict(), dryrun=dryrun, discard_response=dryrun
        )

        valid_imu_data = None
        if json_resp is not None and not dryrun:
            json_resp["imuData"] = imu_data
            valid_imu_data = ValidatedIMUData.from_json(json_resp)
            body["imuData"] = valid_imu_data.resource_id

        return body, valid_imu_data

    def _append_annotation_types(self, body: Dict, annotation_types: Optional[List[str]]) -> Dict:
        if annotation_types:
            body["annotationTypes"] = annotation_types
        return body

    def _append_feature_flags(self, body: Dict, feature_flags: Optional[FeatureFlags]) -> Dict:
        if feature_flags:
            body["featureFlags"] = feature_flags.to_dict()
        return body

    def _validate_and_create_scene(
        self, *, resource_path: str, body: dict, project: Optional[str], batch: Optional[str], dryrun: bool = False
    ) -> Optional[Dict]:
        log.debug("POST:ing to %s input %s", resource_path, body)
        request_url = self._resolve_request_url(resource_path, self._workspace_id, project, batch)
        return self._client.post(request_url, json=body, dryrun=dryrun, discard_response=dryrun)

    def _upload_local_files(self, resources: Optional[Mapping[str, Resource]], response: IOM.SceneJobCreated) -> bool:
        num_signed = len(response.files)
        num_requested = len(resources) if resources is not None else 0
        if num_signed > 0:
            assert num_signed == num_requested, f"File count discrepancy: {num_requested} != {num_signed}"
            uploads = {}
            for resource_id, signed_url in response.files.items():
                uploads[resource_id] = CreateableIOResource.create_upload_spec(signed_url, resources[resource_id])
            self._file_resource_client.upload_files(uploads)
            return True
        return False

    def _upload_imu_data(self, validated_imu_data: Optional[ValidatedIMUData]) -> bool:
        if validated_imu_data is not None and validated_imu_data.signed_url is not None:
            file = io.BytesIO(json.dumps(validated_imu_data.serialize_imu_data()).encode("utf-8"))
            self._file_resource_client.upload_json(file, validated_imu_data.signed_url)
            return True
        return False

    @staticmethod
    def _resolve_request_url(resource_path: str, workspace_id: str, project: Optional[str] = None, batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = INPUTS_ROUTE + "/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path
        url += f"?workspaceId={workspace_id}"

        return url

    @staticmethod
    def create_upload_spec(destination: str, res: Resource):
        return UploadSpec(
            destination=destination,
            content_type=res.content_type,
            filename=res.client_filename,
            data=res.file_data.data if res.file_data is not None else None,
            callback=res.file_data.callback if res.file_data is not None else None,
        )

    def create_from_scene(
        self, scene_uuid: str, project: str, batch: Optional[str] = None, annotation_types: Optional[List[str]] = None, dryrun: bool = False
    ) -> Optional[List[Input]]:
        """
        Create inputs from a scene. Note that, if a pre-annotation has been added for the scene, it will be included for
        all inputs.

        :param scene_uuid: uuid of the scene to create inputs from
        :param project: the project to add the inputs to
        :param batch: the batch to add the inputs to. Will default to the latest open batch if 'None'.
        :param annotation_types: list of annotation types to add inputs for. Will default to all annotation types for
            the project and batch if 'None' or empty
        :param dryrun: whether to do a dry-run or not
        :return: list of created inputs if not dryrun, otherwise None
        """
        if annotation_types is None:
            annotation_types = []
        create_request = InputFromSceneRequest(scene_uuid=scene_uuid, annotation_types=annotation_types, project=project, batch=batch)
        resp = self._client.post(INPUTS_ROUTE, json=create_request.to_dict(), dryrun=dryrun, discard_response=dryrun)
        if dryrun:
            return None

        return [Input.from_json(js) for js in resp]

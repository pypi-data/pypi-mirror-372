"""Client for communicating with the Kognic platform."""

import logging
from typing import Optional

from kognic.auth import DEFAULT_HOST as DEFAULT_AUTH_HOST
from kognic.auth.requests.auth_session import RequestsAuthSession
from kognic.base_clients.cloud_storage import FileResourceClient
from kognic.base_clients.http_client import HttpClient
from kognic.io import __version__
from kognic.io.model.hosts import (
    DEFAULT_ANNOTATION_INTEGRATION_API_HOST,
    DEFAULT_INPUT_API_HOST,
    DEFAULT_ORDER_EXECUTION_API_HOST,
    DEFAULT_WORKSPACE_API_HOST,
)
from kognic.io.resources.annotation.annotation import AnnotationResource
from kognic.io.resources.calibration.calibration import CalibrationResource
from kognic.io.resources.input.input import InputResource
from kognic.io.resources.pre_annotation.pre_annotation import PreAnnotationResource
from kognic.io.resources.project.project import ProjectResource
from kognic.io.resources.review.review import ReviewResource
from kognic.io.resources.scene.aggregated_lidars_and_cameras_seq import AggregatedLidarsAndCamerasSequence
from kognic.io.resources.scene.cameras import Cameras
from kognic.io.resources.scene.cameras_sequence import CamerasSequence
from kognic.io.resources.scene.lidars import Lidars
from kognic.io.resources.scene.lidars_and_cameras import LidarsAndCameras
from kognic.io.resources.scene.lidars_and_cameras_sequence import LidarsAndCamerasSequence
from kognic.io.resources.scene.lidars_sequence import LidarsSequence
from kognic.io.resources.scene.scene import SceneResource
from kognic.io.resources.workspace.workspace import WorkspaceResource

log = logging.getLogger(__name__)


class KognicIOClient:
    """Client to work upload and retrieve data from the Kognic platform"""

    def __init__(
        self,
        *,
        auth=None,
        host: str = DEFAULT_INPUT_API_HOST,
        order_execution_api_host: str = DEFAULT_ORDER_EXECUTION_API_HOST,
        annotation_integration_api_host: str = DEFAULT_ANNOTATION_INTEGRATION_API_HOST,
        workspace_api_host: str = DEFAULT_WORKSPACE_API_HOST,
        auth_host: str = DEFAULT_AUTH_HOST,
        client_organization_id: Optional[int] = None,
        max_retry_attempts: int = 23,
        max_retry_wait_time: int = 60,
        timeout: int = 60,
        max_connections: int = 10,
        write_workspace_id: Optional[str] = None,
    ):
        """
        :param auth: auth credentials, see https://docs.kognic.com/api-guide/advanced-setup#WQ641
        :param host: Base url for the input api
        :param order_execution_api_host: Base url for the order execution api
        :param annotation_integration_api_host: Base url for the shape integration api
        :param auth_host: Base url for the auth server
        :param client_organization_id: Overrides your users organization id. Only works with an Kognic user.
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        :param timeout: Max time to wait for response from server.
        :param max_connections: Max nr network connections to apply to the http client.
        :param write_workspace_id: Optional workspace id used for when writing, if you do not provide one we try to infer it.
        """
        self._auth_session = RequestsAuthSession(host=auth_host, auth=auth)
        self._input_client = KognicIOClient._create_http_client(
            host=host,
            client_organization_id=client_organization_id,
            timeout=timeout,
            session=self._auth_session,
        )

        self._workspace_client = KognicIOClient._create_http_client(
            host=workspace_api_host,
            client_organization_id=client_organization_id,
            timeout=timeout,
            session=self._auth_session,
        )

        self._order_execution_client = KognicIOClient._create_http_client(
            host=order_execution_api_host,
            client_organization_id=client_organization_id,
            timeout=timeout,
            session=self._auth_session,
        )

        self._annotation_integration_api_client = KognicIOClient._create_http_client(
            host=annotation_integration_api_host,
            client_organization_id=client_organization_id,
            timeout=timeout,
            session=self._auth_session,
        )

        self._file_client = FileResourceClient(
            max_retry_attempts=max_retry_attempts,
            max_retry_wait_time=max_retry_wait_time,
            timeout=timeout,
            max_connections=max_connections,
        )

        self.workspace = WorkspaceResource(self._workspace_client)
        self._ensure_write_workspace_id(write_workspace_id, client_organization_id)

        self.calibration = CalibrationResource(self._input_client, self._file_client, self.workspace_id)
        self.project = ProjectResource(self._input_client, self._file_client, self.workspace_id)
        self.annotation = AnnotationResource(self._input_client, self._file_client, self.workspace_id)
        self.input = InputResource(self._input_client, self._file_client, self.workspace_id)
        self.pre_annotation = PreAnnotationResource(self._input_client, self._file_client, self.workspace_id)
        self.scene = SceneResource(self._input_client, self._file_client, self.workspace_id)

        self.lidars_and_cameras = LidarsAndCameras(self._input_client, self._file_client, self.workspace_id)
        self.lidars_and_cameras_sequence = LidarsAndCamerasSequence(self._input_client, self._file_client, self.workspace_id)
        self.cameras = Cameras(self._input_client, self._file_client, self.workspace_id)
        self.cameras_sequence = CamerasSequence(self._input_client, self._file_client, self.workspace_id)
        self.lidars = Lidars(self._input_client, self._file_client, self.workspace_id)
        self.lidars_sequence = LidarsSequence(self._input_client, self._file_client, self.workspace_id)
        self.aggregated_lidars_and_cameras_seq = AggregatedLidarsAndCamerasSequence(
            self._input_client, self._file_client, self.workspace_id
        )

        self.review = ReviewResource(client=self._annotation_integration_api_client)

    @staticmethod
    def _create_http_client(host, client_organization_id, timeout, session):
        # TODO: michel might have a dynamic way of doing this but hard code it for now.
        version = __version__
        client = HttpClient(
            host=host,
            client_organization_id=client_organization_id,
            timeout=timeout,
            session=session,
        )
        ua = client.headers.get("User-Agent", "")
        client.headers["User-Agent"] = ua + f" kognic-io/{version}"

        return client

    def _ensure_write_workspace_id(self, workspace_id: Optional[str], client_organization_id: Optional[int]):
        if workspace_id is None:
            if client_organization_id is None:
                workspaces = self.workspace.get_workspaces()
            else:
                workspaces = self.workspace.get_workspaces(organization_ids=[client_organization_id])
            if len(workspaces) != 1:
                raise ValueError("Could not infer a workspace where you are developer, please provide a workspace ID")
            self.workspace_id = workspaces[0].id

        else:
            if client_organization_id is not None:
                log.warning(f"Provided client org ID will not be used for workspace scoping: {client_organization_id}")
            self.workspace_id = workspace_id

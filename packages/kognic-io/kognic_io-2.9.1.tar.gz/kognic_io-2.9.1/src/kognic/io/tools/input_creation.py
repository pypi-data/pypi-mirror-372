import logging
import time
from typing import Generator, List, Optional, Type

from requests import HTTPError
from tqdm import tqdm

from kognic.io.client import KognicIOClient
from kognic.io.model import SceneStatus
from kognic.io.model.scene import AggregatedLidarsAndCamerasSequence, Cameras, CamerasSequence, LidarsAndCameras, LidarsAndCamerasSequence
from kognic.io.model.scene.feature_flags import FeatureFlags
from kognic.io.resources.abstract import CreateableIOResource
from kognic.io.tools.model import (
    InputCreationError,
    InputCreationResult,
    InputCreationStage,
    InputCreationStatus,
    Scene,
    SceneUuid,
    SceneWithPreAnnotation,
)
from kognic.openlabel.models import OpenLabelAnnotation

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 100
CONSERVATIVE_CHUNK_SIZE = 20


def create_inputs(
    client: KognicIOClient,
    scenes_with_pre_annotations: List[SceneWithPreAnnotation],
    project: str,
    dryrun: Optional[bool] = False,
    feature_flags: Optional[FeatureFlags] = None,
    wait_timeout: float = 1800,  # this will depend heavily on the scene size and the number of scenes
    sleep_time: float = 1,
    **kwargs,
) -> Generator[InputCreationResult, None, None]:
    """
    Create multiple inputs, optionally with pre-annotations. This consists of the following steps
    1. Start scene jobs
    2. As scene jobs complete
        2.1. A pre-annotation is optionally created
        2.2. An input is created for the scene

    :param client: KognicIOClient
    :param scenes_with_pre_annotations: List of scenes and pre-annotations to create. Note that the scenes must all be of the same type.
    :param project: project to add input to
    :param dryrun: If True the files/metadata will be validated but no scene job will be created.
    :param feature_flags: Optional set of feature flags to control the scene creation process.
    :param wait_timeout: Time in seconds to wait for scene jobs to complete.
    :param sleep_time: Time in seconds to sleep between checking scene job status.
    :param kwargs: Passed to the `create_from_scene` method. For example batch and annotation_types
    :returns InputCreationResult: Contains information about the creation process. For example, whether it succeeded or failed
    """

    scenes = [swp.scene for swp in scenes_with_pre_annotations]
    resource = _get_creatable_resource(client, scenes)
    scene_uuids = _start_scene_jobs(resource, scenes, dryrun=dryrun, feature_flags=feature_flags)

    if dryrun:  # Don't do anything more if dry-run
        return

    scenes_map = {
        uuid: swp for uuid, swp in zip(scene_uuids, scenes_with_pre_annotations)  # noqa: B905 (strict parameter was introduced in py3.10)
    }
    for input_result in _wait_for_scene_jobs(client, scene_uuids, wait_timeout, sleep_time):
        if input_result.status == InputCreationStatus.CREATED:
            pre_annotation = scenes_map[input_result.scene_uuid].pre_annotation
            if pre_annotation:
                pre_anno_result = _create_pre_annotation(client, input_result.scene_uuid, pre_annotation)
                input_result = input_result.combine(pre_anno_result)

        if input_result.status == InputCreationStatus.CREATED:
            input_from_scene_result = _create_input_from_scene(resource, input_result.scene_uuid, project, **kwargs)
            input_result = input_result.combine(input_from_scene_result)

        external_id = scenes_map[input_result.scene_uuid].scene.external_id
        yield input_result.add_external_id(external_id)


def _start_scene_jobs(
    resource: CreateableIOResource, scenes: List[Scene], dryrun: bool = False, feature_flags: Optional[FeatureFlags] = None
) -> List[SceneUuid]:
    # Starts scene jobs. Don't catch validation errors. The returned list must have the same order as the scenes
    return [
        resource.create(scene, dryrun=dryrun, feature_flags=feature_flags).scene_uuid for scene in tqdm(scenes, desc="Starting scene jobs")
    ]


def _chunkify(origin_list: list, chunk_size: int) -> List[list]:
    return [origin_list[idx : idx + chunk_size] for idx in range(0, len(origin_list), chunk_size)]


def _wait_for_scene_jobs(
    client: KognicIOClient,
    scene_uuids: List[SceneUuid],
    wait_timeout: float,
    sleep_time: float,
) -> Generator[InputCreationResult, None, None]:
    logger.info(f"Waiting for {len(scene_uuids)} scene jobs to complete")
    remaining_scenes_uuids = set(scene_uuids)
    start_time = time.time()
    chunk_size = DEFAULT_CHUNK_SIZE

    while time.time() - start_time < wait_timeout and remaining_scenes_uuids:
        logger.info(f"{len(remaining_scenes_uuids)} scene jobs remaining")
        for chunk in _chunkify(list(remaining_scenes_uuids), chunk_size):
            try:
                scenes = client.scene.get_scenes_by_uuids(chunk)

                for scene in scenes:  # Yield created scenes
                    if scene.status == SceneStatus.Created:
                        yield InputCreationResult(scene_uuid=scene.uuid, status=InputCreationStatus.CREATED)
                        remaining_scenes_uuids.remove(scene.uuid)

                    elif scene.status == SceneStatus.Failed:  # Yield failed scenes
                        yield InputCreationResult(
                            scene_uuid=scene.scene_uuid,
                            status=InputCreationStatus.FAILED,
                            error=InputCreationError(stage=InputCreationStage.SCENE, message=scene.error_message),
                        )
                        remaining_scenes_uuids.remove(scene.scene_uuid)
            except (HTTPError, RuntimeError):
                # Try decreasing the amount of scenes we query the Input API for (only when chunk size is default)
                chunk_size = CONSERVATIVE_CHUNK_SIZE if chunk_size == DEFAULT_CHUNK_SIZE else chunk_size
                break

        time.sleep(sleep_time)

    # Yield results for remaining scenes
    for scene_uuid in remaining_scenes_uuids:
        yield InputCreationResult(scene_uuid=scene_uuid, status=InputCreationStatus.PROCESSING)


def _create_pre_annotation(client: KognicIOClient, scene_uuid: str, pre_annotation: OpenLabelAnnotation) -> InputCreationResult:
    # Try to create a pre-annotation and return a creation result
    try:
        preanno = client.pre_annotation.create(scene_uuid, pre_annotation, dryrun=False)
        return InputCreationResult(scene_uuid=scene_uuid, preannotation_uuid=preanno.id, status=InputCreationStatus.CREATED)
    except (HTTPError, RuntimeError) as error:
        logger.error(f"Failed to create pre-annotation for scene {scene_uuid}. {error}")
        creation_error = InputCreationError(stage=InputCreationStage.PRE_ANNOTATION, message=str(error))
        return InputCreationResult(scene_uuid=scene_uuid, status=InputCreationStatus.FAILED, error=creation_error)


def _create_input_from_scene(resource: CreateableIOResource, scene_uuid: SceneUuid, project: str, **kwargs) -> InputCreationResult:
    # Create input from scene. Catch errors and put them in the result
    try:
        resource.create_from_scene(scene_uuid, project, **kwargs)
        return InputCreationResult(scene_uuid=scene_uuid, input_uuid=scene_uuid, status=InputCreationStatus.CREATED)
    except (HTTPError, RuntimeError) as error:
        logger.error(f"Failed to create input from scene {scene_uuid}. {error}")
        creation_error = InputCreationError(stage=InputCreationStage.INPUT_FROM_SCENE, message=str(error))
        return InputCreationResult(scene_uuid=scene_uuid, status=InputCreationStatus.FAILED, error=creation_error)


def _get_creatable_resource(client: KognicIOClient, scenes: List[Scene]) -> CreateableIOResource:
    scene_type = _check_scene_types(scenes)

    resources_map = {
        Cameras: client.cameras,
        CamerasSequence: client.cameras_sequence,
        LidarsAndCameras: client.lidars_and_cameras,
        LidarsAndCamerasSequence: client.lidars_and_cameras_sequence,
        AggregatedLidarsAndCamerasSequence: client.aggregated_lidars_and_cameras_seq,
    }

    if scene_type not in resources_map:
        raise ValueError(f"Scene of type '{scene_type.__name__}' not supported")
    return resources_map.get(scene_type)


def _check_scene_types(scenes: List[Scene]) -> Type[Scene]:
    first_type = type(scenes[0])
    assert all([isinstance(scene, first_type) for scene in scenes]), "All scenes must be of the same type"
    return first_type

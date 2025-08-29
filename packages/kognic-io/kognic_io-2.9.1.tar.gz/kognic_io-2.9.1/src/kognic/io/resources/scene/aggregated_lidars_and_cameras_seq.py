import logging
from typing import List, Optional

import kognic.io.model.scene as SceneModel
from kognic.io.model.scene.feature_flags import FeatureFlags
from kognic.io.resources.abstract import CreateableIOResource

log = logging.getLogger(__name__)


class AggregatedLidarsAndCamerasSequence(CreateableIOResource):
    path = "aggregated-lidars-and-cameras-sequence"

    def create(
        self,
        aggregated_lidars_and_cameras_seq: SceneModel.AggregatedLidarsAndCamerasSequence,
        project: Optional[str] = None,
        batch: Optional[str] = None,
        annotation_types: Optional[List[str]] = None,
        dryrun: bool = False,
        feature_flags: Optional[FeatureFlags] = None,
    ) -> Optional[SceneModel.CreateSceneResponse]:
        """
        Upload files and create a scene of type ``AggregatedLidarsAndCamerasSequence``.

        :param aggregated_lidars_and_cameras_seq: class containing 2D and 3D resources that constitute the scene
        :param project: project to add input to
        :param batch: batch, defaults to latest open batch
        :param annotation_types: annotation types for which to produce annotations for. Defaults to `None` (corresponds
         to all available annotation types). Passing an empty list will result in the same behaviour as passing `None`.
        :param dryrun: If True the files/metadata will be validated but no input job will be created.
        :param feature_flags Optional set of feature flags to control the input creation process.
        :returns CreateSceneResponse: Class containing uuid of the created scene job, or `None` if dryrun.
        """
        if not isinstance(aggregated_lidars_and_cameras_seq, SceneModel.AggregatedLidarsAndCamerasSequence):
            raise ValueError(f"Cannot create a {type(aggregated_lidars_and_cameras_seq)} via this endpoint")

        response = self._post_input_request(
            self.path,
            aggregated_lidars_and_cameras_seq.to_dict(),
            project=project,
            batch=batch,
            annotation_types=annotation_types,
            imu_data=aggregated_lidars_and_cameras_seq.imu_data,
            resources=aggregated_lidars_and_cameras_seq.resources,
            dryrun=dryrun,
            feature_flags=feature_flags,
        )

        if dryrun:
            return None

        log.info(f"Created scene for files with uuid={response.scene_uuid}")
        return SceneModel.CreateSceneResponse.from_scene_job_created(response)

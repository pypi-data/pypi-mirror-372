from __future__ import absolute_import

import pytest

import examples.lidars_and_cameras_seq_rgb as lidars_cameras_seq_example
import kognic.io.client as IOC
from examples.utils import wait_for_scene_job


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestLidarsAndCamerasSeq:
    def test_create_only_scene_lidars_and_cameras_seq(self, client: IOC.KognicIOClient):
        resp = lidars_cameras_seq_example.run(client=client, project=None, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, fail_on_failed=True)
        assert isinstance(resp.scene_uuid, str)

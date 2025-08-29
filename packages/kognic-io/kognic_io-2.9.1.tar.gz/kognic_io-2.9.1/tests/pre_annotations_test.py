from __future__ import absolute_import, annotations

from datetime import datetime

import pytest

import kognic.io.client as IOC
from examples.utils import wait_for_pre_annotation


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestPreAnnotations:
    def test_list(self, client: IOC.KognicIOClient):
        data = client.pre_annotation.list(statuses=["processing", "available"])
        assert len(data) > 0, "Expected at least one pre-annotation to be returned"

    def test_create_indexed(self, client: IOC.KognicIOClient, uri_for_external_ol: str, existing_lacs_scene_uuid: str):
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=existing_lacs_scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postpone_import=True,
        )

        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "indexed", "Expected the pre-annotation to be in indexed status"

    def test_create(self, client: IOC.KognicIOClient, uri_for_external_ol: str, existing_lacs_scene_uuid: str):
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=existing_lacs_scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postpone_import=False,
        )
        wait_for_pre_annotation(client, pre_annotation_id, fail_on_failed=True)
        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "available", "Expected the pre-annotation to be in available status"

    def test_make_indexed_available(self, client: IOC.KognicIOClient, uri_for_external_ol: str, existing_lacs_scene_uuid: str):
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=existing_lacs_scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postpone_import=True,
        )

        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "indexed", "Expected the pre-annotation to be in indexed status"

        client.pre_annotation.make_indexed_pre_annotation_available(pre_annotation_id)
        wait_for_pre_annotation(client, pre_annotation_id, fail_on_failed=True)
        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "available", "Expected the pre-annotation to be in available status"

    def test_delete(self, client: IOC.KognicIOClient, uri_for_external_ol: str, existing_lacs_scene_uuid: str):
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=existing_lacs_scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postpone_import=True,
        )

        client.pre_annotation.delete(id=pre_annotation_id)

    def test_get_content(self, client: IOC.KognicIOClient, existing_pre_annotation_uuid: str):
        resolved_pre_annotation = client.pre_annotation.get_with_content(uuid=existing_pre_annotation_uuid)
        assert resolved_pre_annotation is not None, "Expected a pre-annotation to be returned"
        assert resolved_pre_annotation.uuid == existing_pre_annotation_uuid, "Wrong UUID"
        assert resolved_pre_annotation.content is not None, "Expected content to be present"
        assert resolved_pre_annotation.content.openlabel is not None
        assert resolved_pre_annotation.content.openlabel.metadata.schema_version == "1.0.0", "Unexpected OL version"
        assert len(resolved_pre_annotation.content.openlabel.frames) == 1, "Bad number of frames"

    def test_get_content_by_external_id(self, client: IOC.KognicIOClient, existing_pre_annotation_uuid: str):
        existing_pre_anno = client.pre_annotation.get_with_content(uuid=existing_pre_annotation_uuid)
        scene_uuid = existing_pre_anno.scene_uuid
        pre_annotation_ext_id = existing_pre_anno.external_id

        pre_annotation = client.pre_annotation.get_with_content(scene_uuid=scene_uuid, external_id=pre_annotation_ext_id)
        assert pre_annotation is not None, "Expected a pre-annotation to be returned"
        assert pre_annotation == existing_pre_anno, "Expected same pre-annotation to be returned as by UUID"
        assert pre_annotation.content is not None, "Expected content to be present"
        assert pre_annotation.content.openlabel is not None
        assert pre_annotation.content.openlabel.metadata.schema_version == "1.0.0", "Unexpected OL version"
        assert len(pre_annotation.content.openlabel.frames) == 1, "Bad number of frames"

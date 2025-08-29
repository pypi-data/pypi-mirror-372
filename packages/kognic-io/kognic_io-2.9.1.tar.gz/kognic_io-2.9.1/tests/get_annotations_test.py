from __future__ import absolute_import, annotations

import pytest

import examples.get_annotation as get_annotation_example
import examples.get_annotation_for_input as get_annotation_for_input_example
import examples.get_annotations_for_scene as get_annotations_for_scene_example
import kognic.io.client as IOC
from kognic.io.model import Annotation
from kognic.io.model.annotation.client_annotation import Annotation as AnnotationLegacy


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestGetAnnotations:
    def test_get_annotation_for_input(self, client: IOC.KognicIOClient):
        annotation = get_annotation_for_input_example.run(client=client, input_uuid="55ecfb29-d542-4192-a0c5-c4f5516efa70")
        assert isinstance(annotation, Annotation)

    def test_get_annotations_for_scene(self, client: IOC.KognicIOClient):
        annotations = get_annotations_for_scene_example.run(client=client, scene_uuid="ec33447c-60a8-4c67-883a-079592d3296e")
        assert isinstance(annotations, list) and len(annotations) == 1
        assert isinstance(annotations[0], Annotation)

    def test_get_annotation(self, client: IOC.KognicIOClient):
        annotation = get_annotation_example.run(client=client, scene_uuid="e1229546-f447-4c07-8f6d-1347f067d14a", annotation_type="signs")
        assert isinstance(annotation, AnnotationLegacy)

    def test_get_annotation_incorrect_at(self, client: IOC.KognicIOClient):
        with pytest.raises(Exception) as exception_info:
            get_annotation_example.run(client=client, scene_uuid="e1229546-f447-4c07-8f6d-1347f067d14a", annotation_type="od")

        assert "404 Client Error: Not Found for url:" in exception_info.value.args[0]

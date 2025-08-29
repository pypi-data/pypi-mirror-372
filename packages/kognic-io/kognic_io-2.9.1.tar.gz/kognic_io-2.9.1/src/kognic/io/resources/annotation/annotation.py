from typing import Generator, List, Optional

from kognic.io.model.annotation.annotation import Annotation, PartialAnnotation
from kognic.io.model.annotation.client_annotation import Annotation as ClientAnnotation
from kognic.io.model.annotation.client_annotation import PartialAnnotation as PartialClientAnnotation
from kognic.io.resources.abstract import IOResource
from kognic.io.util import deprecated_parameter


class AnnotationResource(IOResource):
    def get_annotation_for_input(self, input_uuid: str) -> Annotation:
        """
        Gets an annotation for an input. A NotFound exception will be raised if there isn't any annotation for the given uuid.

        :param input_uuid: uuid of the input
        :returns Annotation: annotation with its content
        """
        json_resp = self._client.get(f"v2/inputs/{input_uuid}/annotation")
        partial_annotation = PartialAnnotation.from_json(json_resp)
        content = self._file_client.get_json(partial_annotation.uri)
        return partial_annotation.to_annotation(content)

    def get_annotations_for_scene(self, scene_uuid: str) -> List[Annotation]:
        """
        Gets all annotations for a scene. A NotFound exception will be raised if the scene doesn't exist.

        :param scene_uuid: uuid of the scene
        :returns List[Annotation]: annotations with their content
        """
        annotations = list()
        for js in self._client.get(f"v2/scenes/{scene_uuid}/annotations"):
            partial_annotation = PartialAnnotation.from_json(js)
            content = self._file_client.get_json(partial_annotation.uri)
            annotations.append(partial_annotation.to_annotation(content))
        return annotations

    def get_project_annotations(
        self,
        project: str,
        annotation_type: str,
        batch: Optional[str] = None,
        include_content: bool = True,
    ) -> Generator[Annotation, None, None]:
        """
        Gets annotations for a project and annotation type with an optional filter for a batch.
        Annotations include annotation contents which means that this function is heavier than `get_partial_annotations`
        that only gets partial annotations.

        :param project: project to query annotations from
        :param annotation_type: annotation type to query annotation on
        :param batch: batch to filter on (optional)
        :param include_content: whether to include annotation content (default: True)
        :returns Generator[Annotation]: Generator of annotations
        """

        url = f"v1/annotations/projects/{project}/"
        if batch:
            url += f"batch/{batch}/"

        url += f"annotation-type/{annotation_type}/search"

        for js in self._paginate_get(url):
            partial_annotation = PartialClientAnnotation.from_json(js)
            content = self._file_client.get_json(partial_annotation.uri) if include_content else None
            yield partial_annotation.to_annotation(content)

    @deprecated_parameter("input_uuid", "scene_uuid", end_version="3.0.0")
    def get_annotation(self, scene_uuid: str, annotation_type: str) -> Annotation:
        """
        Gets an annotation for a scene and annotation type. A NotFound exception will be raised if there isn't any
        annotation for the given uuid and annotation type.

        :param scene_uuid: uuid of the scene
        :param annotation_type: annotation type to get annotation for
        :returns Annotation: annotation with its content
        """
        json_resp = self._client.get(f"v1/annotations/inputs/{scene_uuid}/annotation-type/{annotation_type}")
        annotation = ClientAnnotation.from_json(json_resp)
        return annotation

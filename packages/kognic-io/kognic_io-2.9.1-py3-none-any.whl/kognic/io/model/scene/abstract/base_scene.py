from abc import ABC
from typing import Mapping

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.model.scene.resources.resource import Resource


class BaseScene(BaseSerializer, ABC):
    """
    Base class for the concept of an input scene.
    """

    @property
    def resources(self) -> Mapping[str, Resource]:
        raise NotImplementedError(f"resources not implemented for {type(self)}")

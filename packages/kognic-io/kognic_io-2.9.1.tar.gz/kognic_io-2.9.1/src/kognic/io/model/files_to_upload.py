from typing import List

from kognic.io.model.base_serializer import BaseSerializer


class FilesToUpload(BaseSerializer):
    """
    Used when retrieving upload urls from input api
    """

    files_to_upload: List[str]

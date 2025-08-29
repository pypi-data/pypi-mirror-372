from typing import Dict

from pydantic import Field

from kognic.io.model.base_serializer import BaseSerializer


class UploadUrls(BaseSerializer):
    files_to_url: Dict[str, str] = Field(alias="files")
    input_uuid: int = Field(alias="jobId")

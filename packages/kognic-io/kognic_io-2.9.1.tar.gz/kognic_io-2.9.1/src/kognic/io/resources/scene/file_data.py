import mimetypes
from enum import Enum
from typing import Optional

from kognic.base_clients.cloud_storage.upload_spec import Callback, UploadableData


class FileData:
    """
    Describes a source of file data to upload at a later point.
    """

    class Format(str, Enum):
        """
        Enumeration of file data formats supported as input resources.
        """

        CSV = "csv"
        LAS = "las"
        LAZ = "laz"
        PCD = "pcd"
        JPG = "jpg"
        PNG = "png"
        WEBP = "webp"
        AVIF = "avif"

        @property
        def is_pointcloud(self):
            return self in (FileData.Format.CSV, FileData.Format.LAS, FileData.Format.LAZ, FileData.Format.PCD)

        @property
        def is_image(self):
            return self in (FileData.Format.JPG, FileData.Format.PNG, FileData.Format.WEBP, FileData.Format.AVIF)

    format: Format
    data: Optional[UploadableData]
    callback: Optional[Callback]

    def __init__(self, format: Format, data: Optional[UploadableData] = None, callback: Optional[Callback] = None):
        """
        Create a new FileData, describing the content of a file. The data in the file is taken from either a blob
        provided directly at creation time, or from a callback that will be called at some later point.

        :param format: The format of the data in this file. Must be one of the supported types in FileData.Format.
        :param data: Optional, the data itself. May be bytes or a bytes-like object.
        :param callback: Optional, a callback which can provide the data later, as bytes or a bytes-like object.
        """
        self.format = format
        self.data = data
        self.callback = callback
        self.check_data_source()

    def check_data_source(self):
        if self.data is None and self.callback is None:
            raise ValueError("One of data or callback must be set on FileData")
        if self.data is not None and self.callback is not None:
            raise ValueError("Only one of data or callback may be set on FileData")

    @property
    def suffix(self):
        return f".{self.format.value}"

    @property
    def content_type(self):
        if self.suffix in mimetypes.types_map:
            return mimetypes.types_map[self.suffix]
        else:
            return "application/octet-stream"

    def __repr__(self):
        data_part = "" if self.data is None else "blob"
        callback_part = "" if self.callback is None else "callback"
        return f"FileData({data_part}{callback_part} format={self.format})"

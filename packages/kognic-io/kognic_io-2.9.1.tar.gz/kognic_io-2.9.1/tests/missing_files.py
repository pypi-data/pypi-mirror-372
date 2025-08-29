from __future__ import absolute_import

import tempfile

import pytest

from kognic.io.model import Image, MissingFileError, PointCloud
from kognic.io.resources.scene.file_data import FileData

lidar_sensor = "lidar"
cam_sensor = "RFC01"

empty_las = tempfile.mkstemp(suffix=".las")[1]
empty_jpg = tempfile.mkstemp(suffix=".jpg")[1]


class TestCreateInputWithFileData:
    """
    Test that missing files will cause scene creation to baulk before starting to communicate with the API.
    """

    def test_do_not_detect_missing_files_for_file_datas(self):
        """
        Missing files should not be detected for file_datas (callback or blob); a local file is not required.
        """
        try:
            PointCloud(filename="pc_blob", sensor_name=lidar_sensor, file_data=FileData(FileData.Format.LAS, data=b"not used"))
        except MissingFileError:
            pytest.fail("Should not have detected missing file for blob file_data")

        try:
            Image(filename="img_from_blob", sensor_name=cam_sensor, file_data=FileData(FileData.Format.JPG, data=b"not used"))
        except MissingFileError:
            pytest.fail("Should not have detected missing file for blob file_data")

        def stub(filename: str) -> bytes:
            return b"not used"

        try:
            PointCloud(filename="pc_cb", sensor_name=lidar_sensor, file_data=FileData(FileData.Format.LAS, callback=stub))
        except MissingFileError:
            pytest.fail("Should not have detected missing file for blob file_data")

        try:
            Image(filename="img_from_blob", sensor_name=cam_sensor, file_data=FileData(FileData.Format.JPG, callback=stub))
        except MissingFileError:
            pytest.fail("Should not have detected missing file for blob file_data")

    def test_detect_missing_files(self):
        """
        Should detect files which are completely absent from the filesystem.
        """
        with pytest.raises(MissingFileError) as exc_info:
            PointCloud(filename="./examples/resources/missing.las", sensor_name=lidar_sensor)
        assert exc_info.value.empty is False

        with pytest.raises(MissingFileError) as exc_info:
            Image(filename="./examples/resources/missing.jpg", sensor_name=cam_sensor)
        assert exc_info.value.empty is False

    def test_detect_empty_files(self):
        """
        Should detect files which exist in the filesystem but do not contain any data.
        """
        with pytest.raises(MissingFileError) as exc_info:
            PointCloud(filename=empty_las, sensor_name=lidar_sensor)
        assert exc_info.value.empty

        with pytest.raises(MissingFileError) as exc_info:
            Image(filename=empty_jpg, sensor_name=cam_sensor)
        assert exc_info.value.empty

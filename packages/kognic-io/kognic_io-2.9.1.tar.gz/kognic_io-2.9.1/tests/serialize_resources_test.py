import pytest

from kognic.io.model import Image, PointCloud
from kognic.io.resources.scene.file_data import FileData


def test_resource_id_or_path_image_without_resource_id():
    image_dict = Image(filename="examples/resources/img_RFC01.jpg", resource_id=None, sensor_name="not used").to_dict()
    assert image_dict["resourceId"] == "examples/resources/img_RFC01.jpg"


def test_resource_id_or_path_image_with_resource_id():
    image_dict = Image(filename="examples/resources/img_RFC01.jpg", resource_id="local://foo/bar", sensor_name="not used").to_dict()
    assert image_dict["resourceId"] == "local://foo/bar"


@pytest.mark.parametrize("format_to_test", [FileData.Format.CSV, FileData.Format.LAS, FileData.Format.LAZ, FileData.Format.PCD])
def test_images_cannot_be_pointclouds(format_to_test):
    with pytest.raises(ValueError) as ex:
        Image(filename="foo.jpg", sensor_name="sensor", file_data=FileData(data=b"asdf", format=format_to_test))
    assert ex is not None


@pytest.mark.parametrize("format_to_test", [FileData.Format.JPG, FileData.Format.PNG])
def test_pointclouds_cannot_be_images(format_to_test):
    with pytest.raises(ValueError) as ex:
        PointCloud(filename="foo.las", sensor_name="sensor", file_data=FileData(data=b"asdf", format=format_to_test))
    assert ex is not None

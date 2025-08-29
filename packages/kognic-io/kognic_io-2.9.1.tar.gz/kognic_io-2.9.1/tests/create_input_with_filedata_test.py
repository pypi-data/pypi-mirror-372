from __future__ import absolute_import

import asyncio
from datetime import datetime
from typing import List
from uuid import uuid4

import pytest

import kognic.io.client as IOC
import kognic.io.model.scene.cameras as C
import kognic.io.model.scene.cameras_sequence as CS
import kognic.io.model.scene.lidars_and_cameras as LC
import kognic.io.model.scene.lidars_and_cameras_sequence as LCS
from examples.calibration.calibration import create_sensor_calibration
from kognic.io.model import Image, PointCloud, Project, SensorCalibrationEntry
from kognic.io.resources.abstract import CreateableIOResource
from kognic.io.resources.scene.file_data import FileData
from tests.utils import TestProjects

lidar_sensor = "lidar"
cam_sensor = "RFC01"
img_name = "./examples/resources/img_RFC01.jpg"
pc_name = "./examples/resources/point_cloud_RFL01.las"
anno_types = ["object-detection"]


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestCreateInputWithFileData:
    """
    Smoke tests for each input type for creating an input with directly-provided and callback-sourced bytes.
    """

    @staticmethod
    def filter_project(projects: List[Project], project: str) -> str:
        return [p for p in projects if p.project == project][0].project

    @staticmethod
    def file_callback(name: str) -> bytes:
        return open(name, "rb").read()

    @staticmethod
    async def async_file_callback(name: str) -> bytes:
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, lambda: open(name, "rb").read())
        return content

    @pytest.fixture
    def calibration_cam(self, client: IOC.KognicIOClient) -> SensorCalibrationEntry:
        calibration_spec = create_sensor_calibration(f"Calibration {datetime.now()}", [], [cam_sensor])
        return client.calibration.create_calibration(calibration_spec)

    @pytest.fixture
    def calibration_lidar_and_cam(self, client: IOC.KognicIOClient) -> SensorCalibrationEntry:
        calibration_spec = create_sensor_calibration(f"Calibration {datetime.now()}", [lidar_sensor], [cam_sensor])
        return client.calibration.create_calibration(calibration_spec)

    @pytest.fixture
    def pc_blob(self) -> PointCloud:
        return PointCloud(
            filename=pc_name,
            sensor_name=lidar_sensor,
            file_data=FileData(data=TestCreateInputWithFileData.file_callback(pc_name), format=FileData.Format.LAS),
        )

    @pytest.fixture
    def pc_cb(self) -> PointCloud:
        return PointCloud(
            filename=pc_name,
            sensor_name=lidar_sensor,
            file_data=FileData(callback=TestCreateInputWithFileData.file_callback, format=FileData.Format.LAS),
        )

    @pytest.fixture
    def pc_cb_async(self) -> PointCloud:
        return PointCloud(
            filename=pc_name,
            sensor_name=lidar_sensor,
            file_data=FileData(callback=TestCreateInputWithFileData.async_file_callback, format=FileData.Format.LAS),
        )

    @pytest.fixture
    def img_blob(self) -> Image:
        return Image(
            filename=img_name,
            sensor_name=cam_sensor,
            file_data=FileData(data=TestCreateInputWithFileData.file_callback(img_name), format=FileData.Format.JPG),
        )

    @pytest.fixture
    def img_cb(self) -> Image:
        return Image(
            filename=img_name,
            sensor_name=cam_sensor,
            file_data=FileData(callback=TestCreateInputWithFileData.file_callback, format=FileData.Format.JPG),
        )

    @pytest.fixture
    def img_cb_async(self) -> Image:
        return Image(
            filename=img_name,
            sensor_name=cam_sensor,
            file_data=FileData(callback=TestCreateInputWithFileData.async_file_callback, format=FileData.Format.JPG),
        )

    # Cameras
    def _test_create_cameras(self, client: IOC.KognicIOClient, calibration, img):
        project = self.filter_project(client.project.get_projects(), TestProjects.CamerasProject)
        scene = C.Cameras(
            external_id=f"alternative-source-cams-{uuid4()}",
            calibration_id=calibration.id,
            frame=C.Frame(images=[img]),
        )
        resp = client.cameras.create(scene, project=project, annotation_types=anno_types, dryrun=False)
        assert resp is not None

    def test_create_cameras_with_blob(self, client: IOC.KognicIOClient, calibration_cam, img_blob):
        self._test_create_cameras(client, calibration_cam, img_blob)

    def test_create_cameras_with_callback(self, client: IOC.KognicIOClient, calibration_cam, img_cb):
        self._test_create_cameras(client, calibration_cam, img_cb)

    def test_create_cameras_with_async_callback(self, client: IOC.KognicIOClient, calibration_cam, img_cb_async):
        self._test_create_cameras(client, calibration_cam, img_cb_async)

    # Cameras Seq
    def _test_create_cameras_seq(self, client: IOC.KognicIOClient, calibration, img):
        project = self.filter_project(client.project.get_projects(), TestProjects.CamerasSequenceProject)
        scene = CS.CamerasSequence(
            external_id=f"alternative-source-cams-seq-{uuid4()}",
            calibration_id=calibration.id,
            frames=[CS.Frame(frame_id="1", relative_timestamp=0, images=[img])],
        )
        resp = client.cameras_sequence.create(scene, project=project, annotation_types=anno_types, dryrun=False)
        assert resp is not None

    def test_create_cameras_seq_with_blob(self, client: IOC.KognicIOClient, calibration_cam, img_blob):
        self._test_create_cameras_seq(client, calibration_cam, img_blob)

    def test_create_cameras_seq_with_callback(self, client: IOC.KognicIOClient, calibration_cam, img_cb):
        self._test_create_cameras_seq(client, calibration_cam, img_cb)

    def test_create_cameras_seq_with_async_callback(self, client: IOC.KognicIOClient, calibration_cam, img_cb_async):
        self._test_create_cameras_seq(client, calibration_cam, img_cb_async)

    # Lidars and Cameras
    def _test_create_lidars_and_cameras(self, client: IOC.KognicIOClient, calibration, img, pc):
        project = self.filter_project(client.project.get_projects(), TestProjects.LidarsAndCamerasProject)
        frame = LC.Frame(frame_id="1", relative_timestamp=0, point_clouds=[pc], images=[img])
        scene = LC.LidarsAndCameras(
            external_id=f"alternative-source-lids-and-cams-{uuid4()}",
            calibration_id=calibration.id,
            frame=frame,
        )
        resp = client.lidars_and_cameras.create(scene, project=project, annotation_types=anno_types, dryrun=False)
        assert resp is not None

    def test_create_lidars_and_cameras_with_blob(self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_blob, pc_blob):
        self._test_create_lidars_and_cameras(client, calibration_lidar_and_cam, img_blob, pc_blob)

    def test_create_lidars_and_cameras_with_callback(self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_cb, pc_cb):
        self._test_create_lidars_and_cameras(client, calibration_lidar_and_cam, img_cb, pc_cb)

    def test_create_lidars_and_cameras_with_async_callback(
        self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_cb_async, pc_cb_async
    ):
        self._test_create_lidars_and_cameras(client, calibration_lidar_and_cam, img_cb_async, pc_cb_async)

    # Lidars and Cameras Seq
    def _test_create_lidars_and_cameras_seq(self, client: IOC.KognicIOClient, calibration, img, pc):
        project = self.filter_project(client.project.get_projects(), TestProjects.LidarsAndCamerasSequenceProject)
        frame = LCS.Frame(frame_id="1", relative_timestamp=0, point_clouds=[pc], images=[img])
        scene = LCS.LidarsAndCamerasSequence(
            external_id=f"alternative-source-lids-and-cams-seq-{uuid4()}",
            calibration_id=calibration.id,
            frames=[frame],
        )
        resp = client.lidars_and_cameras_sequence.create(scene, project=project, dryrun=False)
        assert resp is not None

    def test_create_lidars_and_cameras_seq_with_blob(self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_blob, pc_blob):
        self._test_create_lidars_and_cameras_seq(client, calibration_lidar_and_cam, img_blob, pc_blob)

    def test_create_lidars_and_cameras_seq_with_callback(self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_cb, pc_cb):
        self._test_create_lidars_and_cameras_seq(client, calibration_lidar_and_cam, img_cb, pc_cb)

    def test_create_lidars_and_cameras_seq_with_async_callback(
        self, client: IOC.KognicIOClient, calibration_lidar_and_cam, img_cb_async, pc_cb_async
    ):
        self._test_create_lidars_and_cameras_seq(client, calibration_lidar_and_cam, img_cb_async, pc_cb_async)

    # The filename passed to the callback should not have been modified by internal code, so that it's still a value
    # that will make sense to the client (e.g. we cannot have added any suffixes).
    @pytest.mark.parametrize("filename", ["foo.jpg", "foo.bar", "foo.bar.jpg", "a_b-1000.2000.jpg"])
    def test_callback_param_identity(self, filename):
        the_name = "placeholder"

        def cb(name):
            nonlocal the_name
            the_name = name
            return b"some data"

        image = Image(filename=filename, sensor_name="cam", file_data=FileData(callback=cb, format=FileData.Format.JPG))
        upload_spec = CreateableIOResource.create_upload_spec("dest url not used", image)
        data = upload_spec.callback(upload_spec.filename)
        assert the_name == filename
        assert data == b"some data"

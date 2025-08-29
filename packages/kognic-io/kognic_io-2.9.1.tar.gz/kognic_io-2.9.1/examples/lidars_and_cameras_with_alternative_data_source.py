from __future__ import absolute_import

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import kognic.io.model.scene.lidars_and_cameras as LC
from examples.calibration.calibration import create_sensor_calibration
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, Image, PointCloud
from kognic.io.resources.scene.file_data import FileData


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> CreateSceneResponse:
    print("Creating Lidars And Cameras Scene with data from alternative sources...")

    lidar_sensor1 = "lidar"
    cam_sensor1 = "RFC01"
    cam_sensor2 = "RFC02"
    cam_sensor3 = "RFC03"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    # Create calibration
    calibration_spec = create_sensor_calibration(f"Collection {datetime.now()}", [lidar_sensor1], [cam_sensor1, cam_sensor2, cam_sensor3])
    created_calibration = client.calibration.create_calibration(calibration_spec)

    # Callback to sources and returns the bytes for some input file. This example implementation assumes the filename
    # refers to a local file but it may source the bytes for that name via any means.
    def get_bytes(name: str) -> bytes:
        return Path(name).open("rb").read()

    # The single pointcloud is taken from a file without special treatment
    pc_name = "./examples/resources/point_cloud_RFL01.las"

    # Alternative 1: data is passed directly as an in-memory blob:
    img1_name = "./examples/resources/img_RFC01.jpg"
    img1_data = FileData(data=get_bytes(img1_name), format=FileData.Format.JPG)

    # Alternative 2: data will be obtained from a callback:
    img2_name = "./examples/resources/img_RFC02.jpg"
    img2_data = FileData(callback=get_bytes, format=FileData.Format.JPG)

    scene = LC.LidarsAndCameras(
        external_id=f"alternative-source-{uuid4()}",
        frame=LC.Frame(
            point_clouds=[PointCloud(filename=pc_name, sensor_name=lidar_sensor1)],
            images=[
                Image(filename=img1_name, file_data=img1_data, sensor_name=cam_sensor1),
                Image(filename=img2_name, file_data=img2_data, sensor_name=cam_sensor2),
            ],
        ),
        calibration_id=created_calibration.id,
        metadata=metadata,
    )

    # Create scene
    return client.lidars_and_cameras.create(scene, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-id>"

    run(client, project=project)

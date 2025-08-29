from __future__ import absolute_import

from datetime import datetime
from typing import Optional
from uuid import uuid4

import kognic.io.model.scene.lidars_and_cameras as LCM
from examples.calibration.calibration import create_sensor_calibration
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, Image, PointCloud


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> Optional[CreateSceneResponse]:
    print("Creating Lidars And Cameras Scene...")

    lidar_sensor1 = "lidar"
    cam_sensor1 = "RFC01"
    cam_sensor2 = "RFC02"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    # Create calibration
    # (Please refer to the API documentation about calibration for more details)
    calibration_spec = create_sensor_calibration(
        f"Collection {datetime.now()}",
        [lidar_sensor1],
        [cam_sensor1, cam_sensor2],
    )
    created_calibration = client.calibration.create_calibration(calibration_spec)

    scene = LCM.LidarsAndCameras(
        external_id=f"lidars-and-cameras-example-{uuid4()}",
        frame=LCM.Frame(
            point_clouds=[
                PointCloud(
                    filename="./examples/resources/point_cloud_RFL01.las",
                    sensor_name=lidar_sensor1,
                )
            ],
            images=[
                Image(
                    filename="./examples/resources/img_RFC01.jpg",
                    sensor_name=cam_sensor1,
                ),
                Image(
                    filename="./examples/resources/img_RFC02.jpg",
                    sensor_name=cam_sensor2,
                ),
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
    project = "<project-identifier>"

    run(client, project=project)

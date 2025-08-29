from __future__ import absolute_import

import os.path
from typing import Optional
from uuid import uuid4

import kognic.io.model.scene.lidars as LM
from examples.imu_data.create_imu_data import create_dummy_imu_data
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, PointCloud


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> Optional[CreateSceneResponse]:
    print("Creating Lidars Scene...")

    lidar_sensor1 = "lidar"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    imu_data = create_dummy_imu_data(1557539923, 1557539925, int(1e9))
    examples_path = os.path.dirname(__file__)
    scene = LM.Lidars(
        external_id=f"lidars-with-imu-data-example-{uuid4()}",
        frame=LM.Frame(
            point_clouds=[PointCloud(filename=examples_path + "/resources/point_cloud_RFL01.las", sensor_name=lidar_sensor1)],
            unix_timestamp=1644223851 * 1e9,
        ),
        metadata=metadata,
        imu_data=imu_data,
    )

    # Create scene
    return client.lidars.create(scene, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-identifier>"
    run(client, project=project)

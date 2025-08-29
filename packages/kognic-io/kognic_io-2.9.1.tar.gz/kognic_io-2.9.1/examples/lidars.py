from __future__ import absolute_import

from uuid import uuid4

import kognic.io.model.scene.lidars as LM
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, PointCloud
from kognic.io.model.scene.metadata.metadata import MetaData


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> CreateSceneResponse:
    print("Creating Lidars Scene...")

    lidar_sensor1 = "lidar"
    metadata = MetaData.model_validate({"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"})

    lidars = LM.Lidars(
        external_id=f"lidars-example-{uuid4()}",
        frame=LM.Frame(point_clouds=[PointCloud(filename="./examples/resources/point_cloud_RFL01.las", sensor_name=lidar_sensor1)]),
        metadata=metadata,
    )

    # Create scene
    return client.lidars.create(lidars, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-identifier>"
    run(client, project=project)

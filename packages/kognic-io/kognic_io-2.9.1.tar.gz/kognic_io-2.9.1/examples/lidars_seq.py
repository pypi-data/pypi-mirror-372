from __future__ import absolute_import

from typing import Optional
from uuid import uuid4

import kognic.io.model.scene.lidars_sequence as LSM
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, PointCloud


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> Optional[CreateSceneResponse]:
    print("Creating Lidar Sequence Scene...")

    lidar_sensor1 = "lidar"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    scene = LSM.LidarsSequence(
        external_id=f"lidars-seq-example-{uuid4()}",
        frames=[
            LSM.Frame(
                frame_id="1",
                relative_timestamp=0,
                point_clouds=[
                    PointCloud(filename="./examples/resources/point_cloud_RFL01.las", sensor_name=lidar_sensor1),
                ],
                metadata={"dut_status": "active"},
            ),
            LSM.Frame(
                frame_id="2",
                relative_timestamp=100,
                point_clouds=[
                    PointCloud(filename="./examples/resources/point_cloud_RFL02.las", sensor_name=lidar_sensor1),
                ],
                metadata={"dut_status": "active"},
            ),
        ],
        metadata=metadata,
    )
    # Create scene
    return client.lidars_sequence.create(scene, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-identifier>"
    run(client, project=project)

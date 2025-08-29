from __future__ import absolute_import

from datetime import datetime
from typing import Optional
from uuid import uuid4

import kognic.io.model.scene.lidars_and_cameras_sequence as LCSM
from examples.calibration.calibration import create_sensor_calibration
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, EgoVehiclePose, Image, PointCloud, Position, RotationQuaternion


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> Optional[CreateSceneResponse]:
    print("Creating Lidar and Camera Sequence Scene...")

    lidar_sensor1 = "lidar"
    cam_sensor1 = "RFC01"
    cam_sensor2 = "RFC02"
    cam_sensor3 = "RFC03"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    # Create calibration
    calibration_spec = create_sensor_calibration(f"Collection {datetime.now()}", [lidar_sensor1], [cam_sensor1, cam_sensor2, cam_sensor3])
    created_calibration = client.calibration.create_calibration(calibration_spec)

    scene = LCSM.LidarsAndCamerasSequence(
        external_id=f"LCS-full-example-{uuid4()}",
        frames=[
            LCSM.Frame(
                frame_id="1",
                relative_timestamp=0,
                point_clouds=[
                    PointCloud(filename="./examples/resources/point_cloud_RFL01.las", sensor_name=lidar_sensor1),
                ],
                images=[
                    Image(filename="./examples/resources/img_RFC01.jpg", sensor_name=cam_sensor1),
                    Image(filename="./examples/resources/img_RFC02.jpg", sensor_name=cam_sensor2),
                ],
                metadata={"dut_status": "active"},
                ego_vehicle_pose=EgoVehiclePose(
                    position=Position(x=1.0, y=1.0, z=1.0), rotation=RotationQuaternion(w=0.01, x=1.01, y=1.01, z=1.01)
                ),
            ),
            LCSM.Frame(
                frame_id="2",
                relative_timestamp=500,
                point_clouds=[
                    PointCloud(filename="./examples/resources/point_cloud_RFL02.las", sensor_name=lidar_sensor1),
                ],
                images=[
                    Image(filename="./examples/resources/img_RFC11.jpg", sensor_name=cam_sensor1),
                    Image(filename="./examples/resources/img_RFC12.jpg", sensor_name=cam_sensor2),
                ],
                ego_vehicle_pose=EgoVehiclePose(
                    position=Position(x=2.0, y=2.0, z=2.0), rotation=RotationQuaternion(w=0.01, x=2.01, y=2.01, z=2.01)
                ),
            ),
        ],
        calibration_id=created_calibration.id,
        metadata=metadata,
    )
    # Create scene
    return client.lidars_and_cameras_sequence.create(scene, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    client = KognicIOClient()

    # Project - Available via `client.project.get_projects()`
    project = "<project-identifier>"

    run(client, project=project)

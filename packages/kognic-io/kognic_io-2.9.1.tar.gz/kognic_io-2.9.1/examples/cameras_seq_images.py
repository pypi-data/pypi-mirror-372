from __future__ import absolute_import

from typing import Optional
from uuid import uuid4

import kognic.io.model.scene.cameras_sequence as CSM
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import CreateSceneResponse, Image


def run(client: KognicIOClient, dryrun: bool = True, **kwargs) -> Optional[CreateSceneResponse]:
    print("Creating Cameras Sequence Scene...")

    sensor1 = "RFC01"
    sensor2 = "RFC02"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    scene = CSM.CamerasSequence(
        external_id=f"camera-seq-images-example-{uuid4()}",
        frames=[
            CSM.Frame(
                frame_id="1",
                relative_timestamp=0,
                images=[
                    # JPG Images in Frame 1
                    Image(
                        filename="./examples/resources/img_RFC01.jpg",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC02.jpg",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
            CSM.Frame(
                frame_id="2",
                relative_timestamp=500,
                images=[
                    # PNG Images in Frame 2
                    Image(
                        filename="./examples/resources/img_RFC11.png",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC12.png",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
            CSM.Frame(
                frame_id="3",
                relative_timestamp=1000,
                images=[
                    # WebP VP8 Images in Frame 3
                    Image(
                        filename="./examples/resources/img_RFC21.webp",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC22.webp",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
            CSM.Frame(
                frame_id="4",
                relative_timestamp=1500,
                images=[
                    # WebP VP8L Images in Frame 4
                    Image(
                        filename="./examples/resources/img_RFC31.webp",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC32.webp",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
            CSM.Frame(
                frame_id="5",
                relative_timestamp=2000,
                images=[
                    # WebP VP8X Images in Frame 5
                    Image(
                        filename="./examples/resources/img_RFC41.webp",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC42.webp",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
            CSM.Frame(
                frame_id="6",
                relative_timestamp=2500,
                images=[
                    # AVIF Images in Frame 6
                    Image(
                        filename="./examples/resources/img_RFC51.avif",
                        sensor_name=sensor1,
                    ),
                    Image(
                        filename="./examples/resources/img_RFC52.avif",
                        sensor_name=sensor2,
                    ),
                ],
                metadata={"dut_status": "active"},
            ),
        ],
        metadata=metadata,
    )

    # Create scene
    return client.cameras_sequence.create(scene, dryrun=dryrun, **kwargs)


if __name__ == "__main__":
    setup_logging(level="INFO")
    # Project - Available via `client.project.get_projects()`
    project = "<project-identifier>"

    client = KognicIOClient()
    run(client, project=project)

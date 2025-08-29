from __future__ import absolute_import

from uuid import uuid4

import kognic.io.model.scene.cameras_sequence as CSM
from kognic.io.client import KognicIOClient
from kognic.io.logger import setup_logging
from kognic.io.model import VideoFrame


def run(client: KognicIOClient, dryrun: bool = True, **kwargs):
    print("Creating Cameras Sequence Scene...")

    sensor1 = "RFC01"
    sensor2 = "RFC02"
    metadata = {"location-lat": 27.986065, "location-long": 86.922623, "vehicle_id": "abg"}

    scene = CSM.CamerasSequence(
        external_id=f"camera-seq-videos-example-{uuid4()}",
        frames=[
            CSM.Frame(
                frame_id="1",
                relative_timestamp=0,
                video_frames=[
                    VideoFrame(filename="./examples/resources/video_RFC01.mp4", sensor_name=sensor1, video_timestamp=0),
                    VideoFrame(filename="./examples/resources/video_RFC02.mp4", sensor_name=sensor2, video_timestamp=0),
                ],
            ),
            CSM.Frame(
                frame_id="2",
                relative_timestamp=500,
                video_frames=[
                    VideoFrame(filename="./examples/resources/video_RFC01.mp4", sensor_name=sensor1, video_timestamp=100),
                    VideoFrame(filename="./examples/resources/video_RFC02.mp4", sensor_name=sensor2, video_timestamp=100),
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

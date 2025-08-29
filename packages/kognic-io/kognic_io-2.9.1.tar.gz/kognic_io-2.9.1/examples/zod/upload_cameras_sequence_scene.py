import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from conversion import convert_zod_camera_frame_to_image
from utils import ns_to_ms, seconds_to_ns
from zod.constants import Camera as ZodCamera
from zod.constants import Version as ZodVersion
from zod.zod_sequences import ZodSequence, ZodSequences

from kognic.io.client import KognicIOClient
from kognic.io.model import CamerasSequence
from kognic.io.model.scene.cameras_sequence import Frame as CSFrame

logging.basicConfig(level=logging.WARNING)

LARGE_NUMBER = 1000000


def upload_cameras_sequence_scenes(
    zod_path: Path,
    zod_version: ZodVersion,
    client: KognicIOClient,
    max_nr_scenes: Optional[int],
    max_nr_frames: Optional[int],
    dryrun: bool,
) -> None:
    sequences = ZodSequences(str(zod_path), version=zod_version)
    for key in sorted(sequences.get_all_ids())[: max_nr_scenes or LARGE_NUMBER]:
        external_id = "sequences_" + key + "_" + str(uuid4())[:8]
        sequence = sequences[key]

        scene = convert_scene(sequence, external_id, max_nr_frames or LARGE_NUMBER)
        scene_uuid = create_scene(client, scene, dryrun=dryrun)
        print(f"Created scene with UUID: {scene_uuid}")


def create_scene(client: KognicIOClient, scene: CamerasSequence, dryrun: bool = False) -> str:
    created_scene = client.cameras_sequence.create(scene, dryrun=dryrun)
    if dryrun is False:
        return created_scene.scene_uuid


def convert_scene(zod_sequence: ZodSequence, external_id: str, max_nr_frames: int) -> CamerasSequence:
    frames = convert_frames(zod_sequence, max_nr_frames)
    return CamerasSequence(external_id=external_id, frames=frames)


def convert_frames(sequence: ZodSequence, max_nr_frames: int) -> list[CSFrame]:
    frames, seen_frame_timestamps = list(), set()
    start_ts_ms = ns_to_ms(seconds_to_ns(sequence.info.get_camera_frames()[0].time.timestamp()))

    for camera_frame in sequence.info.get_camera_frames(camera=ZodCamera.FRONT)[:max_nr_frames]:
        frame_ts_s = camera_frame.time.timestamp()

        if frame_ts_s in seen_frame_timestamps:
            continue

        seen_frame_timestamps.add(frame_ts_s)
        frame_ts_ns = seconds_to_ns(frame_ts_s)

        frames.append(
            CSFrame(
                relative_timestamp=ns_to_ms(frame_ts_ns) - start_ts_ms,
                frame_id=str(frame_ts_ns),
                images=[convert_zod_camera_frame_to_image(camera_frame)],
            )
        )
    return frames


if __name__ == "__main__":
    client = KognicIOClient()

    upload_cameras_sequence_scenes(
        zod_path=Path("/path/to/zod"),  # change me
        zod_version="mini",
        client=client,
        max_nr_scenes=1,
        max_nr_frames=10,
        dryrun=False,
    )

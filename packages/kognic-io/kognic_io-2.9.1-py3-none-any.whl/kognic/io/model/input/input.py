from kognic.io.model.base_serializer import BaseSerializer


class Input(BaseSerializer):
    uuid: str
    scene_uuid: str
    request_uid: str
    scene_external_id: str
    view_link: str

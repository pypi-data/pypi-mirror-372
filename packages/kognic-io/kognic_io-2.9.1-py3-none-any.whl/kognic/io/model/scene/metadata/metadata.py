from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

allowed_types = (int, float, str, bool)
allowed_types_pretty = [t.__name__ for t in allowed_types]


class MetaDataBase(BaseModel):
    """
    Base class for MetaData which only allows flat key-value pairs.
    """

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    def validate_flat_types(cls, values):
        return _validate_flat_types(values, cls.model_fields)


def _validate_flat_types(values: dict, reserved_fields: set):
    for key, val in values.items():
        if key in reserved_fields:
            continue

        if not isinstance(val, allowed_types):
            raise ValueError(
                f"Illegal Metadata value type for field '{key}'. Got '{type(val).__name__}', \
                but expected one of {allowed_types_pretty}"
            )

    return values


class MetaData(MetaDataBase):
    """
    Container for metadata belonging to the input.
    The attributes of this class are reserved keywords
    with associated functionality in the Kognic platform.

    Attributes:
        region: A string indicating the region the data was collected in.
            If there are annotation instructions associated with a specific
            region, talk to your contact at Kognic to sync what should be
            specified in the region attribute.
    """

    region: Optional[str] = None


class FrameMetaData(MetaDataBase):
    pass

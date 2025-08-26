import logging
from typing import Literal, Optional

from bliss.rest_service.typedef import (
    ObjectType,
    HardwareSchema,
    Field,
    CallableSchema,
    HardwareRefField,
)

logger = logging.getLogger(__name__)

SlitStates = ["READY"]

SlitTypes = ["horizontal", "vertical", "both"]


class _PropertiesSchema(HardwareSchema):
    state: Optional[Literal[tuple(SlitStates)]] = Field(None, read_only=True)
    type: Optional[Literal[tuple(SlitTypes)]] = Field(None, read_only=True)
    hgap: Optional[str] = HardwareRefField(None, read_only=True)
    vgap: Optional[str] = HardwareRefField(None, read_only=True)
    hoffset: Optional[str] = HardwareRefField(None, read_only=True)
    voffset: Optional[str] = HardwareRefField(None, read_only=True)


class _CallablesSchema(CallableSchema):
    pass


class SlitType(ObjectType):
    NAME = "slit"
    STATE_OK = [SlitStates[0]]

    PROPERTIES = _PropertiesSchema
    CALLABLES = _CallablesSchema


Default = SlitType

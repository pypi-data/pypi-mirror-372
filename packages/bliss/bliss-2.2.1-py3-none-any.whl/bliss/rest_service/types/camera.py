from __future__ import annotations
import logging
from typing import Literal, Optional

from bliss.rest_service.typedef import (
    ObjectType,
    HardwareSchema,
    Field,
    CallableSchema,
    Callable1Arg,
)

logger = logging.getLogger(__name__)

CameraStates = ["READY", "ACQUIRING", "UNKNOWN", "ERROR"]


class CameraPropertiesSchema(HardwareSchema):
    state: Optional[Literal[tuple(CameraStates)]] = Field(None, read_only=True)
    exposure: Optional[float] = None
    gain: Optional[float] = None
    mode: Optional[str] = Field(None, read_only=True)
    live: Optional[bool] = None
    width: Optional[int] = Field(None, read_only=True)
    height: Optional[int] = Field(None, read_only=True)


class CameraCallablesSchema(CallableSchema):
    save: Callable1Arg[str]


class CameraType(ObjectType):
    NAME = "camera"
    STATE_OK = [CameraStates[0], CameraStates[1]]

    PROPERTIES = CameraPropertiesSchema
    CALLABLES = CameraCallablesSchema


Default = CameraType

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from bliss.rest_service.mappingdef import (
    ObjectMapping,
    HardwareProperty,
    ObjectRefProperty,
)
from ..types.slit import SlitType

logger = logging.getLogger(__name__)


class Slit(ObjectMapping):
    TYPE = SlitType

    def _get_state(self):
        return "READY"

    def _get_role(self, role: str):
        obj = self._object
        axis = [a for a in obj.pseudos if obj._axis_tag(a) == role]
        if len(axis) > 0:
            return axis[0]
        # in case of invslit
        axis = [a for a in obj.reals if obj._axis_tag(a) == role]
        if len(axis) > 0:
            return axis[0]
        return None

    def _get_hgap(self):
        return self._get_role("hgap")

    def _get_vgap(self):
        return self._get_role("vgap")

    def _get_hoffset(self):
        return self._get_role("hoffset")

    def _get_voffset(self):
        return self._get_role("voffset")

    PROPERTY_MAP = {
        "state": HardwareProperty("state", _get_state),
        "type": HardwareProperty("slit_type"),
        "hgap": ObjectRefProperty("hgap", True, _get_hgap),
        "vgap": ObjectRefProperty("vgap", True, _get_vgap),
        "hoffset": ObjectRefProperty("hoffset", True, _get_hoffset),
        "voffset": ObjectRefProperty("voffset", True, _get_voffset),
    }

    CALLABLE_MAP = {}


Default = Slit

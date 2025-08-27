# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from .lima_base import CameraBase


class Camera(CameraBase):
    def to_dict(self, *args, **kwargs):
        kwargs["include_properties"] = (
            "acquisition_mode",
            "config_name",
            "flat_field_correction_flag",
            "geometrical_correction_flag",
            "ithl_offset",
            "output_signal",
        )
        return super().to_dict(*args, **kwargs)

    @property
    def synchro_mode(self):
        return "IMAGE"

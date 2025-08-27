# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from .lima_base import CameraBase


class Camera(CameraBase):
    def to_dict(self, *args, **kwargs):
        kwargs["include_properties"] = ("pixel_depth", "threshold_energy")
        return super().to_dict(*args, **kwargs)

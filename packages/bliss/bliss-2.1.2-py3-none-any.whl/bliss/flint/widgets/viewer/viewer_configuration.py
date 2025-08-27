# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations


class ViewerConfiguration:
    """Store a viewer configuration for serialization"""

    def __init__(self):
        # Mode
        self.interaction_mode: str | None = None
        self.refresh_mode: int | None = None
        # Axis
        self.x_axis_scale: str | None = None
        self.y_axis_scale: str | None = None
        self.y2_axis_scale: str | None = None
        self.y_axis_inverted: bool = False
        self.y2_axis_inverted: bool = False
        self.fixed_aspect_ratio: bool = False
        self.use_data_margins: bool | None = True
        # View
        self.grid_mode: bool = False
        self.axis_displayed: bool = True
        # Tools
        self.crosshair_enabled: bool = False
        self.colorbar_displayed: bool = False
        self.profile_widget_displayed: bool = False
        self.roi_widget_displayed: bool = False
        self.histogram_widget_displayed: bool = False

        # Widget displaying dedicated detectors (MCAs, images, one dim)
        self.device_name: str | None = None

        # Curve widget
        self.spec_mode: bool = False
        self.x_duration: int | None = None
        self.x_duration_enabled: bool = False
        self.previous_scans_displayed: bool = False
        self.previous_scans_stack_size: int = 3

        # Image widget
        self.flatfield_stage = False
        self.mask_stage = False
        self.expotime_stage = False
        self.statistics_stage = True
        self.saturation_stage = False
        self.saturation_stage_value = None
        self.diffraction_stage = False
        self.diffraction_stage_is_rings_visible = True
        self.diffraction_stage_tooltip_units = None

        # Image/scatter widget
        self.colormap: dict | None = None
        self.profile_state: bytes | None = None

        # Image
        self.side_profile_displayed: bool = False

    def __reduce__(self):
        return (self.__class__, (), self.__getstate__())

    def __getstate__(self):
        """Inherit the serialization to make sure the object can grow up in the
        future"""
        state: dict[str, object] = {}
        state.update(self.__dict__)
        return state

    def __setstate__(self, state):
        """Inherit the serialization to make sure the object can grow up in the
        future"""
        for k in self.__dict__.keys():
            if k in state:
                v = state.pop(k)
                self.__dict__[k] = v

    def __str__(self):
        return self.__dict__.__str__()

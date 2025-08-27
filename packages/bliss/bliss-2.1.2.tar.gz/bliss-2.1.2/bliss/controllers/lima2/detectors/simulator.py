# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numbers

from bliss.common.utils import typecheck
from bliss.common.counter import SamplingCounter
from bliss.common.protocols import counter_namespace

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.controller import DetectorStatusController
from bliss.controllers.lima2.settings import Settings, setting_property


class Detector(Settings):
    """Simulator detector user interface"""

    def __init__(self, device):
        self._params = device._ctrl_params["det"]
        super().__init__(device._config, path=["simulator"])

        self._det_cc = DetectorStatusController(device)
        self._temperature_cnt = SamplingCounter(
            "temperature", self._det_cc, unit="degC"
        )
        self._humidity_cnt = SamplingCounter("humidity", self._det_cc, unit="%")

        class Generator(Settings):
            """
            {
                "type": "gauss",
                "gauss": {
                    "peaks": [{"x0": 1024.0, "y0": 1024.0, "fwhm": 128.0, "max": 100.0}],
                    "grow_factor": 0.0,
                },
                "diffraction": {
                    "x0": 1024.0,
                    "y0": 1024.0,
                    "source_pos_x": 5.0,
                    "source_pos_y": 5.0,
                    "source_speed_x": 0.0,
                    "source_speed_y": 0.0,
                },
                "pixel_type": "gray8",
            }

            """

            def __init__(self, device):
                self._params = device._ctrl_params["det"]["generator"]
                super().__init__(device._config, path=["simulator", "generator"])

            @setting_property(default="gauss")
            def type(self):
                return self._params["type"]

            @type.setter
            @typecheck
            def type(self, value: str):
                self._params["type"] = value

            @setting_property(default="gray16")
            def pixel_type(self):
                return self._params["pixel_type"]

            @pixel_type.setter
            @typecheck
            def pixel_type(self, value: str):
                self._params["pixel_type"] = value

            @setting_property(default=1)
            def nb_channels(self):
                return self._params["nb_channels"]

            @nb_channels.setter
            @typecheck
            def nb_channels(self, value: int):
                self._params["nb_channels"] = value

            @setting_property(
                default=[{"x0": 1024.0, "y0": 1024.0, "fwhm": 128.0, "max": 100.0}]
            )
            def peaks(self):
                return self._params["gauss"]["peaks"]

            @peaks.setter
            @typecheck
            def peaks(self, value: list):
                self._params["gauss"]["peaks"] = value

            @setting_property(default=0.0)
            def grow_factor(self):
                return self._params["gauss"]["grow_factor"]

            @grow_factor.setter
            @typecheck
            def grow_factor(self, value: numbers.Real):
                self._params["gauss"]["grow_factor"] = value

            def __info__(self):
                return tabulate(self._params) + "\n\n"

        self.generator = Generator(device)

    @setting_property(default="generator")
    def source(self):
        return self._params["image_source"]

    @source.setter
    @typecheck
    def source(self, value: str):
        self._params["image_source"] = value

    @setting_property(default=1)
    def nb_prefetch_frames(self):
        return self._params["nb_prefetch_frames"]

    @nb_prefetch_frames.setter
    @typecheck
    def nb_prefetch_frames(self, value: numbers.Integral):
        self._params["nb_prefetch_frames"] = value

    def __info__(self):
        return (
            f"{self.source.title()}:\n"
            + f"nb_prefetch_frames: {self.nb_prefetch_frames}\n\n"
            + getattr(self, self.source).__info__()
        )

    @property
    def counters(self):
        return [
            self._temperature_cnt,
            self._humidity_cnt,
        ]

    @property
    def counter_groups(self):
        res = {}
        res["health"] = counter_namespace([self._temperature_cnt, self._humidity_cnt])
        return res

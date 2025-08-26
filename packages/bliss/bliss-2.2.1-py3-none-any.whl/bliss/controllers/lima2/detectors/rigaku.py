# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from bliss.common.utils import typecheck
from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.controller import (
    DetectorController,
)
from bliss.controllers.lima2.settings import Settings, setting_property


class Detector:
    """Rigaku detector user interface"""

    def __init__(self, device):
        self._frame_cc = DetectorController(device)

        class Acquisition(Settings):
            """
            {
                'thresholds': [{
                    'energy': 4020.5,
                    'enabled': True
                }, {
                    'energy': 4020.5,
                    'enabled': True
                }],
                'trigger_start_delay': 0.0,
                'roi': 'full',
                'nb_pipeline_threads': 1
            }
            """

            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["det"]
                super().__init__(device._config, path=["rigaku", "acquisition"])

            @setting_property(default="4.5-12.0keV")
            def calibration_data_label(self):
                return self._params["calibration_data_label"]

            @calibration_data_label.setter
            @typecheck
            def calibration_data_label(self, value: str):
                self._params["calibration_data_label"] = value

            @setting_property(default=4.5)
            def energy_threshold_low(self):
                return self._params["energy_threshold_low"]

            @energy_threshold_low.setter
            @typecheck
            def energy_threshold_low(self, value: float):
                self._params["energy_threshold_low"] = value

            @setting_property(default=12.0)
            def energy_threshold_high(self):
                return self._params["energy_threshold_high"]

            @energy_threshold_high.setter
            @typecheck
            def energy_threshold_high(self, value: float):
                self._params["energy_threshold_high"] = value

            @setting_property(default="b16_1s")
            def imaging_mode(self):
                return self._params["imaging_mode"]

            @imaging_mode.setter
            @typecheck
            def imaging_mode(self, value: str):
                self._params["imaging_mode"] = value

            @setting_property(default="fixed_time")
            def acquisition_mode(self):
                return self._params["acquisition_mode"]

            @acquisition_mode.setter
            @typecheck
            def acquisition_mode(self, value: str):
                self._params["acquisition_mode"] = value

            @setting_property(default="unsigned_16bit")
            def output_mode(self):
                return self._params["output_mode"]

            @output_mode.setter
            @typecheck
            def output_mode(self, value: str):
                self._params["output_mode"] = value

            @setting_property(default=1)
            def nb_pileup(self):
                return self._params["nb_pileup"]

            @nb_pileup.setter
            @typecheck
            def nb_pileup(self, value: int):
                self._params["nb_pileup"] = value

            @setting_property(default=False)
            def enable_diversion(self):
                return self._params["enable_diversion"]

            @enable_diversion.setter
            @typecheck
            def enable_diversion(self, value: bool):
                self._params["enable_diversion"] = value

            @setting_property(default="/tmp")
            def diversion_filename(self):
                return self._params["diversion_base_path"]

            @diversion_filename.setter
            @typecheck
            def diversion_filename(self, value: str):
                self._params["diversion_base_path"] = value

            @setting_property(default=1)
            def nb_frames(self):
                return self._params["nb_frames"]

            @nb_frames.setter
            @typecheck
            def nb_frames(self, value: int):
                self._params["nb_frames"] = value

            def __info__(self):
                return "Acquisition:\n" + tabulate(self._params) + "\n\n"

        class Experiment(Settings):
            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["exp"]
                super().__init__(device._config, path=["dectris", "experiment"])

            def __info__(self):
                return "Experiment:\n" + tabulate(self._params) + "\n\n"

        self.acquisition = Acquisition(device)
        # self.experiment = Experiment(device)

    def __info__(self):
        return (
            self.acquisition.__info__()
            # + self.experiment.__info__()
        )

    @property
    def counters(self):
        return []

    @property
    def counter_groups(self):
        res = {}
        return res

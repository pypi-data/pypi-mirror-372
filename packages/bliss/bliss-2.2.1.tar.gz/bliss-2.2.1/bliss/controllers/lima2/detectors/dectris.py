# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numbers
import gevent
import requests
import json
import base64
import numpy
import fabio

from bliss.common.utils import typecheck
from bliss.common.counter import SamplingCounter
from bliss.common.protocols import counter_namespace
from bliss.common.user_status_info import status_message

from bliss.controllers.lima2.tabulate import tabulate
from bliss.controllers.lima2.counter import FrameCounter
from bliss.controllers.lima2.controller import (
    DetectorController,
    DetectorStatusController,
)
from bliss.controllers.lima2.settings import Settings, setting_property

DECTRIS_TO_NUMPY = {"<u4": numpy.uint32, "<f4": numpy.float32}


class Detector:
    """Dectris Eiger2 detector user interface"""

    def __init__(self, device):
        self._det_cc = DetectorStatusController(device)
        self._frame_cc = DetectorController(device)

        self._config = device._config.get("dectris", {})
        self._dcu_ip = self._config.get("ip_address", None)

        self._temperature_cnt = SamplingCounter(
            "temperature", self._det_cc, unit="degC"
        )
        self._humidity_cnt = SamplingCounter("humidity", self._det_cc, unit="%")
        self._raw_frame_cnt = FrameCounter(
            "raw_frame", device._frame_cc, ("recvs", "saving"), file_only=True
        )

        class Acquisition(Settings):
            """
            {
                'thresholds': [{
                    'energy': 4020.5,
                    'enabled': True
                }, {
                    'energy': 4020.5,
                    'enabled': True
                }, ...],
                'trigger_start_delay': 0.0,
                'roi': 'full',
                'nb_pipeline_threads': 1
            }
            """

            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["det"]

                # Construct the missing threshold parameters
                nb_thresholds = device.det_info["nb_thresholds"]
                nb_thresholds_in_settings = len(self._params["thresholds"])
                for i in range(nb_thresholds_in_settings, nb_thresholds):
                    self._params["thresholds"].insert(
                        i, {"enabled": i == 0, "energy": 4020.5}
                    )

                # Insert getters & setters for threshold parameters
                for i in range(nb_thresholds):

                    def make_fget(i, param):
                        def fget_inner(self):
                            return self._params["thresholds"][i][param]

                        fget_inner.__name__ = f"threshold{i}_{param}"
                        return fget_inner

                    def make_fset(i, param):
                        def fset_inner(self, value):
                            self._params["thresholds"][i][param] = value

                        fset_inner.__name__ = f"threshold{i}_{param}"
                        return fset_inner

                    setattr(
                        Acquisition,
                        f"threshold{i}_enabled",
                        Settings._property(
                            make_fget(i, "enabled"),
                            make_fset(i, "enabled"),
                            default=True,
                        ),
                    )

                    setattr(
                        Acquisition,
                        f"threshold{i}_energy",
                        Settings._property(
                            make_fget(i, "energy"),
                            make_fset(i, "energy"),
                            default=4020.5,
                        ),
                    )

                super().__init__(device._config, path=["dectris", "acquisition"])

            @setting_property(default=False)
            def difference_enabled(self):
                return self._params["difference"]["enabled"]

            @difference_enabled.setter
            @typecheck
            def difference_enabled(self, value: bool):
                self._params["difference"]["enabled"] = value

            @setting_property(default="full")
            def roi(self):
                return self._params["roi"]

            @roi.setter
            @typecheck
            def roi(self, value: str):
                self._params["roi"] = value

            @setting_property(default=1)
            def nb_pipeline_threads(self):
                return self._params["nb_pipeline_threads"]

            @nb_pipeline_threads.setter
            @typecheck
            def nb_pipeline_threads(self, value: numbers.Integral):
                self._params["nb_pipeline_threads"] = value

            def __info__(self):
                return "Acquisition:\n" + tabulate(self._params) + "\n\n"

        class Experiment(Settings):
            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["exp"]
                super().__init__(device._config, path=["dectris", "experiment"])

            @setting_property(default=8041)
            def photon_energy(self):
                return self._params["photon_energy"]

            @photon_energy.setter
            @typecheck
            def photon_energy(self, value: numbers.Real):
                self._params["photon_energy"] = value

            def __info__(self):
                return "Experiment:\n" + tabulate(self._params) + "\n\n"

        class Saving(Settings):
            """ "
            {
                'enabled': False,
                'filename': {
                    'base_path': '/tmp',
                    'filename_format': '{filename_prefix}_{filename_rank}_{file_number:05d}{filename_suffix}',
                    'filename_prefix': 'lima2',
                    'filename_suffix': '.h5'
                }
            }
            """

            def __init__(self, device):
                self._device = device
                self._params = device._ctrl_params["saving"]
                super().__init__(device._config, path=["dectris", "saving"])

            @setting_property(default=False)
            def enabled(self):
                return self._params["enabled"]

            @enabled.setter
            @typecheck
            def enabled(self, value: bool):
                self._params["enabled"] = value

            @property
            def filename_prefix(self):
                return self._params["filename_prefix"]

            @filename_prefix.setter
            @typecheck
            def filename_prefix(self, value: str):
                self._params["filename_prefix"] = value

            @setting_property
            def nb_frames_per_file(self):
                return self._params["nb_frames_per_file"]

            @nb_frames_per_file.setter
            @typecheck
            def nb_frames_per_file(self, value: int):
                self._params["nb_frames_per_file"] = value

            def __info__(self):
                return "Saving:\n" + tabulate(self._params) + "\n\n"

        self.acquisition = Acquisition(device)
        self.experiment = Experiment(device)
        self.saving = Saving(device)

    def __info__(self):
        return (
            self.acquisition.__info__()
            + self.experiment.__info__()
            + self.saving.__info__()
        )

    @property
    def counters(self):
        return [
            self._temperature_cnt,
            self._humidity_cnt,
            self._raw_frame_cnt,
        ]

    @property
    def counter_groups(self):
        res = {}
        res["health"] = counter_namespace([self._temperature_cnt, self._humidity_cnt])
        res["images"] = counter_namespace([self._raw_frame_cnt])
        return res

    def __get_request_address(self, subsystem, name):
        if self._dcu_ip is None:
            raise RuntimeError("Dectris DCU IP address not configured")
        dcu = self._dcu_ip
        api = "1.8.0"
        return f"http://{dcu}/{subsystem}/api/{api}/{name}"

    def raw_command(self, subsystem, name, dict_data=None):
        address = self.__get_request_address(subsystem, name)
        if dict_data is not None:
            data_json = json.dumps(dict_data)
            request = requests.put(address, data=data_json)
        else:
            request = requests.put(address)
        if request.status_code != 200:
            raise RuntimeError(f"Command {address} failed")
        return request.json()

    def raw_get(self, subsystem, name):
        address = self.__get_request_address(subsystem, name)
        request = requests.get(address)
        if request.status_code != 200:
            raise RuntimeError(
                f"Failed to get {address}\nStatus code = {request.status_code}"
            )
        return request.json()

    def raw_put(self, subsystem, name, dict_data):
        address = self.__get_request_address(subsystem, name)
        data_json = json.dumps(dict_data)
        request = requests.put(address, data=data_json)
        if request.status_code != 200:
            raise RuntimeError(f"Failed to put {address}")
        return request.json()

    def get(self, subsystem, name):
        raw_data = self.raw_get(subsystem, name)
        if isinstance(raw_data["value"], dict):
            return self.__raw2numpy(raw_data)
        return raw_data["value"]

    def put(self, subsystem, name, value):
        dict_data = {"value": value}
        return self.raw_put(subsystem, name, dict_data)

    def __raw2numpy(self, raw_data):
        str_data = base64.standard_b64decode(raw_data["value"]["data"])
        data_type = DECTRIS_TO_NUMPY.get(raw_data["value"]["type"])
        arr_data = numpy.fromstring(str_data, dtype=data_type)
        arr_data.shape = tuple(raw_data["value"]["shape"])
        return arr_data

    def check_timing(self, count_time=None, frame_time=None):
        if frame_time and count_time:
            self.put("detector", "config/frame_time", frame_time)
            self.put("detector", "config/count_time", count_time)
        elif frame_time:
            self.put("detector", "config/count_time", frame_time)
            self.put("detector", "config/frame_time", frame_time)
        elif count_time:
            self.put("detector", "config/frame_time", count_time)
            self.put("detector", "config/count_time", count_time)
        res = dict()
        for name in [
            "count_time",
            "frame_time",
            "frame_count_time",
            "bit_depth_readout",
            "bit_depth_image",
        ]:
            res[name] = self.get("detector", f"config/{name}")
        return res

    def show_timing(self, count_time=None, frame_time=None):
        res = self.check_timing(count_time, frame_time)
        res["frequency"] = 1.0 / res["frame_time"]
        res["autosum"] = res["bit_depth_image"] == 32 and "YES" or "NO"
        txt = "count time          = {count_time} sec\n"
        txt += "frame time          = {frame_time} sec\n"
        txt += "frequency           = {frequency:.1f} Hz\n"
        txt += "readout bit depth   = {bit_depth_readout} bit\n"
        txt += "image bit depth     = {bit_depth_image} bit\n"
        txt += "auto summation used = {autosum}\n"
        if res["autosum"] == "YES":
            txt += "subframe count time = {frame_count_time} sec\n"
        print(txt.format(**res))

    def array2edf(self, subsystem, name, filename):
        arr_data = self.get(subsystem, name)
        if not isinstance(arr_data, numpy.ndarray):
            address = self.__get_request_address(subsystem, name)
            raise ValueError(f"{address} does not return an array !!")
        edf_file = fabio.edfimage.EdfImage(arr_data)
        edf_file.save(filename)

    def mask2lima(self, filename):
        arr_data = self.get("detector", "config/pixel_mask")
        lima_data = numpy.array(arr_data == 0, dtype=numpy.uint8)
        edf_file = fabio.edfimage.EdfImage(lima_data)
        edf_file.save(filename)

    def reset_high_voltage(self, reset_time=None, wait=True):
        if reset_time is not None:
            data = {"value": float(reset_time)}
            self.raw_command("detector", "command/hv_reset", data)
        else:
            self.raw_command("detector", "command/hv_reset")
        if wait:
            self.wait_high_voltage()

    def wait_high_voltage(self):
        widx = 0
        with status_message() as update:
            while True:
                gevent.sleep(0.5)
                state = self.get("detector", "status/high_voltage/state")
                if state == "READY":
                    break
                dots = "." * (widx % 4)
                update(f"High Voltage status: {state:10.10s} {dots:3.3s}")
                widx += 1
        print(f"High Voltage status: {state:20.20s}")

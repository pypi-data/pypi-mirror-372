# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging
import numpy as np

from bliss.common.protocols import (
    HasMetadataForDataset,
    HasMetadataForScanExclusive,
)
from bliss.controllers.counter import CounterController
from bliss.controllers.counter import (
    IntegratingCounterController,
    SamplingCounterController,
)
from bliss.scanning.acquisition.counter import (
    SamplingCounterAcquisitionSlave,
    IntegratingCounterAcquisitionSlave,
)

_logger = logging.getLogger("bliss.ctrl.lima2")


# Logger decorator
def logger(fn):
    def inner(*args, **kwargs):
        _logger.debug(f"Entering {fn.__name__}")
        to_execute = fn(*args, **kwargs)
        _logger.debug(f"Exiting {fn.__name__}")
        return to_execute

    return inner


class DetectorController(
    CounterController, HasMetadataForScanExclusive, HasMetadataForDataset
):
    """
    Detector controller.
    """

    DEVICE_TYPE = "lima2"

    TIMEOUT = 10.0

    @logger
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._dev = device

    @property
    def device(self):
        return self._dev

    # implements HasMetadataForDataset
    @logger
    def dataset_metadata(self) -> dict:
        description = f"{self._dev.det_info['plugin']}, {self._dev.det_info['model']}"
        pixel_size = self._dev.det_info["pixel_size"]
        return {
            "name": self.name,
            "description": description,
            "x_pixel_size": pixel_size["x"],
            "y_pixel_size": pixel_size["y"],
        }

    # implements HasMetadataForScanExclusive
    @logger
    def scan_metadata(self) -> dict:
        description = f"{self._dev.det_info['plugin']}, {self._dev.det_info['model']}"
        pixel_size = self._dev.det_info["pixel_size"]
        return {
            "type": "lima2",
            "description": description,
            "x_pixel_size": pixel_size["x"],
            "y_pixel_size": pixel_size["y"],
            "x_pixel_size@units": "m",
            "y_pixel_size@units": "m",
            # "camera_settings": camera_settings,
        }

    # }

    # implements CounterController
    # {
    # Called by scan builder (toolbox) after get_default_chain_parameters
    @logger
    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        """
        Returns an AcquisitionObject instance.

        This function is intended to be used by the `ChainNode`.
        `acq_params`, `ctrl_params` and `parent_acq_params` have to be `dict` (`None` not supported)

        In case a incomplete set of `acq_params` is provided `parent_acq_params` may eventually
        be used to complete `acq_params` before choosing which Acquisition Object needs to be
        instantiated or just to provide all necessary `acq_params` to the Acquisition Object.

        parent_acq_params should be inserted into `acq_params` with low priority to not overwrite
        explicitly provided `acq_params` i.e. by using `setdefault`
        """
        _logger.debug(f"{acq_params} {ctrl_params} {parent_acq_params}")

        # avoid cyclic import
        from bliss.scanning.acquisition.lima2 import Lima2AcquisitionMaster

        return Lima2AcquisitionMaster(
            self, self.name, ctrl_params=ctrl_params, **acq_params
        )

    # Called first by scan builder (toolbox) to get default scan params
    @logger
    def get_default_chain_parameters(self, scan_params, acq_params):
        """
        Returns completed acq_params with missing values guessed from scan_params
        in the context of default chain i.e. step-by-step scans.
        """
        # scan_params, parameters from user. Additional properties can be added?
        # acq_params "empty" to be filled for master, or filled by master if slaves
        _logger.debug(f"scan_params: {scan_params} acq_params: {acq_params}")

        npoints = scan_params.get("npoints", 1)
        count_time = scan_params.get("count_time", 1.0)

        # Get default trigger mode
        if "software" in self._dev.det_capabilities["trigger_modes"]:
            default_trigger_mode = "software"
        else:
            default_trigger_mode = "internal"

        # USE PROVIDED TRIGGER MODE ELSE USE DEFAULT VALUE
        trigger_mode = acq_params.get("trigger_mode", default_trigger_mode)

        # npoints = acq_params.get("acq_nb_frames", scan_params.get("npoints", 1))

        prepare_once = trigger_mode in (
            "software",
            "external",
            "gate",
        )

        # start always called once, then trigger called once (internal) or multiple times (software)
        start_once = True

        nb_frames = acq_params.get("nb_frames")
        if nb_frames is None:
            nb_frames = npoints if prepare_once else 1

        expo_time = acq_params.get("expo_time")
        if expo_time is None:
            expo_time = count_time

        # Return required parameters
        params = {}
        params["nb_frames"] = nb_frames
        params["expo_time"] = expo_time
        params["trigger_mode"] = trigger_mode
        # params["acq_mode"] = acq_params.get("acq_mode", "SINGLE")
        # params["wait_frame_id"] = range(npoints)
        params["prepare_once"] = prepare_once
        params["start_once"] = start_once
        params["is_saving"] = False

        _logger.debug(f"default_chain_parameters: {params}")
        return params

    def get_current_parameters(self):
        """Should return an exhaustive dict of parameters that will be send
        to the hardware controller at the beginning of each scan.
        These parametes may be overwritten by scan specific ctrl_params
        """

        from copy import deepcopy

        return deepcopy(
            {
                "ctrl": self._dev._ctrl_params,
                "recvs": self._dev._recvs_params,
                "procs": self._dev._processing._params,
            }
        )

    def apply_parameters(self, ctrl_params):
        # Nothing to do
        ...

    # }


class RoiStatController(IntegratingCounterController):
    def __init__(self, device, master_controller):
        super().__init__(
            "roi_counters",  # Automatically prefixed with master_controller name
            master_controller=master_controller,
            register_counters=False,
        )

        self._dev = device
        self._rois = None

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj

        if "expo_time" in parent_acq_params:
            count_time = parent_acq_params["expo_time"]
        else:
            count_time = acq_params["count_time"]

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return IntegratingCounterAcquisitionSlave(
            self,
            ctrl_params=ctrl_params,
            count_time=count_time,
            npoints=nb_frames,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        params = {"count_time": count_time}

        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params["npoints"] = npoints

        return params

    def get_values(self, from_index, *counters: list):
        """
        Return the counter values for the list of given counters.
        For each counter, data is a list of values (one per measurement).
        All counters must retrieve the same number of data!

        args:
            - from_index: an integer corresponding to the index of the
            measurement from which new data should be retrieved
            - counters: the list of counters for which measurements should be retrieved.
        """
        assert self._rois
        assert counters

        values = self._dev.current_pipeline.pop_roi_statistics()

        _logger.debug(f"pop_roi_statistics returned {len(values)} values")

        if not values:
            return [np.array([]) for c in counters]
        else:
            values = values[0]  # TODO

            # Expend structured type to multiple data arrays
            name2idx = {r.name: i for i, r in enumerate(self._rois)}
            res = []
            for c in counters:
                res.append(
                    values[name2idx[c.roi.name] :: len(self._rois)][c.stat.value]
                )

            return res


class RoiProfilesController(IntegratingCounterController):
    def __init__(self, device, master_controller):
        super().__init__(
            "roi_profiles",  # Automatically prefixed with master_controller name
            master_controller=master_controller,
            register_counters=False,
        )

        self._dev = device
        self._rois = None

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj

        if "expo_time" in parent_acq_params:
            count_time = parent_acq_params["expo_time"]
        else:
            count_time = acq_params["count_time"]

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return IntegratingCounterAcquisitionSlave(
            self,
            ctrl_params=ctrl_params,
            count_time=count_time,
            npoints=nb_frames,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        params = {"count_time": count_time}

        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params["npoints"] = npoints

        return params

    def get_values(self, from_index, *counters: list):
        """
        Return the counter values for the list of given counters.
        For each counter, data is a list of values (one per measurement).
        All counters must retrieve the same number of data!

        args:
            - from_index: an integer corresponding to the index of the
            measurement from which new data should be retrieved
            - counters: the list of counters for which measurements should be retrieved.
        """
        assert self._rois
        assert counters

        values = self._dev.current_pipeline.pop_roi_profiles()

        _logger.debug(f"pop_roi_profiles returned {len(values)} values")

        if not values:
            return [np.array([]) for c in counters]
        else:
            values = np.array(values[0])  # TODO

            def profile_length(roi):
                if roi.mode == "horizonthal":
                    len = roi.height
                elif roi.mode == "vertical":
                    len = roi.width

                return len

            frame_length = sum([profile_length(roi) for roi in self._rois])

            values = values.reshape((-1, frame_length))

            # Expend structured type to multiple data arrays
            name2idx = {r.name: i for i, r in enumerate(self._rois)}
            res = []
            for c in counters:
                res.append(
                    values[:, name2idx[c.roi.name] : profile_length(c.roi)][
                        c.stat.value
                    ].flatten()
                )

            return res


class DetectorStatusController(SamplingCounterController):
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._device = device

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        if "expo_time" in parent_acq_params:
            count_time = parent_acq_params["expo_time"]
        else:
            count_time = acq_params["count_time"]

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return SamplingCounterAcquisitionSlave(
            self,
            ctrl_params=ctrl_params,
            count_time=count_time,
            npoints=nb_frames,
        )

    def read_all(self, *counters):
        status = self._device.det_status

        values = []
        for cnt in counters:
            values.append(status[cnt.name])
        return values


class IntegratingController(IntegratingCounterController):
    def __init__(self, name, master_controller, device, getter):
        super().__init__(
            name, master_controller=master_controller, register_counters=False
        )

        self._device = device
        self._getter = getter

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        # Avoid RuntimeError: {'acq_params': [{'count_time': ['null value not allowed']}]}
        # when creating children in create_children_acq_obj
        if "expo_time" in parent_acq_params:
            count_time = parent_acq_params["expo_time"]
        else:
            count_time = acq_params["count_time"]

        if "nb_frames" in parent_acq_params:
            nb_frames = parent_acq_params["nb_frames"]
        else:
            nb_frames = acq_params["npoints"]

        return IntegratingCounterAcquisitionSlave(
            self,
            ctrl_params=ctrl_params,
            count_time=count_time,
            npoints=nb_frames,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        params = {"count_time": count_time}

        try:
            npoints = acq_params["npoints"]
        except KeyError:
            npoints = scan_params["npoints"]

        params["npoints"] = npoints

        return params

    def get_values(self, from_index, *counters):
        getter = getattr(self._device.current_pipeline, self._getter, None)
        if getter:
            values = getter()
            _logger.debug(f"{self._getter} returned {len(values)} values")
        else:
            _logger.error(
                f"{self._getter} is not available in {type(self._device.current_pipeline)}"
            )

        if not values:
            return [np.array([]) for c in counters]
        else:
            return [values[0] for cnt in counters]


class ProcessingController(CounterController):
    """
    Processing controller.
    """

    TIMEOUT = 10.0

    @logger
    def __init__(self, device):
        super().__init__(device.name, register_counters=False)

        self._dev = device

    # implements CounterController
    # {
    # Called by scan builder (toolbox) after get_default_chain_parameters
    @logger
    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        """
        Returns an AcquisitionObject instance.

        This function is intended to be used by the `ChainNode`.
        `acq_params`, `ctrl_params` and `parent_acq_params` have to be `dict` (`None` not supported)

        In case a incomplete set of `acq_params` is provided `parent_acq_params` may eventually
        be used to complete `acq_params` before choosing which Acquisition Object needs to be
        instantiated or just to provide all necessary `acq_params` to the Acquisition Object.

        parent_acq_params should be inserted into `acq_params` with low priority to not overwrite
        explicitly provided `acq_params` i.e. by using `setdefault`
        """
        _logger.debug(f"{acq_params} {ctrl_params} {parent_acq_params}")

        # avoid cyclic import
        from bliss.scanning.acquisition.lima2 import Lima2ProcessingSlave

        return Lima2ProcessingSlave(
            self, self.name + ":proc", ctrl_params=ctrl_params, **acq_params
        )

        # Called first by scan builder (toolbox) to get default scan params

    @logger
    def get_default_chain_parameters(self, scan_params, acq_params):
        return {}

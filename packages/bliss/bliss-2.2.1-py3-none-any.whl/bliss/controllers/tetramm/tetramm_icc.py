# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""CAENels TetrAMM picoammeter BLISS controller."""


import numpy as np
import gevent
from bliss.common import tango

from bliss.common.utils import BOLD, all_equal
from bliss.common.logtools import log_debug
from bliss.common.counter import IntegratingCounter
from bliss.common.protocols import HasMetadataForScanExclusive

from bliss.controllers.counter import (
    IntegratingCounterController,
    IntegratingCounterAcquisitionSlave,
)


class TetrammCounter(IntegratingCounter):
    def __init__(
        self,
        config,
        controller=None,
        conversion_function=None,
        unit=None,
        dtype=np.float64,
    ):

        self.channel = config.get("channel", default=None)
        conversion_function = config.get("conversion_function", default=None)

        super().__init__(
            name=config.get("name"),
            controller=controller,
            conversion_function=conversion_function,
            unit=config.get("unit", "A"),
        )

        if self.channel is not None:
            self.channel = int(self.channel)

    def scan_metadata(self):
        hw = self._counter_controller._hw

        meta_dict = {"@NX_class": "NXcollection"}
        meta_dict["bias"] = hw.bias
        meta_dict["range"] = hw.get_range(str(self.channel))[0]
        meta_dict["dark_offset"] = hw.get_dark_offset(str(self.channel))[0]
        return meta_dict


class TetrammICC(IntegratingCounterController, HasMetadataForScanExclusive):
    def __init__(self, name, controller):
        self.controller = controller
        self._hw = controller._hw
        self.burst_npulses = None

        super().__init__(name=name, master_controller=None, register_counters=True)

        self.xray_freq = 0
        self.single_pulse = True
        self.trigger_mode = "SOFTWARE"

    def get_acquisition_object(self, acq_params, ctrl_params, parent_acq_params):
        """
        Return a IntegratingCounterAcquisitionSlave.

        args:
         - `acq_params`: parameters for the acquisition object (dict)
         - `ctrl_params`: parameters for the controller (dict)
         - `parent_acq_params`: acquisition parameters of the master (if any)
        """
        self.trigger_mode = acq_params.pop("trigger_mode", "SOFTWARE")
        return TetrammICAS(
            self,
            trigger_mode=self.trigger_mode,
            ctrl_params=ctrl_params,
            **acq_params,
        )

    def get_default_chain_parameters(self, scan_params, acq_params):
        """
        Return necessary acquisition parameters in the context of step by
        step scans.

        args:
         - `scan_params`: parameters of the scan (dict)
         - `acq_params`: parameters for the acquisition (dict)

        return: a dictionary of acquisition parameters

        In the context of a step-by-step scan, `acq_params` is usually empty
        and the returned dict must be deduced from `scan_params`.

        However, in the case of a customized DEFAULT_CHAIN, `acq_params` may
        be not empty and these parameters must override the default ones.
        """
        try:
            count_time = acq_params["count_time"]
        except KeyError:
            count_time = scan_params["count_time"]

        params = {"count_time": count_time}

        if scan_params["npoints"] > 0:
            params["npoints"] = scan_params["npoints"]
        else:
            params["npoints"] = 1

        return params

    def get_values(self, from_index, *counters):
        """Get counter values corresponding to 'counters' as a list.

        For each counter, data is a list of values (one per measurement).
        All counters must retrieve the same number of data!

        args:
          - from_index: an integer corresponding to the index of the
            measurement from which new data should be retrieved
          - counters: the list of counters for which measurements should be
            retrieved.

        example:
            tmp = [self.get_available_measurements(cnt, from_index) for cnt in
                   counters]
            dmin = min([len(cnt_data) for cnt_data in tmp])


            return [cnt_data[:dmin] for cnt_data in tmp]
        """

        data = self._hw.get_data(from_index)  # flattened array of readouts

        if len(data) == 0:
            cnt_values = [[] for cnt in counters]

        else:
            nch = self._hw.last_nch

            nreadouts = len(data) // nch
            data = data.reshape((nreadouts, nch))
            # avg_data = np.mean(data, axis=0)

            log_debug(self, data)

            cnt_values = []
            for cnt in counters:
                # counter_readouts = list(avg_data[cnt.channel - 1])
                counter_readouts = list(data[:, cnt.channel - 1])
                cnt_values.append(counter_readouts)

        return cnt_values

    def scan_metadata(self):
        meta_dict = {"@NX_class": "NXcollection"}
        meta_dict["data_rate"] = self._hw.data_rate
        meta_dict["nrsamp"] = self._hw.nrsamp
        return meta_dict


class TetrammICAS(IntegratingCounterAcquisitionSlave):
    def __init__(
        self,
        *counters,
        ctrl_params=None,
        count_time=None,
        npoints=1,
        prepare_once=True,
        start_once=False,
        trigger_mode="SOFTWARE",
    ):
        self.trigger_mode = trigger_mode
        self._is_prepared = False
        self._readout_task = None

        super().__init__(
            *counters,
            count_time=count_time,
            npoints=npoints,
            prepare_once=prepare_once,
            start_once=start_once,
            ctrl_params=ctrl_params,
        )

        log_debug(self, "=== AcquisitionSlave: __init__()")

        try:
            # Make sur the
            self.device._hw.ping()
            self.device._hw.in_scan = (
                False  # TODO this should be handled somewhere else
            )
        except BaseException:
            pass

    def wait_ready(self):
        """Wait at beginning of scan and at beginning/end of the each point."""

        log_debug(self, "=== AcquisitionSlave: wait_ready() start")
        if not self._is_prepared:
            if self.device._hw.in_scan:
                raise RuntimeError(
                    "Another scan using the same counter is "
                    + "running (tetramm.ds.in_scan=True)."
                )

        log_debug(self, "=== AcquisitionSlave: wait_ready() stop")

        if self.trigger_mode in ["SOFTWARE", "HARDWARE_SINGLE"]:
            self.wait_readout()

    def _prepare_device(self):
        """
        Prepare device (tetramm) once.
        The underscore is needed to distinguish this method from the standard
        BLISS prepare_device().
        What we want here is to create a function that is called only through
        start_device() and not directly by BLISS.
        """
        naq = int(self.count_time * self.device._hw.data_rate)
        nch = self.device._hw.nch

        if self.trigger_mode == "SOFTWARE":
            log_debug(self, "=== AcquisitionSlave: --> SOFTWARE trigger")
            ntrg = 1
        elif self.trigger_mode == "HARDWARE_SINGLE":
            log_debug(self, "=== AcquisitionSlave: --> HARDWARE SINGLE trigger")
            ntrg = 1
        elif self.trigger_mode == "HARDWARE_MULTI":
            log_debug(self, "=== AcquisitionSlave: --> HARDWARE MULTI trigger")
            if self.device.single_pulse:
                ntrg = self.npoints
            else:
                ntrg = int(np.round(self.device.xray_freq * self.count_time, 0))
        else:
            raise RuntimeError(f"trigger_mode={self.trigger_mode} not recognized")

        self.device._hw.in_scan = True

        if naq >= 1:
            if self.trigger_mode.startswith("HARDWARE"):
                self.device._hw.trg_off()
                self.device._hw.trg_on()
            elif self.trigger_mode == "SOFTWARE":
                self.device._hw.trg_off()
            self.device._hw.prepare_acq_once([naq, ntrg, nch])
        else:
            raise RuntimeError(
                "'count_time' too small for TetrAMM 'data_rate'"
                + f"={self.device._hw.last_data_rate:g}Hz."
            )

        self._is_prepared = True

    def prepare_device(self):
        """
        Nothing to do since, we prefer to late prepare in the first call
        of the start_device(). By this way acq_on() cannot be executed
        if a Ctrl-C happens during the prepare phase. Remember that
        stop_device() is only called if start_device() has been run before.
        """
        pass

    def start_device(self):
        """
        Arm device: done at every scan point before trigger().

        The master will not trigger the aquisition (e.g. n354 burst) until
        the execution of this function is completed.

        For the above reason, data buffering cannot be initiated here.
        """
        log_debug(self, "=== AcquisitionSlave: start_device()")
        if not self._is_prepared:
            self._prepare_device()
        self.device._hw.acq_on()

        self._start_readout_task()
        # sleep to not loose the hw trigger if < 0.01 sec.
        gevent.sleep(0.005)

    def _do_readout(self):
        if self.device.controller.is_tango:
            try:
                # run an async. command
                idx = self.device._hw.command_inout_asynch("readout")
                while self.device._hw.state() == tango.DevState.RUNNING:
                    gevent.sleep(0.01)
                # and check for exception
                self.device._hw.command_inout_reply(idx)
            except BaseException:
                log_debug(self, "_do_readout(): Exception raised during readout")
                self._stop_flag = True
        else:
            try:
                return self.device._hw.readout()
            except BaseException:
                log_debug(self, "_do_readout(): Exception raised during readout")

    def _start_readout_task(self):
        if self._readout_task is None or self._readout_task.ready():
            self._readout_task = gevent.spawn(self._do_readout)

    def wait_readout(self):
        # Join readout greenlet
        if self._readout_task is not None:
            return self._readout_task.get()

    def reading(self):
        try:
            log_debug(self, "=== AcquisitionSlave: reading() try")
            from_index = 0
            while (
                not self.npoints or self._nb_acq_points < self.npoints
            ) and not self._stop_flag:
                counters = list(self._counters.keys())

                # data should be a list:
                # - each element of the list contains all readouts of a given
                #   counter
                # - all counters should have the same number of readouts
                data = [
                    counters[i].conversion_function(x)
                    for i, x in enumerate(self.device.get_values(from_index, *counters))
                ]
                # same as:
                # data = self.device.get_values(from_index, *counters)
                # if not conversion_function is applied

                # nch = self.device._hw.last_nch
                # data_rate = self.device._hw.last_data_rate
                # ndata_per_point = data_rate * self.count_time

                # nreadouts = len(data) // nch
                # data = data.reshape((ndata_per_point, nreadouts, nch))
                # data = np.mean(data, axis=1)

                if not all_equal([len(d) for d in data]):
                    raise RuntimeError("Read data can't have different sizes")

                if len(data[0]) > 0:
                    log_debug(
                        self,
                        "=== AcquisitionSlave: reading() while \n"
                        "===                   "
                        + BOLD(
                            f"from_index: {from_index}->" + f"{from_index+len(data[0])}"
                        ),
                    )
                    from_index += len(data[0])
                    self._nb_acq_points += len(data[0])
                    self._emit_new_data(data)
                    self.emit_progress_signal(
                        {"last_count_acquired": self._nb_acq_points}
                    )
                else:
                    gevent.sleep(0.1)
        finally:
            log_debug(self, "=== AcquisitionSlave: reading() finally")
            self.stop_device()

    def trigger(self):
        """
        Trigger the readout at every scan point.

        This is called always after acq_on() AND after the master has
        triggered the acquisition (e.g. after the call from within the n354
        controller trigger() function).

        Once the above is done, the burst at some point WILL BE sent.

        So, it is fine to start the data buffering here.
        """
        log_debug(self, "=== AcquisitionSlave: " + BOLD("trigger()"))

    def stop_device(self):
        """
        Stop device at the end of the scan or at CTRL-C.

        NOTE: if CTRL-C is pressed before start_device() is executed, the
              stop_device() is not called (that is why we are not using
              apply_parameters() anymore)
        Bliss call stop() which sets the _stop_flag to True, then reading() will
        call stop_device() in the finally statement.
        """
        log_debug(self, "=== AcquisitionSlave: stop()")
        if self.trigger_mode.startswith("HARDWARE"):
            # IT IS TOO EARLY TO STOP ACQ ?
            self.device._hw.trg_off()
        self.device._hw.acq_off()

        self.device._hw.empty_buffer()  # in principle not needed

        self.device._hw.in_scan = False

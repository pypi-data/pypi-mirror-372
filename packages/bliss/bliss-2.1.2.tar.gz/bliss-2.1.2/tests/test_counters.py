# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import pytest
import gevent
import h5py
import numpy
import tango
import mock

from beartype.roar import BeartypeCallHintParamViolation

from bliss.common.counter import SamplingCounter, SamplingMode, SoftCounter
from bliss.common.scans import loopscan, ct, ascan
from bliss import setup_globals
from bliss.common.soft_axis import SoftAxis

from bliss.controllers.counter import (
    IntegratingCounterController,
    SamplingCounterController,
)
from bliss.controllers.simulation_diode import (
    SimulationDiodeSamplingCounter,
    SimulationDiodeIntegratingCounter,
    SimulationDiodeController,
    CstSimulationDiodeSamplingCounter,
)
from bliss.scanning.chain import AcquisitionChain
from bliss.scanning.scan import Scan
from bliss.scanning.acquisition.counter import (
    IntegratingCounterAcquisitionSlave,
    SamplingCounterAcquisitionSlave,
)
from bliss.scanning.acquisition.timer import SoftwareTimerMaster


class Timed_Diode:
    """To be used in ascan as SoftAxis and SoftCounter at the same time"""

    def __init__(self):
        self.val = 0
        self.i = 0
        self.more_than_once = False

    def read(self):
        gevent.sleep((self.val % 5 + 1) * 0.002)
        self.i += 1
        return self.i

    def read_slow(self):
        gevent.sleep(0.2)
        return 17

    def read_fast(self):
        gevent.sleep((self.val % 5 + 1) * 0.002)
        return self.val

    def read_once(self):
        if self.more_than_once:
            raise RuntimeError
        else:
            self.more_than_once = True
            return 1

    def read_last(self):
        if self.more_than_once:
            return 2
        else:
            self.more_than_once = True
            return 1

    @property
    def position(self):
        return self.val

    @position.setter
    def position(self, val):
        self.val = val
        self.i = 0
        self.more_than_once = False


class DummyCounterController(IntegratingCounterController):
    def __init__(self):
        super().__init__("dummy_counter_controller")

    def get_values(self, from_index, *counters):
        gevent.sleep(0.01)
        shape = (len(counters), 10)
        return numpy.random.uniform(-100, 100, shape)


def test_diode(session):
    def multiply_by_two(x):
        diode.raw_value = x
        return 2 * x

    diode = SimulationDiodeSamplingCounter(
        "test_diode",
        SimulationDiodeController(),
        conversion_function=multiply_by_two,
        mode="LAST",
    )

    sc = ct(0.01, diode)
    diode_value = sc.get_data()["test_diode"][0]

    assert diode.raw_value * 2 == diode_value


def test_conversion_func(session):
    c = SoftCounter(
        value=lambda: 5,
        name="test",
        conversion_function=None,
        mode=SamplingMode.SINGLE,
    )

    assert c.data_dtype is numpy.float64
    with pytest.raises(AttributeError):
        c.data_dtype = int

    s = loopscan(1, 0.01, c, save=False)
    cnt_value = s.get_data()[c][0]
    assert cnt_value == 5
    assert type(cnt_value) is numpy.float64

    c = SoftCounter(
        value=lambda: 5,
        name="test",
        conversion_function=lambda x: 2 * x,
        mode=SamplingMode.SINGLE,
    )
    s = loopscan(1, 0.01, c, save=False)
    cnt_value = s.get_data()[c][0]
    assert pytest.approx(cnt_value) == 10
    assert type(cnt_value) is numpy.float64

    # let's remove the conversion function
    c.conversion_function = None
    s = loopscan(1, 0.01, c, save=False)
    cnt_value = s.get_data()[c][0]
    assert pytest.approx(cnt_value) == 5
    assert type(cnt_value) is numpy.float64

    # check conv func must be a callable
    with pytest.raises(BeartypeCallHintParamViolation):
        c.conversion_function = 0


def test_sampling_counter_mode(session):
    values = []

    def f(x):
        values.append(x)
        return x

    test_diode = SimulationDiodeSamplingCounter(
        "test_diode", SimulationDiodeController(), conversion_function=f
    )

    # USING DEFAULT MODE
    assert test_diode.mode.name == "MEAN"
    s = loopscan(1, 0.1, test_diode, save=False)
    # assert s.acq_chain.nodes_list[1].device.mode.name == "MEAN"
    assert s.get_data()["test_diode"] == pytest.approx(sum(values) / len(values))

    # UPDATING THE MODE
    values = []
    test_diode.mode = SamplingMode.INTEGRATE
    s = loopscan(1, 0.1, test_diode, save=False)
    assert s.get_data()["test_diode"] == pytest.approx(sum(values) * 0.1 / len(values))

    values = []
    test_diode.mode = "INTEGRATE"
    s = loopscan(1, 0.1, test_diode, save=False)
    assert s.get_data()["test_diode"] == pytest.approx(sum(values) * 0.1 / len(values))

    ## init as SamplingMode
    samp_cnt = SamplingCounter(
        "test_diode", SimulationDiodeController(), mode=SamplingMode.INTEGRATE
    )
    assert samp_cnt.mode.name == "INTEGRATE"

    ## init as String
    samp_cnt = SamplingCounter(
        "test_diode", SimulationDiodeController(), mode="INTEGRATE"
    )
    assert samp_cnt.mode.name == "INTEGRATE"

    ## init as something else
    with pytest.raises(KeyError):
        samp_cnt = SamplingCounter("test_diode", SimulationDiodeController(), mode=17)

    ## two counters with different modes on the same acq_device
    ## and check INTEGRATE mode produces MEAN * count_time
    sdc = SimulationDiodeController()
    cstdiode1 = CstSimulationDiodeSamplingCounter("cstdiode1", sdc)
    cstdiode2 = CstSimulationDiodeSamplingCounter("cstdiode2", sdc)
    cstval = 1
    cstdiode1.set_cst_value(cstval)
    cstdiode2.set_cst_value(cstval)
    cstdiode2.mode = "INTEGRATE"  # will publish mean value * count_time
    npoints = 10
    count_time = 0.1
    s = loopscan(10, count_time, cstdiode1, cstdiode2, save=False)
    res1 = numpy.sum(s.get_data("*cstdiode1"))
    res2 = numpy.sum(s.get_data("*cstdiode2")) / count_time
    assert res1 == cstval * npoints
    assert res1 == res2


def test_SampCnt_mode_SAMPLES_from_conf(session):
    diode2 = session.config.get("diode2")
    diode9 = session.config.get("diode9")
    assert diode9.mode.name == "SAMPLES"

    s = loopscan(10, 0.05, diode2, diode9, save=False)

    assert (
        "simulation_diode_sampling_controller:diode2"
        in s.scan_info["acquisition_chain"]["timer"]["scalars"]
    )
    assert (
        "simulation_diode_sampling_controller:diode9"
        in s.scan_info["acquisition_chain"]["timer"]["scalars"]
    )
    assert (
        "simulation_diode_sampling_controller:diode9_samples"
        in s.scan_info["acquisition_chain"]["timer"]["spectra"]
    )


def test_SampCnt_mode_STATS(session):
    o = Timed_Diode()

    ax = SoftAxis("test-sample-pos", o)
    c_slow = SoftCounter(o, "read_slow", name="test-sample", mode=SamplingMode.STATS)
    s_slow = loopscan(1, 0.1, c_slow, save=False)

    data_slow = s_slow.get_data()
    assert all(data_slow["test-sample"] == numpy.array([17]))
    assert all(data_slow["test-sample_N"] == numpy.array([1]))
    assert all(numpy.isnan(data_slow["test-sample_std"]))

    c_fast = SoftCounter(o, "read_fast", name="test-stat", mode=SamplingMode.STATS)
    c_fast.max_sampling_frequency = None

    s_fast = ascan(ax, 1, 9, 8, 0.1, c_fast, save=False)

    data_fast = s_fast.get_data()

    assert all(
        data_fast["test-stat"]
        == numpy.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    )
    assert all(
        data_fast["test-stat_std"]
        == numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    )
    assert all(
        data_fast["test-stat_var"]
        == numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    )
    assert all(
        data_fast["test-stat_p2v"]
        == numpy.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    )
    assert all(
        data_fast["test-stat_min"]
        == numpy.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    )
    assert all(
        data_fast["test-stat_max"]
        == numpy.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    )


def test_SampCnt_STATS_algorithm():
    statistics = numpy.array([0, 0, 0, numpy.nan, numpy.nan])
    dat = numpy.random.normal(10, 1, 100)
    for k in dat:
        statistics = SamplingCounterAcquisitionSlave.rolling_stats_update(statistics, k)

    stats = SamplingCounterAcquisitionSlave.rolling_stats_finalize(statistics)

    assert pytest.approx(stats.mean) == numpy.mean(dat)
    assert stats.N == len(dat)
    assert pytest.approx(stats.std) == numpy.std(dat)
    assert pytest.approx(stats.var) == numpy.var(dat)
    assert stats.min == numpy.min(dat)
    assert stats.max == numpy.max(dat)
    assert stats.p2v == numpy.max(dat) - numpy.min(dat)


def test_SampCnt_mode_SAMPLES(session):
    o = Timed_Diode()
    ax = SoftAxis("test-sample-pos", o)
    c_samp = SoftCounter(o, "read", name="test-samp", mode=SamplingMode.SAMPLES)
    s = ascan(ax, 1, 9, 8, 0.1, c_samp)

    assert (
        "Timed_Diode:test-samp" in s.scan_info["acquisition_chain"]["axis"]["scalars"]
    )
    assert (
        "Timed_Diode:test-samp_samples"
        in s.scan_info["acquisition_chain"]["axis"]["spectra"]
    )

    with h5py.File(s.writer.get_filename(), mode="r") as f:
        samples_h5 = numpy.array(f["1.1/measurement/test_samp_samples"])

    assert samples_h5.shape[0] == 9
    assert len(samples_h5.shape) == 2

    redis_dat = s.get_data()["test-samp_samples"]
    assert redis_dat.shape[0] == 9
    assert len(redis_dat.shape) == 2

    assert all(numpy.isnan(redis_dat.flatten()) == numpy.isnan(samples_h5.flatten()))
    mask = numpy.logical_not(numpy.isnan(redis_dat.flatten()))
    assert all((redis_dat.flatten() == samples_h5.flatten())[mask])


def test_SampCnt_mode_SINGLE(session):
    env_dict = session.env_dict

    diode2 = env_dict["diode2"]
    diode8 = env_dict["diode8"]
    assert diode8.mode == SamplingMode.SINGLE

    loops = loopscan(10, 0.1, diode2, diode8, save=False)
    diode2_dat = loops.get_data()["diode2"]
    diode8_dat = loops.get_data()["diode8"]

    # check that there is no averaging for diode10
    assert all(diode8_dat.astype(float) == diode8_dat)
    assert not all(diode2_dat.astype(int) == diode2_dat)


def test_SampCnt_mode_LAST(session):

    o = Timed_Diode()
    ax = SoftAxis("test-sample-pos", o)
    c = SoftCounter(o, "read_last", name="test", mode=SamplingMode.LAST)
    c.max_sampling_frequency = None

    s = ascan(ax, 1, 9, 8, 0.1, c, save=False)

    assert all(s.get_data()["test"] == numpy.array([2, 2, 2, 2, 2, 2, 2, 2, 2]))


def test_SampCnt_statistics(session):
    diode = session.config.get("diode")
    diode2 = session.config.get("diode2")

    ct(0.1, diode, diode2)
    statfields = (
        "mean",
        "N",
        "std",
        "var",
        "min",
        "max",
        "p2v",
        "count_time",
        "timestamp",
    )
    assert diode2.statistics._fields == statfields
    assert diode.statistics._fields == statfields
    assert diode2.statistics.N > 0
    assert diode2.statistics.std > 0


def test_SampCnt_mode_INTEGRATE_STATS(session):

    diode = session.config.get("diode")
    diode.mode = SamplingMode.INTEGRATE_STATS

    ct(0.1, diode)
    statfields = (
        "mean",
        "N",
        "std",
        "var",
        "min",
        "max",
        "p2v",
        "count_time",
        "timestamp",
    )
    assert diode.statistics._fields == statfields
    assert diode.statistics._fields == statfields
    assert diode.statistics.N > 0
    assert diode.statistics.std > 0

    statistics = numpy.array([0, 0, 0, numpy.nan, numpy.nan])
    dat = numpy.random.normal(10, 1, 100)
    for k in dat:
        statistics = SamplingCounterAcquisitionSlave.rolling_stats_update(statistics, k)

    stats = SamplingCounterAcquisitionSlave.rolling_stats_finalize(statistics)

    count_time = 0.1
    integ_stats = SamplingCounterAcquisitionSlave.STATS_to_INTEGRATE_STATS(
        stats, count_time
    )

    new_dat = dat * count_time

    assert pytest.approx(integ_stats.mean) == numpy.mean(new_dat)
    assert integ_stats.N == len(dat)
    assert pytest.approx(integ_stats.std) == numpy.std(new_dat)
    assert pytest.approx(integ_stats.var) == numpy.var(new_dat)
    assert integ_stats.min == numpy.min(new_dat)
    assert integ_stats.max == numpy.max(new_dat)
    assert pytest.approx(integ_stats.p2v) == numpy.max(new_dat) - numpy.min(new_dat)


def test_integ_counter(session):
    dcc = DummyCounterController()

    def multiply_by_two(x):
        dcc.raw_value = x
        return 2 * x

    diode = SimulationDiodeIntegratingCounter(
        "test_diode", dcc, conversion_function=multiply_by_two
    )

    sc = ct(0.01, diode)
    diode_value = sc.get_data()["test_diode"]

    assert list(diode_value) == list(2 * dcc.raw_value)


def test_bad_counters(session, beacon):
    diode = session.env_dict["diode"]
    simu_mca = beacon.get("simu1")
    setup_globals.simu_mca = simu_mca
    try:
        simu_mca._bad_counters = True
        ct(0.1, diode)
    finally:
        simu_mca._bad_counters = False


def test_single_integ_counter(default_session):
    timer = SoftwareTimerMaster(0.01, npoints=1)
    acq_controller = DummyCounterController()
    counter = SimulationDiodeIntegratingCounter("test_diode", acq_controller)
    acq_device = IntegratingCounterAcquisitionSlave(counter, count_time=0.01)
    chain = AcquisitionChain()
    chain.add(timer, acq_device)
    s = Scan(chain, save=False)
    with gevent.Timeout(2):
        s.run()


def test_prepare_once_prepare_many(session):
    diode = session.config.get("diode")
    diode2 = session.config.get("diode2")
    diode3 = session.config.get("diode3")

    s = loopscan(10, 0.1, diode2, run=False, save=False)
    d = SamplingCounterAcquisitionSlave(diode, count_time=0.1, npoints=10)
    s.acq_chain.add(s.acq_chain.nodes_list[0], d)

    # avoid discrepancy between scan_info and channels by updating scan_info by hand,
    # this is only for test purpose.
    s._scan_info["channels"].update({"simulation_diode_sampling_controller:diode": {}})
    s.run()
    dat = s.get_data()
    assert len(dat["diode2"]) == 10
    assert len(dat["diode"]) == 10

    # diode2 and diode3 are usually on the same SamplingCounterAcquisitionSlave
    # lets see if they can be split as well
    s = loopscan(10, 0.1, diode2, run=False, save=False)
    d = SamplingCounterAcquisitionSlave(diode3, count_time=0.1, npoints=10)
    s.acq_chain.add(s.acq_chain.nodes_list[0], d)

    # avoid discrepancy between scan_info and channels by updating scan_info by hand,
    # this is only for test purpose.
    s._scan_info["channels"].update({"simulation_diode_sampling_controller:diode3": {}})
    s.run()
    dat = s.get_data()
    assert len(dat["diode2"]) == 10
    assert len(dat["diode3"]) == 10


def test_tango_attr_counter(beacon, dummy_tango_server, session):
    _, device = dummy_tango_server
    counter = beacon.get("taac_dummy_position")

    # `taac_dummy_position` is a tango_attr_as_counter which refers to
    # "position" attribute of "id00/tango/dummy" test device.

    # Scalar attribute
    counter = beacon.get("taac_dummy_position")

    # Two elements of an array attribute
    taac_power_current = beacon.get("taac_undu_power_0")
    taac_power_max = beacon.get("taac_undu_power_1")

    sc = ct(0.01, counter, taac_power_current, taac_power_max)

    #    assert 0.136 == sc.get_data()["taac_undu_power_0"][0]
    #    assert 1.1 == sc.get_data()["taac_undu_power_1"][0]

    counter_value = sc.get_data()["taac_dummy_position"][0]

    assert pytest.approx(counter_value) == 1.41
    assert counter.unit == "mm"  # hard-coded in test config
    assert counter.format_string == "%3.2f"  # hard-coded in test config
    assert counter.mode == SamplingMode.MEAN  # default mode

    # test direct reading (outside of a scan or count)
    assert counter.value == 1.41
    assert counter.raw_value == 1.4078913

    with pytest.raises(RuntimeError) as exc_info:
        _ = beacon.get("wrong_counter")
    assert isinstance(exc_info.value.initial_cause, tango.DevFailed)

    # get BLISS tango_attr_as_counter counters
    taac_pos = beacon.get("taac_undu_position")
    taac_vel = beacon.get("taac_undu_velocity")

    # Test overwriting properties in BEACON configuration.
    assert taac_pos.format_string == "%5.3f"
    assert taac_pos.unit == "km"

    # Test no BEACON unit / no BEACON format
    taac_acc = beacon.get("taac_undu_acceleration")

    # Sampling modes fixed in config.
    assert taac_pos.mode == SamplingMode.MEAN
    assert taac_acc.mode == SamplingMode.LAST

    # Default sampling mode is MEAN
    assert taac_vel.mode == SamplingMode.MEAN

    with pytest.raises(RuntimeError) as exc_info:
        _ = beacon.get("taac_undu_wrong_attr_name")
    assert isinstance(exc_info.value.initial_cause, tango.DevFailed)

    # Get directly BLISS UNDULATOR object (not via tango_attr_as_counter)
    # to compare taac values to direct values.
    u23a = beacon.get("u23a")

    sc = ct(0.01, taac_pos, taac_vel, taac_acc)
    pos = sc.get_data()["taac_undu_position"][0]
    vel = sc.get_data()["taac_undu_velocity"][0]
    acc = sc.get_data()["taac_undu_acceleration"][0]

    assert u23a.position == 1.4078913

    # formating is applyed before averaging :(
    pytest.approx(pos) == 1.408

    assert u23a.velocity == vel
    assert u23a.acceleration == acc

    # Test missing uri
    with pytest.raises(RuntimeError) as exc_info:
        _ = beacon.get("no_uri_counter")
    assert isinstance(exc_info.value.initial_cause, KeyError)

    device.setDisabled(True)

    sc = ct(0.01, taac_vel, taac_pos, taac_acc)
    pos = sc.get_data()["taac_undu_position"][0]
    assert numpy.isnan(pos)
    assert taac_pos.allow_failure is False

    taac_pos.allow_failure = True
    with pytest.raises(tango.DevFailed):
        sc = ct(0.01, taac_vel, taac_pos, taac_acc)

    taac_nan = beacon.get("taac_none_attr")
    sc = ct(0.01, taac_nan)
    counter_value = sc.get_data()["taac_none_attr"][0]
    assert numpy.isnan(counter_value)


def test_info_counters(beacon, dummy_tango_server):
    """
    execute .__info__() method of 4 types of counters.
    """
    mot_robz = beacon.get("robz")

    # SamplingCounter
    diode1 = beacon.get("diode")

    # IntegratingCounter
    diode2 = beacon.get("integ_diode")

    # SoftCounter
    soft_cnt = SoftCounter(mot_robz, "position")

    # tango_attr_as_counter
    counter = beacon.get("taac_dummy_position")

    assert diode1.__info__().startswith(
        "SimulationDiodeSamplingCounter:\n"
        " name  = diode\n"
        " dtype = float64\n"
        " shape = 0D\n"
        " unit  = None\n"
        " mode  = MEAN (1)\n"
    )
    assert diode2.__info__().startswith(
        "SimulationDiodeIntegratingCounter:\n"
        " name  = integ_diode\n"
        " dtype = float64\n"
        " shape = 0D\n"
        " unit  = None\n"
    )
    assert soft_cnt.__info__().startswith(
        "SoftCounter:\n"
        " name  = position\n"
        " dtype = float64\n"
        " shape = 0D\n"
        " unit  = None\n"
        " mode  = MEAN (1)\n"
    )
    assert counter.__info__().startswith(
        "tango_attr_as_counter:\n"
        " name            = taac_dummy_position\n"
        " device server   = id00/tango/dummy\n"
        " Tango attribute = position\n"
        " Tango format    = %3.2f\n"
        " Tango unit      = mm\n"
        " value           = 1.41\n"
    )


def test_multiple_samp_cnt_one_ctrl(default_session):
    class MySampCtrl1(SamplingCounterController):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.counter1 = 0
            self.counter2 = 0
            self.counter3 = 0
            self.counter4 = 0
            self.counter5 = 0
            self.max_sampling_frequency = None

        def read(self, counter):
            val = getattr(self, counter.name)
            setattr(self, counter.name, val + 1)
            return val

    ctrl1 = MySampCtrl1("ctrl1")
    counter1 = SamplingCounter("counter1", ctrl1)
    counter2 = SamplingCounter("counter2", ctrl1)
    counter3 = SamplingCounter("counter3", ctrl1)
    counter4 = SamplingCounter("counter4", ctrl1)
    counter5 = SamplingCounter("counter5", ctrl1)
    counter2.mode = SamplingMode.SAMPLES
    counter3.mode = SamplingMode.SINGLE
    counter4.mode = SamplingMode.LAST
    counter5.mode = SamplingMode.SAMPLES
    s = loopscan(3, 0.1, counter1, counter2, counter3, counter4, counter5, save=False)

    dat = s.get_data()
    assert "ctrl1:counter1" in dat
    assert "ctrl1:counter2" in dat
    assert "ctrl1:counter3" in dat
    assert "ctrl1:counter4" in dat
    assert "ctrl1:counter5" in dat
    assert "ctrl1:counter5_samples" in dat
    assert all(dat["ctrl1:counter1"] == dat["ctrl1:counter5"])

    loopscan(3, 0.1, counter1, counter3, counter4, save=False)

    dat2 = s.get_data()
    assert all(dat2["ctrl1:counter3"] < dat2["ctrl1:counter1"])
    assert all(dat2["ctrl1:counter1"] < dat2["ctrl1:counter4"])


def test_sampling_counter_frequency(default_session):
    diode = default_session.config.get("diode")
    diodeCC = diode._counter_controller

    # Test that MAX frequency is not exceeded.
    # call_count can occasionaly be lower, but at least called once.
    # cf issue #2663
    for freq in [1, 20]:
        diodeCC.max_sampling_frequency = freq
        with mock.patch.object(
            diodeCC, "read_all", wraps=diodeCC.read_all
        ) as mocked_readall:
            ct(1, diode)
            assert mocked_readall.call_count <= freq
            assert mocked_readall.call_count >= 1

    # Test forbiden frequency values.
    for val in [0, "1.5"]:
        with pytest.raises(ValueError):
            diodeCC.max_sampling_frequency = val

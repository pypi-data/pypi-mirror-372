# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Axis related classes (:class:`~bliss.common.axis.Axis`, \
:class:`~bliss.common.axis.AxisState`, :class:`~bliss.common.axis.Motion`
and :class:`~bliss.common.axis.GroupMove`)
"""

from __future__ import annotations

import gevent.timeout

from bliss import global_map
from bliss.common.deprecation import deprecated_warning
from bliss.common.hook import execute_pre_move_hooks
from bliss.common.protocols import HasMetadataForDataset, Scannable
from bliss.common.cleanup import capture_exceptions
from bliss.common.motor_config import MotorConfig
from bliss.common.motor_settings import AxisSettings
from bliss.common import event
from bliss.common.utils import with_custom_members, safe_get
from bliss.config.channels import Channel
from bliss.common.logtools import log_debug, log_warning, log_error
from bliss.common.utils import rounder
from bliss.common.utils import autocomplete_property
from bliss.comm.exceptions import CommunicationError
from bliss.common.closed_loop import ClosedLoop
from bliss.shell.formatters import tabulate

from prompt_toolkit.formatted_text import FormattedText

import enum
import gevent
import gevent.event
import gevent.lock
import re
import math
import functools
import collections
import itertools
import numbers
import numpy
import warnings
import time
import logging

from contextlib import contextmanager

warnings.simplefilter("once", DeprecationWarning)

_motion_logger = logging.getLogger("bliss.motion")
_motion_logger.setLevel(logging.WARNING)
_motion_tree_logger = logging.getLogger("bliss.motion_tree")
_motion_tree_logger.setLevel(logging.WARNING)


@contextmanager
def motion_bench(title: str, msg: str = ""):
    now = time.perf_counter()
    _motion_logger.info(f"ENTER: {title} {msg}")
    try:
        yield
    finally:
        elapsed = int((time.perf_counter() - now) * 1000)
        _motion_logger.info(f"EXIT : {title:30s} {elapsed:6d} ms")


#: Default polling time
DEFAULT_POLLING_TIME = 0.02


class AxisOnLimitError(RuntimeError):
    pass


class AxisOffError(RuntimeError):
    pass


class AxisFaultError(RuntimeError):
    pass


def float_or_inf(value, inf_sign=1):
    if value is None:
        value = float("inf")
        sign = math.copysign(1, inf_sign)
    else:
        sign = 1
    value = float(value)  # accepts float or numpy array of 1 element
    return sign * value


def _prepare_one_controller_motions(controller, motions):
    try:
        return controller.prepare_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.prepare_move(motion)


def _start_one_controller_motions(controller, motions):
    try:
        return controller.start_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.start_one(motion)


def _stop_one_controller_motions(controller, motions):
    try:
        return controller.stop_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.stop(motion.axis)


def _emit_move_done(obj, value=True, from_channel=False):
    try:
        if not from_channel:
            # this is used by calculation motors controllers,
            # to distinguish between 'move_done' received via
            # channel update, or when an actual move with the
            # local move loop is done
            event.send_safe(obj, "internal_move_done", value)
    finally:
        # this is the event, any subscriber can register, to
        # know when a move is done
        event.send_safe(obj, "move_done", value)


_MOTION_TASK_INTERRUPTION_TIMEOUT = 2
_MOTION_MAX_KILL = 4
_MOTION_MAX_STOP_ATTEMPT = 4
_MOTION_STOP_ATTEMPT_SLEEP_TIME = 0.02


class GroupMove:
    def __init__(self, parent=None):
        self.parent = parent
        self._motions_dict = {}

        self._move_task = None
        self._moni_tasks = []

        self._interrupted_move = False
        self._initialization_has_failed = False
        self._kill_nbr = 0
        self._kill_max = _MOTION_MAX_KILL
        self._stop_attempt_max = _MOTION_MAX_STOP_ATTEMPT
        self._stop_attempt_sleep_time = _MOTION_STOP_ATTEMPT_SLEEP_TIME
        self._task_interruption_timeout = _MOTION_TASK_INTERRUPTION_TIMEOUT

        self._prepare_motion_func = None
        self._start_motion_func = None
        self._stop_motion_func = None
        self._move_func = None

        self._initialization_event = gevent.event.Event()
        self._move_prepared_event = gevent.event.Event()
        self._move_started_event = gevent.event.Event()
        self._backlash_started_event = gevent.event.Event()
        self._end_of_move_event = gevent.event.Event()
        self._end_of_move_event.set()

    @property
    def task_interruption_timeout(self):
        return self._task_interruption_timeout

    @property
    def motions_dict(self):
        return self._motions_dict

    @motions_dict.setter
    def motions_dict(self, value):
        self._motions_dict = value

    @property
    def motions_iter(self):
        return itertools.chain.from_iterable(self._motions_dict.values())

    @property
    def all_axes(self):
        return (m.axis for m in self.motions_iter)

    @property
    def is_moving(self):
        return any(motion.axis.is_moving for motion in self.motions_iter)

    def _fill_motions_dict(
        self,
        remaining_axes,
        found_axes,
        not_moving_axes,
        axes_motions,
        axis_pos_dict,
        relative,
        polling_time,
        level=0,
    ):

        _motion_tree_logger.info(
            f"=== ENTER level {level} with inputs: {[x.name for x in axis_pos_dict]} ==="
        )

        for axis, target_pos in axis_pos_dict.items():

            if axis in not_moving_axes:
                _motion_tree_logger.info(f" axis {axis.name} is already discarded")
                continue

            motion = axis.get_motion(
                target_pos, relative=relative, polling_time=polling_time
            )
            if motion is None:  # motion can be None if axis is not supposed to move
                not_moving_axes.add(axis)
                _motion_tree_logger.info(f" axis {axis.name} is already in place")
                continue

            elif axes_motions.get(axis):  # a motion for that axis already exist
                cur_motion = axes_motions.get(axis)
                _motion_tree_logger.info(f" motion for axis {axis.name} already exist")
                if not motion.is_equal(cur_motion):
                    msg = f"Found different motions for same axis {motion.axis.name}:\n"
                    msg += f" existing motion: user_target_pos={cur_motion.user_target_pos} delta={cur_motion.delta} type={cur_motion.type} target_name={cur_motion.target_name}\n"
                    msg += f" new motion:      user_target_pos={motion.user_target_pos} delta={motion.delta} type={motion.type} target_name={motion.target_name}\n"
                    raise RuntimeError(msg)

            else:
                axes_motions[axis] = motion
                _motion_tree_logger.info(f" found motion for axis {axis.name}")

            if isinstance(axis, CalcAxis):
                _motion_tree_logger.info(f" axis {axis.name} is CalcAxis")
                step1_ok = True
                param_motions = []
                moving_axes = found_axes - not_moving_axes
                for param in axis.controller.params:
                    if (
                        param in moving_axes
                    ):  # this controller has a parametric axis involved in the group motion
                        _motion_tree_logger.info(
                            f" axis {axis.name} has a parametric axis {param.name} with motion"
                        )
                        if not axes_motions.get(
                            param
                        ):  # if param motion is not discovered yet, post pone.
                            step1_ok = False
                            _motion_tree_logger.info(
                                f" adding axis {axis.name} to pending list because {param.name} motion is not known yet"
                            )
                            remaining_axes[axis] = motion.user_target_pos
                            break
                        else:
                            param_motions.append(axes_motions.get(param))

                if step1_ok:
                    # now, we are sure that we have all the motions of the param axes that are moved elsewhere
                    # so we can compute the motion of the reals
                    step2_ok = True
                    pseudo_motions = []
                    for pseudo in axis.controller.pseudos:
                        if pseudo in moving_axes:
                            _motion_tree_logger.info(
                                f" found involved pseudo {pseudo.name}"
                            )
                            if not axes_motions.get(pseudo):
                                step2_ok = False
                                _motion_tree_logger.info(
                                    f" adding axis {axis.name} to pending list because {pseudo.name} motion is not known yet"
                                )
                                break
                            else:
                                pseudo_motions.append(axes_motions.get(pseudo))

                    if step2_ok:
                        # now we are sure that we have all the motions of the pseudo of that controller involved in the motion
                        for pseudo in axis.controller.pseudos:
                            if remaining_axes.pop(pseudo, None):
                                _motion_tree_logger.info(
                                    f" axis {pseudo.name} has been cleared from pending list"
                                )
                        motions = pseudo_motions + param_motions
                        _motion_tree_logger.info(
                            f" computing motions of {[x.axis.name for x in motions]} dependencies"
                        )
                        real_move_dict = axis.controller._get_real_axes_move_dict(
                            motions
                        )
                        self._fill_motions_dict(
                            remaining_axes,
                            found_axes,
                            not_moving_axes,
                            axes_motions,
                            real_move_dict,
                            relative=False,
                            polling_time=polling_time,
                            level=level + 1,
                        )

                        _motion_tree_logger.info(f"=== BACKTO level {level} ===")

                        # discard all pseudo axes of this Calc if all its dependencies are not moving
                        dependencies = set(real_move_dict.keys())
                        if not (dependencies - not_moving_axes):
                            psnames = []
                            for pseudo in axis.controller.pseudos:
                                not_moving_axes.add(pseudo)
                                axes_motions.pop(pseudo, None)
                                psnames.append(pseudo.name)
                            _motion_tree_logger.info(
                                f" discarding {psnames} because {[x.name for x in dependencies]} already in place"
                            )

        _motion_tree_logger.info(f"=== EXIT level {level} ===")
        _motion_tree_logger.info(f" found     : {[x.name for x in axes_motions]}")
        _motion_tree_logger.info(f" pending   : {[x.name for x in remaining_axes]}")
        _motion_tree_logger.info(f" discarded : {[x.name for x in not_moving_axes]}")

    def _find_sub_axes(self, axis_pos_dict, found_axes):
        """
        axis_pos_dict: dict of {axes: target_pos} passed to the motion cmd (absolute positions only!)
        found_axes: list of all axes involved in the motion (including all dependencies)
        """
        # find all axes dependencies (keeps discovery order)
        axes_list = axis_pos_dict.keys()
        found_axes.extend(axes_list)

        # do not rely on CalcController.reals (see issue 4306)
        motions_dict = {}
        for axis in axes_list:
            if isinstance(axis, CalcAxis):
                motions_dict.setdefault(axis.controller, []).append(
                    Motion(axis, axis_pos_dict[axis], None)
                )

        for ctrl, motions in motions_dict.items():
            dependencies_pos_dict = ctrl._get_real_axes_move_dict(motions)
            self._find_sub_axes(dependencies_pos_dict, found_axes)

    def _get_motions_per_controller(self, axes_motions):
        motions_dict = {}
        for axis, motion in axes_motions.items():
            motions_dict.setdefault(axis.controller, []).append(motion)
        return motions_dict

    def _find_motion_to_delete(self, motions_dict, excluded_axes):
        from bliss.controllers.motor import CalcController

        # if all motions only concern CalcControllers, cancel the entire motion (see issue 4198)
        if all(
            isinstance(controller, CalcController) for controller in motions_dict.keys()
        ):
            motions_dict.clear()
            _motion_logger.info("All physical axes already in place, motion cancelled")
            return

        for controller, motions in list(motions_dict.items()):
            if isinstance(controller, CalcController):
                if not set(controller.reals) - excluded_axes:
                    excluded_axes |= {motion.axis for motion in motions}
                    _motion_logger.info(
                        f"All Reals of {controller.name} already in place, discarding motions of {[m.axis.name for m in motions]}"
                    )
                    del motions_dict[controller]
                    return True

    def _resolve_motions_tree(self, axis_pos_dict, relative, polling_time):
        """
        'axis_pos_dict' is the dict {axis: target_position} passed to the move cmd.

        This function discovers all axes involved by the move cmd,
        from top level CalcAxis down to physical motors.

        It obtains the motion object for each axis.

        Axes already in place are filtered but it ensures that
        the position of linked CalcAxis is updated.

        Raise an error if different motions are found for same axis.

        Ensures that moving parametric axes are properly handled.

        Returns a dict of motions ordered by controllers
        """

        found_axes = []
        self._find_sub_axes(
            {
                axis: pos if not relative else pos + axis._set_position
                for axis, pos in axis_pos_dict.items()
            },
            found_axes,
        )

        found_axes = list(dict.fromkeys(found_axes))

        # === DEBUG ==========================
        _motion_tree_logger.info(
            f"Axes involved in motion: {[x.name for x in found_axes]}"
        )
        # ====================================

        not_moving_axes = set()
        remaining_axes = {}
        axes_motions = {}
        found_axes = set(found_axes)

        self._fill_motions_dict(
            remaining_axes,
            found_axes,
            not_moving_axes,
            axes_motions,
            axis_pos_dict,
            relative,
            polling_time,
        )

        # deal with axes added to pending list
        while remaining_axes:
            axis_pos_dict = remaining_axes.copy()
            self._fill_motions_dict(
                remaining_axes,
                found_axes,
                not_moving_axes,
                axes_motions,
                axis_pos_dict,
                relative=False,
                polling_time=polling_time,
                level=0,
            )

            if set(axis_pos_dict) == set(remaining_axes):
                raise RuntimeError(
                    f"Unable to resolve motion tree for axes {[x.name for x in remaining_axes]}"
                )

        motions_dict = self._get_motions_per_controller(axes_motions)
        while self._find_motion_to_delete(motions_dict, not_moving_axes):
            pass

        _motion_logger.info(
            f"Axes already in place: {[x.name for x in not_moving_axes]}"
        )
        for axis in not_moving_axes:
            # Different combinations of {pseudo pos, calc params}
            # can lead to the same position of the reals. So reals won't move
            # and won't update pseudos positions via Louie callbacks.
            # So send "internal_position" signal on reals to force linked pseudos to update their positions.
            if not isinstance(axis, CalcAxis):
                event.send(axis, "internal_position", axis.position)

        for motions in motions_dict.values():
            for motion in motions:
                _motion_logger.info(motion.user_msg)

        return motions_dict

    def move(
        self,
        axis_pos_dict,
        prepare_motion,
        start_motion,
        stop_motion,
        move_func=None,
        relative=False,
        wait=True,
        polling_time=None,
    ):

        if self._move_task:
            raise RuntimeError(
                "Cannot start a new motion while current motion is still running"
            )

        with motion_bench("resolve_motions_tree"):
            motions_dict = self._resolve_motions_tree(
                axis_pos_dict, relative, polling_time
            )

        if motions_dict:
            self.start(
                motions_dict,
                prepare_motion,
                start_motion,
                stop_motion,
                move_func=move_func,
                wait=wait,
            )

    def start(
        self,
        motions_dict,
        prepare_motion,
        start_motion,
        stop_motion,
        move_func=None,
        wait=True,
    ):

        self._init_vars_on_start(
            motions_dict, prepare_motion, start_motion, stop_motion, move_func
        )

        with motion_bench(f"start motion {'(wait=True)' if wait else ''}"):

            # assign group_move
            for motion in self.motions_iter:
                motion.axis._group_move = self

            # pre move hooks and check ready
            # (automatically perform post move hook if error/not-ready)
            self._do_pre_move_hooks()

            try:
                self._move_task = gevent.spawn(self._perform_move)
                self._move_task.name = "motion_task"

                # ensure motion is initialized before returning
                with motion_bench("wait motion initialization"):
                    self._initialization_event.wait()

                if wait:
                    self.wait()

            except BaseException as e:
                self.stop()
                raise e

    def wait(self):
        if self._move_task is not None:
            with motion_bench("wait motion task"):
                self._move_task.get()

    def stop(self, wait=True):
        if self._move_task:
            _motion_logger.info(f"ABORT: stop motion {'(wait=True)' if wait else ''}")
            if not self._stopping:
                _motion_logger.info("ABORT: killing move task")
                self._stopping = True
                self._move_task.kill(block=False)
            if wait:
                try:
                    self.wait()
                except (KeyboardInterrupt, gevent.GreenletExit):
                    self._kill_nbr += 1
                    if self._kill_nbr > self._kill_max:
                        _motion_logger.info(
                            "ABORT: exit stopping procedure after max KeyboardInterrupt"
                        )
                        raise

                    elif self._kill_nbr == self._kill_max:
                        log_warning(
                            self,
                            f"!!! NEXT CTRL-C WILL INTERRUPT THE STOPPPING PROCEDURE AND CAN LEAVE AXES IN BAD STATE OR STILL RUNNING !!! (stopping attempt: {self._kill_nbr}/{self._kill_max})",
                        )
                        self.stop()

                    else:
                        log_warning(
                            self,
                            f"Motion is stopping, please wait (stopping attempt: {self._kill_nbr}/{self._kill_max})",
                        )
                        self.stop()

    def _request_motion_stop(self):
        """Send controllers stop cmds and retry in case of cmd failure.
        After too many unsuccessful attempts an error is raised.
        """

        with motion_bench("request_motion_stop"):

            retries = 0
            failing_stop_tasks = self._send_stop_cmds(self.motions_dict)

            # retry controller's stop cmds which have failed (up to _stop_attempt_max)
            while failing_stop_tasks:
                retries += 1
                if retries > self._stop_attempt_max:
                    msg_lines = [""]
                    for task, ctrl in failing_stop_tasks.items():
                        axes = [m.axis.name for m in self.motions_dict[ctrl]]
                        msg_lines.append(
                            f"axis {axes} stopping cmd failed with exception: {task.exception}"
                        )
                    msg_lines.append("")
                    raise RuntimeError("\n".join(msg_lines))

                gevent.sleep(self._stop_attempt_sleep_time)
                motions_dict = {
                    ctrl: self.motions_dict[ctrl]
                    for ctrl in failing_stop_tasks.values()
                }
                failing_stop_tasks = self._send_stop_cmds(motions_dict)

    def _init_vars_on_start(
        self, motions_dict, prepare_motion, start_motion, stop_motion, move_func
    ):
        self.motions_dict = motions_dict
        self._prepare_motion_func = prepare_motion
        self._start_motion_func = start_motion
        self._stop_motion_func = stop_motion
        self._move_func = move_func

        self._interrupted_move = False
        self._stopping = False
        self._kill_nbr = 0

        self._initialization_has_failed = False
        self._initialization_event.clear()
        self._move_prepared_event.clear()
        self._move_started_event.clear()
        self._backlash_started_event.clear()

    def _initialize_motion(self):
        with motion_bench("initialize_motion"):
            try:
                # set target position and moving state
                restore_axes = {}
                for motion in self.motions_iter:
                    target_pos = motion.user_target_pos
                    if target_pos is not None:
                        restore_axes[motion.axis] = (
                            motion.axis._set_position,
                            motion.axis.state,
                        )
                        motion.axis._set_position = target_pos

                    msg = motion.user_msg
                    if msg:
                        event.send_safe(motion.axis, "msg", msg)
                        if motion.type != "move":
                            print(msg)

                    motion.axis._set_moving_state()

                if self.parent:
                    _emit_move_done(self.parent, value=False)

            except BaseException:
                self._initialization_has_failed = True
                with motion_bench("restore axes"):
                    for ax, (setpos, state) in restore_axes.items():
                        # revert actions of _set_moving_state
                        ax.settings.set("state", state)
                        ax._set_move_done()
                        ax._set_position = setpos
                raise

            finally:
                self._initialization_event.set()

    def _perform_move(self):

        self._end_of_move_event.clear()

        try:
            self._initialize_motion()

            with motion_bench("perform main motion"):
                self._main_motion_task()

            self._backlash_motion_task()

        except BaseException as e:
            _motion_logger.info(f"ABORT: exception during motion: {e}")
            self._interrupted_move = True

            if self._move_started_event.is_set():

                with capture_exceptions(raise_index=0) as capture:
                    with capture():
                        self._request_motion_stop()
                    if capture.failed:
                        log_warning(
                            self,
                            "ABORT: stop cmd failed, now waiting initial motion to finish",
                        )

                    with motion_bench("joining current monitoring tasks"):
                        if all(
                            [task.dead for task in self._moni_tasks]
                        ):  # all dead or _moni_tasks empty
                            # in case of failure before monitor_motion has been called (but motions started):
                            # case 1: during     main-motion => self._moni_tasks = []
                            # case 2: during backlash-motion => self._moni_tasks = [dead_task, ...]
                            self._monitor_motion(
                                raise_error=False
                            )  # do not raise to join all tasks
                        else:
                            gevent.joinall(self._moni_tasks)

            raise e

        finally:

            try:
                if not self._initialization_has_failed:
                    self._finalize_motion()

                self._do_post_move_hooks()

            finally:
                self._stopping = False
                self._end_of_move_event.set()

    def _main_motion_task(self):
        self._send_prepare_cmds()
        self._send_start_cmds()
        self._monitor_motion()

    def _backlash_motion_task(self):
        backlash_motions = collections.defaultdict(list)
        for controller, motions in self.motions_dict.items():
            for motion in motions:
                if motion.backlash:
                    backlash_motions[controller].append(motion.backlash_motion)

        if backlash_motions:
            bgm = GroupMove()
            bgm._init_vars_on_start(
                backlash_motions,
                _prepare_one_controller_motions,
                _start_one_controller_motions,
                _stop_one_controller_motions,
                None,
            )
            self._backlash_started_event.set()
            with motion_bench("perform backlash motion"):
                bgm._main_motion_task()

    def _do_pre_move_hooks(self):
        with motion_bench("pre move hooks and check ready"):
            with execute_pre_move_hooks(list(self.motions_iter)):
                for motion in self.motions_iter:
                    motion.axis._check_ready()

    def _do_post_move_hooks(self):
        with motion_bench("post_move_hooks"):
            hooks = collections.defaultdict(list)
            for motion in self.motions_iter:
                for hook in motion.axis.motion_hooks:
                    hooks[hook].append(motion)

            with capture_exceptions(raise_index=0) as capture:
                for hook, motions in reversed(list(hooks.items())):
                    with capture():
                        hook.post_move(motions)

    def _send_prepare_cmds(self):
        """Send in parallel controllers prepare cmds.
        If one fails, wait for others to finish before 'self.task_interruption_timeout'
        else kill associated tasks to avoid hanging on blocking prepare cmds.
        """

        with motion_bench("send_prepare_cmds"):
            tasks = []
            if self._prepare_motion_func is not None:
                for controller, motions in self.motions_dict.items():
                    task = gevent.spawn(self._prepare_motion_func, controller, motions)
                    task.name = f"motion_prepare_{controller.name}"
                    tasks.append(task)

            try:
                gevent.joinall(tasks, raise_error=True)
            except BaseException:
                try:
                    with gevent.Timeout(self.task_interruption_timeout):
                        gevent.joinall(tasks)
                except gevent.Timeout:
                    _motion_logger.info(
                        "ABORT: unexpected timeout while joining prepare cmd tasks, now killing tasks"
                    )
                    gevent.killall(tasks)
                raise

            self._move_prepared_event.set()

    def _send_start_cmds(self):
        """Send in parallel controllers start cmds.
        If one fails, wait for others to finish before 'self.task_interruption_timeout'
        else kill associated tasks to avoid hanging on blocking start cmds.
        """

        with motion_bench("send_start_cmds"):
            tasks = []
            for controller, motions in self.motions_dict.items():
                task = gevent.spawn(self._start_motion_func, controller, motions)
                task.name = f"motion_start_{controller.name}"
                tasks.append(task)

            self._move_started_event.set()

            try:
                gevent.joinall(tasks, raise_error=True)
            except BaseException:
                try:
                    with gevent.Timeout(self.task_interruption_timeout):
                        gevent.joinall(tasks)
                except gevent.Timeout:
                    _motion_logger.info(
                        "ABORT: unexpected timeout while joining start cmd tasks, now killing tasks"
                    )
                    gevent.killall(tasks)
                raise

    def _send_stop_cmds(self, motions_dict):
        """Send in parallel controllers stop cmds and return the ones which have failed"""

        axes_to_stop = [
            m.axis.name for m in itertools.chain.from_iterable(motions_dict.values())
        ]
        with motion_bench("send_stop_cmds", f"{axes_to_stop}"):
            tasks = {}
            for controller, motions in motions_dict.items():
                task = gevent.spawn(self._stop_motion_func, controller, motions)
                task.name = f"motion_stop_{controller.name}"
                tasks[task] = controller

            failing_stop_tasks = {}
            for task in gevent.iwait(tasks):
                if task.exception is not None:
                    ctrl = tasks[task]
                    failing_stop_tasks[task] = ctrl

        return failing_stop_tasks

    def _monitor_motion(self, raise_error=True):
        with motion_bench("monitor_motion"):

            if self._move_func is None:
                move_func = "_handle_move"
            else:
                move_func = self._move_func

            self._moni_tasks = []
            for motion in self.motions_iter:
                if isinstance(motion.axis, CalcAxis):
                    # calc axes will get updated via real motors updates
                    continue

                task = gevent.spawn(getattr(motion.axis, move_func), motion)
                task.name = f"motion_monitor_{motion.axis.name}"
                self._moni_tasks.append(task)

            gevent.joinall(self._moni_tasks, raise_error=raise_error)

    def _parallel_set_move_done(self):
        with motion_bench("parallel_set_move_done"):
            tasks = []
            for ax in (ax for ax in self.all_axes if not isinstance(ax, CalcAxis)):
                task = gevent.spawn(ax._set_move_done)
                task.name = f"motion_set_move_done_{ax.name}"
                tasks.append(task)

            try:
                gevent.joinall(tasks, raise_error=True)
            except BaseException:
                gevent.joinall(tasks)
                raise

    def _jog_cleanup(self, motion):
        with motion_bench("perform jog cleanup"):
            motion.axis._jog_cleanup(motion.saved_velocity, motion.reset_position)

    def _finalize_motion(self):
        with motion_bench("finalize_motion"):

            with capture_exceptions(raise_index=0) as capture:

                reset_setpos = self._interrupted_move

                all_motions = list(self.motions_iter)
                if len(all_motions) == 1:
                    motion = all_motions[0]
                    if motion.type == "jog":
                        reset_setpos = False

                        with capture():
                            self._jog_cleanup(motion)

                    elif motion.type == "homing":
                        reset_setpos = True
                    elif motion.type == "limit_search":
                        reset_setpos = True

                if reset_setpos:
                    # even in case of interrupted motion, monitoring tasks have been joined
                    # so dial and state cache have been updated after hw_state reported not READY
                    # so axis.position is the correct/up-to-date value read after axis has been stopped
                    # (if motor controller stop-cmd returns once the motor has really stopped!!!)
                    with motion_bench("reset set_positions"):
                        for motion in self.motions_iter:

                            with capture():
                                motion.axis._set_position = motion.axis.position
                                event.send(motion.axis, "sync_hard")

                with capture():
                    self._parallel_set_move_done()

                with capture():
                    if self.parent:
                        _emit_move_done(self.parent)

                if self._interrupted_move:
                    for motion in self.motions_iter:

                        with capture():
                            _axis = motion.axis
                            _axis_pos = safe_get(_axis, "position", on_error="!ERR")
                            _axis_pos = _axis.axis_rounder(_axis_pos)
                            msg = f"Axis {_axis.name} stopped at position {_axis_pos}"
                            event.send_safe(
                                _axis,
                                "msg",
                                msg,
                            )
                            if motion.type != "move":
                                print(msg)

                # once move task is finished, check encoder if needed
                with motion_bench("do_encoder_reading"):
                    for axis in (m.axis for m in all_motions):

                        with capture():
                            if axis._check_encoder:
                                axis._do_encoder_reading()

                for _, err, _ in capture.exception_infos:
                    _motion_logger.info(f"ERROR: cleanup: {err}")


class Modulo:
    def __init__(self, mod=360):
        self.modulo = mod

    def __call__(self, axis):
        dial_pos = axis.dial
        axis._Axis__do_set_dial(dial_pos % self.modulo)


class Motion:
    """Motion information

    Represents a specific motion. The following members are present:

    * *axis* (:class:`Axis`): the axis to which this motion corresponds to
    * *target_pos* (:obj:`float`): final motion position
    * *delta* (:obj:`float`): motion displacement
    * *backlash* (:obj:`float`): motion backlash

    Note: target_pos and delta can be None, in case of specific motion
    types like homing or limit search
    """

    def __init__(
        self,
        axis,
        target_pos,
        delta,
        motion_type="move",
        target_name=None,
    ):
        self.__axis = axis
        self.__type = motion_type
        self.__target_name = target_name

        self._target_pos_raw = target_pos  # steps
        self._delta_raw = delta  # steps
        self._backlash = 0  # steps
        self._encoder_delta = 0  # steps
        self._polling_time = None  # seconds

        # special jog motion
        self._jog_velocity = None
        self._direction = None

        try:
            self._dial_target_pos = self._target_pos_raw / axis.steps_per_unit
        except TypeError:
            self._dial_target_pos = None

        self._user_target_pos = self.axis.dial2user(
            self._dial_target_pos
        )  # dial2user handles None

    @property
    def axis(self):
        """Return the Axis object associated to this motion"""
        return self.__axis

    @property
    def type(self):
        """Type of motion (move, jog, homing, limit_search, ...)"""
        return self.__type

    @property
    def target_name(self):
        """Descriptive text about the target position for some motion types (None, home, lim+, lim-, ...)"""
        return self.__target_name

    @property
    def backlash(self):
        """Backlash compensation (in steps)"""
        return self._backlash

    @backlash.setter
    def backlash(self, value):
        self._backlash = value

    @property
    def encoder_delta(self):
        """Controller vs Encoder compensation (in steps)"""
        return self._encoder_delta

    @encoder_delta.setter
    def encoder_delta(self, value):
        self._encoder_delta = value

    @property
    def jog_velocity(self):
        """Get jog velocity in steps and unsigned (used by hardware)"""
        return self._jog_velocity

    @jog_velocity.setter
    def jog_velocity(self, value):
        """Set jog velocity in steps and unsigned (used by hardware)"""
        if value < 0:
            raise ValueError(
                f"Motion jog velocity cannot be negative but receive {value}"
            )
        self._jog_velocity = value

    @property
    def direction(self):
        """Get jog direction (in dial/ctrl referential, used by hardware)"""
        return self._direction

    @direction.setter
    def direction(self, value):
        """Set jog direction (in dial/ctrl referential, used by hardware)"""
        if value not in [-1, 1]:
            raise ValueError(f"Motion direction must be in [-1, 1] but receive {value}")
        self._direction = value

    @property
    def polling_time(self):
        """Polling time used during motion monitoring to refresh dial and state values"""
        return (
            self._polling_time
            if self._polling_time is not None
            else self.axis._polling_time
        )

    @polling_time.setter
    def polling_time(self, value):
        self._polling_time = value

    @property
    def dial_target_pos(self):
        """The target position requested by the user expressed as 'dial' value (in motor units).
        Does not include backlash and encoder corrections.
        """
        return self._dial_target_pos

    @property
    def user_target_pos(self):
        """The target position requested by the user expressed as 'user' value (in motor units).
        Does not include backlash and encoder corrections.
        """
        return self._user_target_pos

    @property
    def target_pos_raw(self):
        """The motion target position (in steps) without backlash and encoder corrections.
        It corresponds to the position requested by the user (from cmd) converted into steps.
        """
        return self._target_pos_raw

    @property
    def target_pos(self):
        """The motion target position (in steps) that will be sent to the hardware controller.
        It takes into account the backlash and encoder corrections.
        """
        return self._target_pos_raw - self._backlash + self._encoder_delta

    @property
    def delta_raw(self):
        """Difference between target and current pos: (dial_target - dial, in steps)
        without backlash and encoder corrections.
        """
        return self._delta_raw

    @property
    def delta(self):
        """Difference between target and current pos: (dial_target - dial, in steps).
        Used by controllers working in RELATIVE mode.
        It takes into account the backlash and encoder corrections.
        """
        return self._delta_raw - self._backlash + self._encoder_delta

    @property
    def backlash_motion(self):
        """Return the Motion object corresponding to the final move, if there is backlash"""
        return Motion(self.axis, self.target_pos_raw, delta=self.backlash)

    @property
    def user_msg(self):
        start_ = self.__axis.axis_rounder(self.axis.position)
        if self.type == "jog":
            velocity = self.jog_velocity / self.axis.steps_per_unit  # velocity in user
            direction = self.direction * self.axis.sign  # direction in user
            msg = (
                f"Moving {self.axis.name} from {start_} at velocity {velocity} in {'positive' if direction > 0 else 'negative'} direction\n"
                f"Stop motion with: {self.axis.name}.stop()"
            )
            return msg

        else:
            if self.target_name:
                # can be a string in case of special move like limit search, homing...
                end_ = self.target_name
            else:
                if self.user_target_pos is None:
                    return
                end_ = self.__axis.axis_rounder(self.user_target_pos)
            return f"Moving {self.axis.name} from {start_} to {end_}"

    def is_equal(self, other_motion):
        """Compare this motion to another motion and check if they are identical"""
        # Don't overload __eq__ to keep this object hashable!

        if self.axis != other_motion.axis:
            return False

        if self.type != other_motion.type:
            return False

        if self.target_name != other_motion.target_name:
            return False

        if self.delta != other_motion.delta:
            if not numpy.isnan(self.delta) or not numpy.isnan(other_motion.delta):
                return False

        if self.target_pos_raw != other_motion.target_pos_raw:
            if not numpy.isnan(self.target_pos_raw) or not numpy.isnan(
                other_motion.target_pos_raw
            ):
                return False

        return True


class Trajectory:
    """Trajectory information

    Represents a specific trajectory motion.

    """

    def __init__(self, axis, pvt):
        """
        Args:
            axis -- axis to which this motion corresponds to
            pvt  -- numpy array with three fields ('position','velocity','time')
        """
        self.__axis = axis
        self.__pvt = pvt
        self._events_positions = numpy.empty(
            0, dtype=[("position", "f8"), ("velocity", "f8"), ("time", "f8")]
        )

    @property
    def axis(self):
        return self.__axis

    @property
    def pvt(self):
        return self.__pvt

    @property
    def events_positions(self):
        return self._events_positions

    @events_positions.setter
    def events_positions(self, events):
        self._events_positions = events

    def has_events(self):
        return self._events_positions.size

    def __len__(self):
        return len(self.pvt)

    def convert_to_dial(self):
        """
        Return a new trajectory with pvt position, velocity converted to dial units and steps per unit
        """
        user_pos = self.__pvt["position"]
        user_velocity = self.__pvt["velocity"]
        pvt = numpy.copy(self.__pvt)
        pvt["position"] = self._axis_user2dial(user_pos) * self.axis.steps_per_unit
        pvt["velocity"] = user_velocity * self.axis.steps_per_unit
        new_obj = self.__class__(self.axis, pvt)
        pattern_evts = numpy.copy(self._events_positions)
        pattern_evts["position"] *= self.axis.steps_per_unit
        pattern_evts["velocity"] *= self.axis.steps_per_unit
        new_obj._events_positions = pattern_evts
        return new_obj

    def _axis_user2dial(self, user_pos):
        return self.axis.user2dial(user_pos)


class CyclicTrajectory(Trajectory):
    def __init__(self, axis, pvt, nb_cycles=1, origin=0):
        """
        Args:
            axis -- axis to which this motion corresponds to
            pvt  -- numpy array with three fields ('position','velocity','time')
                    point coordinates are in relative space
        """
        super(CyclicTrajectory, self).__init__(axis, pvt)
        self.nb_cycles = nb_cycles
        self.origin = origin

    @property
    def pvt_pattern(self):
        return super(CyclicTrajectory, self).pvt

    @property
    def events_pattern_positions(self):
        return super(CyclicTrajectory, self).events_positions

    @events_pattern_positions.setter
    def events_pattern_positions(self, values):
        self._events_positions = values

    @property
    def is_closed(self):
        """True if the trajectory is closed (first point == last point)"""
        pvt = self.pvt_pattern
        return (
            pvt["time"][0] == 0
            and pvt["position"][0] == pvt["position"][len(self.pvt_pattern) - 1]
        )

    @property
    def pvt(self):
        """Return the full PVT table. Positions are absolute"""
        pvt_pattern = self.pvt_pattern
        if self.is_closed:
            # take first point out because it is equal to the last
            raw_pvt = pvt_pattern[1:]
            cycle_size = raw_pvt.shape[0]
            size = self.nb_cycles * cycle_size + 1
            offset = 1
        else:
            raw_pvt = pvt_pattern
            cycle_size = raw_pvt.shape[0]
            size = self.nb_cycles * cycle_size
            offset = 0
        pvt = numpy.empty(size, dtype=raw_pvt.dtype)
        last_time, last_position = 0, self.origin
        for cycle in range(self.nb_cycles):
            start = cycle_size * cycle + offset
            end = start + cycle_size
            pvt[start:end] = raw_pvt
            pvt["time"][start:end] += last_time
            last_time = pvt["time"][end - 1]
            pvt["position"][start:end] += last_position
            last_position = pvt["position"][end - 1]

        if self.is_closed:
            pvt["time"][0] = pvt_pattern["time"][0]
            pvt["position"][0] = pvt_pattern["position"][0] + self.origin

        return pvt

    @property
    def events_positions(self):
        pattern_evts = self.events_pattern_positions
        time_offset = 0.0
        last_time = self.pvt_pattern["time"][-1]
        nb_pattern_evts = len(pattern_evts)
        all_events = numpy.empty(
            self.nb_cycles * len(pattern_evts), dtype=pattern_evts.dtype
        )
        for i in range(self.nb_cycles):
            sub_evts = all_events[
                i * nb_pattern_evts : i * nb_pattern_evts + nb_pattern_evts
            ]
            sub_evts[:] = pattern_evts
            sub_evts["time"] += time_offset
            time_offset += last_time
        return all_events

    def _axis_user2dial(self, user_pos):
        # here the trajectory is relative to the origin so the **pvt_pattern**
        # should not contains the axis offset as it's already in **origin**
        return user_pos * self.axis.sign

    def convert_to_dial(self):
        """
        Return a new trajectory with pvt position, velocity converted to dial units and steps per unit
        """
        new_obj = super(CyclicTrajectory, self).convert_to_dial()
        new_obj.origin = self.axis.user2dial(self.origin) * self.axis.steps_per_unit
        new_obj.nb_cycles = self.nb_cycles
        return new_obj


def lazy_init(func):
    """Decorator to call `self._lazy_init()` before the use of a function."""

    @functools.wraps(func)
    def func_wrapper(self, *args, **kwargs):
        self._lazy_init()
        return func(self, *args, **kwargs)

    return func_wrapper


@with_custom_members
class Axis(Scannable, HasMetadataForDataset):
    """
    This class is typically used by motor controllers in bliss to export
    axis with harmonised interface for users and configuration.
    """

    class READ_POSITION_MODE(enum.Enum):
        CONTROLLER = 1
        ENCODER = 2

    def __init__(self, name, controller, config):
        self.__name = name
        self.__controller = controller
        self.__move_done = gevent.event.Event()
        self.__move_done_callback = gevent.event.Event()
        self.__move_done.set()
        self.__move_done_callback.set()
        self.__motion_hooks = []
        for hook in config.get("motion_hooks", []):
            hook._add_axis(self)
            self.__motion_hooks.append(hook)
        self.__encoder = config.get("encoder")
        if self.__encoder is not None:
            self.__encoder.axis = self
        self.__config = MotorConfig(config)
        self.__settings = AxisSettings(self)
        self._init_config_properties()
        self.__no_offset = False
        self._group_move = GroupMove()
        self._lock = gevent.lock.Semaphore()
        self.__positioner = True
        self._disabled: bool = False
        if config.get("closed_loop"):
            self._closed_loop = ClosedLoop(self)
        else:
            self._closed_loop = None

        self._display_digits = None

        try:
            config.parent
        except AttributeError:
            # some Axis don't have a controller, e.g. SoftAxis
            disabled_cache = list()
        else:
            disabled_cache = config.parent.get(
                "disabled_cache", []
            )  # get it from controller (parent)
        disabled_cache.extend(config.get("disabled_cache", []))  # get it for this axis
        for setting_name in disabled_cache:
            self.settings.disable_cache(setting_name)

        # self.config ?
        self._unit = self.config.get("unit", str, None)
        self._polling_time = config.get("polling_time", DEFAULT_POLLING_TIME)
        global_map.register(self, parents_list=["axes", controller])

        # create Beacon channels
        self.settings.init_channels()
        self._move_stop_channel = Channel(
            f"axis.{self.name}.move_stop",
            default_value=False,
            callback=self._external_stop,
            self_updates=False,
        )
        self._jog_velocity_channel = Channel(
            f"axis.{self.name}.change_jog_velocity",
            default_value=None,
            callback=self._set_jog_velocity,
            self_updates=False,
        )

    def _lazy_init(self):
        """Initialization triggered at any use of this axis.

        Raises an exception if the axis was flagged as `disabled`
        or if it was not possible to initialize the controller.
        """
        if self.disabled:
            raise RuntimeError(f"Axis {self.name} is disabled")
        try:
            self.controller._initialize_axis(self)
        except Exception as e:
            if isinstance(e, CommunicationError):
                # also disable the controller
                self.controller._disabled = True
            self._disabled = True
            raise
        else:
            if not self.controller.axis_initialized(self):
                # failed to initialize
                self._disabled = True

    def __close__(self):
        self.close()

    def close(self):
        self.controller.close()

    def axis_rounder(self, value):
        """
        Return a rounded value of <value> as a string.
        Use `display_digits` as number of digits after decimal point.
        Use `bliss.common.utils.rounder` function to perform the rounding.
        <value> : number
        """

        if not isinstance(value, numbers.Number):
            return value

        if math.isnan(value):
            return "nan"

        # Convert a number of digits to a model string usable by rounder() function.
        # ex: 2 -> 0.01 ; 8 -> 0.00000001
        try:
            display_model = float(
                f"{1/pow(10,self.display_digits):0.{self.display_digits}f}"
            )
        except ValueError as val_err:
            raise RuntimeError(
                f"axis {self.name}: error on display_digits:{self.display_digits} {type(self.display_digits)}"
            ) from val_err

        # print("display_model=", display_model)
        rounded_pos_str = rounder(display_model, value)
        return rounded_pos_str

    @property
    def _check_encoder(self):
        return self.config.get("check_encoder", bool, self.encoder) and self.encoder

    @property
    def _read_position_mode(self):
        if self.config.get("read_position", str, "controller") == "encoder":
            return self.READ_POSITION_MODE.ENCODER
        else:
            return self.READ_POSITION_MODE.CONTROLLER

    @property
    def _encoder_read_mode(self):
        return self._read_position_mode == self.READ_POSITION_MODE.ENCODER

    @property
    def no_offset(self):
        return self.__no_offset

    @no_offset.setter
    def no_offset(self, value):
        self.__no_offset = value

    @property
    def unit(self):
        """unit used for the Axis (mm, deg, um...)"""
        return self._unit

    @property
    def name(self):
        """name of the axis"""
        return self.__name

    @property
    def _positioner(self):
        """Axis positioner"""
        return self.__positioner

    @_positioner.setter
    def _positioner(self, new_p):
        self.__positioner = new_p

    @autocomplete_property
    def controller(self):
        """
        Motor controller of the axis
        Reference to :class:`~bliss.controllers.motor.Controller`
        """
        return self.__controller

    @property
    def config(self):
        """Reference to the :class:`~bliss.common.motor_config.MotorConfig`"""
        return self.__config

    @property
    def settings(self):
        """
        Reference to the
        :class:`~bliss.controllers.motor_settings.AxisSettings`
        """
        return self.__settings

    @property
    def is_moving(self):
        """
        Tells if the axis is moving (:obj:`bool`)
        """
        return not self.__move_done.is_set()

    def _init_config_properties(
        self, velocity=True, acceleration=True, limits=True, sign=True, backlash=True
    ):
        self.__steps_per_unit = self.config.get("steps_per_unit", float, 1)
        self.__tolerance = self.config.get("tolerance", float, 1e-4)
        if velocity:
            if "velocity" in self.settings.config_settings:
                self.__config_velocity = self.config.get("velocity", float)
            if "jog_velocity" in self.settings.config_settings:
                self.__config_jog_velocity = self.config.get(
                    "jog_velocity", float, self.__config_velocity
                )
            self.__config_velocity_low_limit = self.config.get(
                "velocity_low_limit", float, float("inf")
            )
            self.__config_velocity_high_limit = self.config.get(
                "velocity_high_limit", float, float("inf")
            )
        if acceleration:
            if "acceleration" in self.settings.config_settings:
                self.__config_acceleration = self.config.get("acceleration", float)
        if limits:
            self.__config_low_limit = self.config.get("low_limit", float, float("-inf"))
            self.__config_high_limit = self.config.get(
                "high_limit", float, float("+inf")
            )
        if backlash:
            self.__config_backlash = self.config.get("backlash", float, 0)

    @property
    def steps_per_unit(self):
        """Current steps per unit (:obj:`float`)"""
        return self.__steps_per_unit

    @property
    def config_backlash(self):
        """Current backlash in user units (:obj:`float`)"""
        return self.__config_backlash

    @property
    def backlash(self):
        """Current backlash in user units (:obj:`float`)"""
        backlash = self.settings.get("backlash")
        if backlash is None:
            return 0
        return backlash

    @backlash.setter
    def backlash(self, backlash):
        self.settings.set("backlash", backlash)

    @property
    @lazy_init
    def closed_loop(self):
        """
        Closed loop object associated to axis.
        """
        return self._closed_loop

    @property
    def tolerance(self):
        """Current Axis tolerance in dial units (:obj:`float`)"""
        return self.__tolerance

    @property
    def encoder(self):
        """
        Reference to :class:`~bliss.common.encoder.Encoder` or None if no
        encoder is defined
        """
        return self.__encoder

    @property
    def motion_hooks(self):
        """Registered motion hooks (:obj:`MotionHook`)"""
        return self.__motion_hooks

    @property
    def offset(self):
        """Current offset in user units (:obj:`float`)"""
        offset = self.settings.get("offset")
        if offset is None:
            return 0
        return offset

    @offset.setter
    def offset(self, new_offset):
        if self.no_offset:
            raise RuntimeError(
                f"{self.name}: cannot change offset, axis has 'no offset' flag"
            )
        self.__do_set_position(offset=new_offset)

    @property
    def sign(self):
        """Current motor sign (:obj:`int`) [-1, 1]"""
        sign = self.settings.get("sign")
        if sign is None:
            return 1
        return sign

    @sign.setter
    @lazy_init
    def sign(self, new_sign):
        new_sign = float(
            new_sign
        )  # works both with single float or numpy array of 1 element
        new_sign = math.copysign(1, new_sign)
        if new_sign != self.sign:
            if self.no_offset:
                raise RuntimeError(
                    f"{self.name}: cannot change sign, axis has 'no offset' flag"
                )
            self.settings.set("sign", new_sign)
            # update pos with new sign, offset stays the same
            # user pos is **not preserved** (like spec)
            self.position = self.dial2user(self.dial)

    def set_setting(self, *args):
        """Sets the given settings"""
        self.settings.set(*args)

    def get_setting(self, *args):
        """Return the values for the given settings"""
        return self.settings.get(*args)

    def has_tag(self, tag):
        """
        Tells if the axis has the given tag

        Args:
            tag (str): tag name

        Return:
            bool: True if the axis has the tag or False otherwise
        """
        for t, axis_list in self.__controller._tagged.items():
            if t != tag:
                continue
            if self.name in [axis.name for axis in axis_list]:
                return True
        return False

    @property
    def disabled(self):
        return self._disabled

    def enable(self):
        self._disabled = False
        self.hw_state  # force update

    @lazy_init
    def on(self):
        """Turns the axis on"""
        if self.is_moving:
            return

        self.__controller.set_on(self)
        state = self.__controller.state(self)
        self.settings.set("state", state)

    @lazy_init
    def off(self):
        """Turns the axis off"""
        if self.is_moving:
            raise RuntimeError("Can't set power off while axis is moving")

        self.__controller.set_off(self)
        state = self.__controller.state(self)
        self.settings.set("state", state)

    @property
    @lazy_init
    def _set_position(self):
        sp = self.settings.get("_set_position")
        if sp is not None:
            return sp
        position = self.position
        self._set_position = position
        return position

    @_set_position.setter
    @lazy_init
    def _set_position(self, new_set_pos):
        new_set_pos = float(
            new_set_pos
        )  # accepts both float or numpy array of 1 element
        self.settings.set("_set_position", new_set_pos)

    @property
    @lazy_init
    def measured_position(self):
        """
        Return measured position (ie: usually the encoder value).

        Returns:
            float: encoder value in user units
        """
        return self.dial2user(self.dial_measured_position)

    @property
    @lazy_init
    def dial_measured_position(self):
        """
        Dial encoder position.

        Returns:
            float: Dial encoder position
        """
        if self.encoder is not None:
            return self.encoder.read()
        else:
            raise RuntimeError("Axis '%s` has no encoder." % self.name)

    def __do_set_dial(self, new_dial):
        user_pos = self.position

        # Set the new dial on the encoder
        if self._encoder_read_mode:
            dial_pos = self.encoder.set(new_dial)
        else:
            # Send the new value in motor units to the controller
            # and read back the (atomically) reported position
            new_hw = new_dial * self.steps_per_unit
            hw_pos = self.__controller.set_position(self, new_hw)
            dial_pos = hw_pos / self.steps_per_unit
        self.settings.set("dial_position", dial_pos)

        if self.no_offset:
            self.__do_set_position(dial_pos, offset=0)
        else:
            # set user pos, will recalculate offset
            # according to new dial
            self.__do_set_position(user_pos)

        return dial_pos

    @property
    @lazy_init
    def dial(self):
        """
        Return current dial position, or set dial

        Returns:
            float: current dial position (dimensionless)
        """
        dial_pos = self.settings.get("dial_position")
        if dial_pos is None:
            dial_pos = self._update_dial()
        return dial_pos

    @dial.setter
    @lazy_init
    def dial(self, new_dial):
        if self.is_moving:
            raise RuntimeError(
                "%s: can't set axis dial position " "while moving" % self.name
            )
        new_dial = float(new_dial)  # accepts both float or numpy array of 1 element
        old_offset = self.axis_rounder(self.offset)
        old_dial = self.dial
        new_dial = self.__do_set_dial(new_dial)
        new_offset = self.axis_rounder(self.offset)
        print(
            f"'{self.name}` dial position reset from {old_dial} to {new_dial} ; "
            f"offset changed from {old_offset} to {new_offset} (sign:{self.sign})"
        )

    def __do_set_position(self, new_pos=None, offset=None):
        dial = self.dial
        curr_offset = self.offset
        if offset is None:
            # calc offset
            offset = new_pos - self.sign * dial
        if math.isnan(offset):
            # this can happen if dial is nan;
            # cannot continue
            return False
        if math.isclose(offset, 0):
            offset = 0
        if not math.isclose(curr_offset, offset):
            self.settings.set("offset", offset)
        if new_pos is None:
            # calc pos from offset
            new_pos = self.sign * dial + offset
        if math.isnan(new_pos):
            # do not allow to assign nan as a user position
            return False
        self.settings.set("position", new_pos)
        self._set_position = new_pos
        return True

    @property
    @lazy_init
    def position(self):
        """
        Return current user position, or set new user position in user units.

        Returns
        -------
            float: current user position (user units)

        Parameters
        ----------
        new_pos : float
            New position to set, in user units.

        Note
        ----
        This update offset.

        """
        pos = self.settings.get("position")
        if pos is None:
            pos = self.dial2user(self.dial)
            self.settings.set("position", pos)
        return pos

    @position.setter
    @lazy_init
    def position(self, new_pos):
        """See property getter"""
        log_debug(self, "axis.py : position(new_pos=%r)" % new_pos)
        if self.is_moving:
            raise RuntimeError(
                "%s: can't set axis user position " "while moving" % self.name
            )
        new_pos = float(new_pos)  # accepts both float or numpy array of 1 element
        old_offset = self.axis_rounder(self.offset)
        curr_pos = self.position
        if self.no_offset:
            self.dial = new_pos
        if self.__do_set_position(new_pos):
            new_offset = self.axis_rounder(self.offset)
            print(
                f"'{self.name}` position reset from {curr_pos} to {new_pos} ; "
                f"offset changed from {old_offset} to {new_offset} (sign:{self.sign})"
            )

    @property
    def display_digits(self):
        """
        Return number of digits to use in position display.

        This value is determined according to the following rules:

        - use `display_digits` if defined in config.
        - use same number of digits than:
            - `axis.steps_per_unit` if steps_per_unit != 1
            - `axis.tolerance` otherwise

        NB: `axis.tolerance` should always exist.
        """
        # Cached value.
        if self._display_digits is not None:
            return self._display_digits

        # Use `display_digits` value in config in priority.
        self._display_digits = self.config.get("display_digits")

        # `display_digits` not found in config => calculate a default value.
        if self._display_digits is None:
            if self.steps_per_unit < 2:  # Include usual case `steps_per_unit`==1.
                # Use tolerance.
                tol = self.tolerance
                #                print(f"{self.name} USE TOL")
                if tol >= 1:
                    self._display_digits = 2
                else:
                    # Count number of leading zeros in decimal part and add 1.
                    # * tolerance =  0.01          -> digits = 2
                    # * tolerance =  0.0001        -> digits = 4
                    # * tolerance = 12             -> digits = 2
                    # * tolerance = 1e-5 = 0.00001 -> digits = 5
                    self._display_digits = 1 + len(
                        str(f"{float(tol):.15f}").rstrip("0").split(".")[1]
                    )
            else:
                # Use steps_per_unit
                # * steps_per_unit = 555 -> 1 step = 0.0018 -> digits = 4
                # * steps_per_unit =   0.1  -> digits = 0
                if self.steps_per_unit <= 1:
                    self._display_digits = 0
                self._display_digits = len(str(int(self.steps_per_unit))) + 1

        # Ensure value is an integer.
        if not isinstance(self._display_digits, int):
            log_error(
                self,
                f"in display_digits calculation for axis {self.name}: {self._display_digits} (use default: 5)",
            )
            self._display_digits = 5

        return self._display_digits

    @lazy_init
    def _update_dial(self, update_user=True):
        dial_pos = self._hw_position
        update_list = (
            "dial_position",
            dial_pos,
        )
        if update_user:
            update_list += (
                "position",
                self.dial2user(dial_pos, self.offset),
            )
        self.settings.set(*update_list)
        return dial_pos

    @property
    @lazy_init
    def _hw_position(self):
        if self._encoder_read_mode:
            return self.dial_measured_position
        try:
            curr_pos = self.__controller.read_position(self) / self.steps_per_unit
        except NotImplementedError:
            # this controller does not have a 'position'
            # (e.g like some piezo controllers)
            curr_pos = 0
        return curr_pos

    @property
    @lazy_init
    def state(self):
        """
        Return the axis state

        Return:
            AxisState: axis state
        """
        if self.is_moving:
            return AxisState("MOVING")
        state = self.settings.get("state")
        if state is None:
            # really read from hw
            state = self.hw_state
            self.settings.set("state", state)
        return state

    @property
    @lazy_init
    def hw_state(self):
        """Return the current hardware axis state (:obj:`AxisState`)"""
        return self.__controller.state(self)

    def __info__(self):
        """Standard method called by BLISS Shell info helper:
        Return common axis information about the axis and controller specific information.
        Return FormattedText to deal with nice colors :)
        """
        try:
            self._lazy_init()
        except Exception:
            pass

        if self.disabled:
            return FormattedText([("", f"AXIS {self.name} is disabled")])

        from bliss.common.standard import info

        info_string = FormattedText([("", f"AXIS {self.name}\n")])

        if self.unit is not None:
            _unit = "(" + self.unit + ")"
        else:
            _unit = ""

        # position dial offset sign velocity acc spu tolerance
        info_lines = []
        info_lines.append(
            [
                ("class:header", f"position{_unit} "),
                ("class:header", f"dial{_unit}"),
                ("class:header", f"offset{_unit} "),
                ("class:header", "sign"),
                ("class:header", "steps_per_unit"),
                ("class:header", f"tolerance{_unit}"),
            ]
        )

        try:
            info_lines.append(
                [
                    ("class:primary", f"{self.axis_rounder(self.position)}"),
                    f"{self.axis_rounder(self.dial)}",
                    f"{self.axis_rounder(self.offset)}",
                    self.sign,
                    f"{self.steps_per_unit:.2f}",
                    f"{self.tolerance}",
                ]
            )
        except Exception:
            info_lines.append(["Unable to get info..."])

        info_string += FormattedText([("", "\n")])
        info_string += tabulate.tabulate(info_lines)
        info_string += FormattedText([("", "\n")])
        info_string += FormattedText([("", "\n")])

        # SETTINGS WITH CONFIG VALUES
        swc_lines = []
        _low_cfg_limit, _high_cfg_limit = self.config_limits

        swc_lines.append(["    ", "CURRENT VALUES", "|", "CONFIG VALUES"])
        swc_lines.append(["    ", "--------------", "|", "-------------"])

        try:
            # limits
            swc_lines.append(
                [
                    f"limits{_unit} [low ; high]",
                    f"[ {self.low_limit:.5f} ; {self.high_limit:.5f}]",
                    "|",
                    f"[ {_low_cfg_limit:.5f} ; {_high_cfg_limit:.5f}]",
                ]
            )

            try:
                # velocity and velocity limits
                swc_lines.append(
                    [
                        f"velocity ({self.unit}/s)",
                        f"{self.velocity}",
                        "|",
                        f"{self.config_velocity}",
                    ]
                )
                vel_low, vel_high = self.velocity_limits
                vel_config_low, vel_config_high = self.config_velocity_limits

                swc_lines.append(
                    [
                        "velocity limits [low ; high]",
                        f"[ {vel_low:.5f} ; {vel_high:.5f}]",
                        "|",
                        f"[ {vel_config_low:.5f} ; {vel_config_high:.5f}]",
                    ]
                )
            except NotImplementedError:
                pass

            try:
                # acceleration / acctime
                swc_lines.append(
                    [
                        f"acceleration ({self.unit}/s²)",
                        f"{self.acceleration}",
                        "|",
                        f"{self.config_acceleration}",
                    ]
                )
                swc_lines.append(
                    ["acctime (s)", f"{self.acctime}", "|", f"{self.config_acctime}"]
                )
            except NotImplementedError:
                pass

            # backlash
            swc_lines.append(
                [
                    f"backlash{_unit}",
                    f"{self.axis_rounder(self.backlash)}",
                    "|",
                    f"{self.axis_rounder(self.config_backlash)}",
                ]
            )
            swc_lines.append(["    ", "", "", ""])

            info_string += tabulate.tabulate(
                swc_lines,
                # tablefmt="plain",
                # colalign=("left", "right", "center", "left"),
            )
            info_string += FormattedText([("", "\n")])

        except Exception:
            info_string += FormattedText([("", "Error reading parameters...\n")])

        # jog_velocity jog_acctime
        # TODO ???

        try:
            # Axis State(s)
            states_line = []
            for _state in self.state.current_states_names:
                if _state in self.state._STANDARD_STATES:
                    states_line.append(
                        (self.state._STANDARD_STATES_STYLES[_state], _state + " ")
                    )

                elif _state in ["ALARM", "ALARMDESC"]:
                    states_line.append(("class:danger", _state + " "))
                elif _state == "SCSTOP":
                    states_line.append(("class:info", _state + " "))
                else:
                    states_line.append(("", _state + " "))

            if len(self.state.current_states_names) > 1:
                info_string += FormattedText([("", "STATES: ")])
            else:
                info_string += FormattedText([("", "STATE: ")])

            info_string += FormattedText(states_line)
            info_string += FormattedText([("", "\n")])

        except Exception:
            info_string += FormattedText([("", "Error reading state...\n")])

        # SPECIFIC AXIS INFO
        try:
            # usage of get_axis_info() to pass axis as param.
            info_string += FormattedText([("", "\n")])
            info_string += FormattedText(
                [("", self.__controller.get_axis_info(self) + "\n")]
            )
        except Exception:
            info_string += FormattedText(
                [("", "ERROR: Unable to get axis info from controller\n")]
            )

        # ENCODER
        if self.encoder is not None:
            try:
                # Encoder is initialised here if not already done.
                info_string += FormattedText([("", info(self.encoder) + "\n")])
            except Exception:
                info_string += FormattedText(
                    [("", "ERROR: Unable to get encoder info\n")]
                )
        else:
            info_string += FormattedText([("", "ENCODER not present\n")])

        # CLOSED-LOOP
        if not self._disabled:
            if self.closed_loop is not None:
                try:
                    info_string += FormattedText([("", info(self.closed_loop))])
                except Exception:
                    info_string += FormattedText(
                        [("", "ERROR: Unable to get closed loop info\n")]
                    )
            else:
                info_string += FormattedText([("", "CLOSED-LOOP not present\n")])

        # MOTION HOOK
        if self.motion_hooks:
            info_string += FormattedText([("", "MOTION HOOKS:\n")])
            for hook in self.motion_hooks:
                info_string += FormattedText([("", f"          {hook}\n")])
        else:
            info_string += FormattedText([("", "MOTION HOOKS not present\n")])

        # CONTROLLER
        def bliss_obj_ref(obj):

            if hasattr(self.__controller, "name"):
                return self.__controller.name
            return f"{type(self.__controller)}({repr(self.__controller)})"

        if self.controller is not None:
            info_string += FormattedText(
                [
                    (
                        "",
                        f"CONTROLLER:\n name: {bliss_obj_ref(self.__controller)}  (type ",
                    ),
                    ("class:em", f"{self.name}.controller"),
                    ("", " for more information)"),
                ]
            )

        return info_string

    def sync_hard(self):
        """Forces an axis synchronization with the hardware"""
        self.settings.set("state", self.hw_state)
        self._update_dial()
        self._set_position = self.position
        if self.closed_loop is not None:
            self.closed_loop.sync_hard()
        event.send(self, "sync_hard")

    def _check_velocity_limits(self, new_velocity):
        min_velocity, max_velocity = self.velocity_limits
        if abs(new_velocity) > abs(max_velocity):
            raise ValueError(
                f"Velocity ({new_velocity}) exceeds max. velocity: {max_velocity}"
            )
        if min_velocity != float("inf") and abs(new_velocity) < abs(min_velocity):
            raise ValueError(
                f"Velocity ({new_velocity}) is below min. velocity: {min_velocity}"
            )

    @property
    @lazy_init
    def velocity(self):
        """
        Return or set the current velocity.

        Parameters:
            float: new_velocity in user unit/second
        Return:
            float: current velocity in user unit/second
        """
        # Read -> Return velocity read from motor axis.
        _user_vel = self.settings.get("velocity")
        if _user_vel is None:
            _user_vel = self.__controller.read_velocity(self) / abs(self.steps_per_unit)

        return _user_vel

    @velocity.setter
    @lazy_init
    def velocity(self, new_velocity):
        # Write -> Converts into motor units to change velocity of axis.
        new_velocity = float(
            new_velocity
        )  # accepts both float or numpy array of 1 element
        self._check_velocity_limits(new_velocity)

        if new_velocity < 0:
            raise RuntimeError(
                "Invalid velocity, the velocity cannot be a negative value"
            )

        try:
            self.__controller.set_velocity(
                self, new_velocity * abs(self.steps_per_unit)
            )
        except Exception as err:
            raise ValueError(
                "Cannot set value {} for {}".format(new_velocity, self.name)
            ) from err

        _user_vel = self.__controller.read_velocity(self) / abs(self.steps_per_unit)

        if not math.isclose(new_velocity, _user_vel, abs_tol=1e-4):
            log_warning(
                self,
                f"Controller velocity ({_user_vel}) is different from set velocity ({new_velocity})",
            )

        curr_vel = self.settings.get("velocity")
        if curr_vel != _user_vel:
            print(f"'{self.name}` velocity changed from {curr_vel} to {_user_vel}")
        self.settings.set("velocity", _user_vel)

        return _user_vel

    @property
    @lazy_init
    def config_velocity(self):
        """
        Return the config velocity.

        Return:
            float: config velocity (user units/second)
        """
        return self.__config_velocity

    @property
    @lazy_init
    def config_velocity_limits(self):
        """
        Return the config velocity limits.

        Return:
            (low_limit, high_limit): config velocity (user units/second)
        """
        return self.__config_velocity_low_limit, self.__config_velocity_high_limit

    @property
    def velocity_limits(self):
        return self.velocity_low_limit, self.velocity_high_limit

    @velocity_limits.setter
    def velocity_limits(self, limits):
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .velocity_limits = low, high")
        ll = float_or_inf(limits[0], inf_sign=1)
        hl = float_or_inf(limits[1], inf_sign=1)
        self.settings.set("velocity_low_limit", ll)
        self.settings.set("velocity_high_limit", hl)

    @property
    @lazy_init
    def velocity_high_limit(self):
        """
        Return the limit max of velocity
        """
        return float_or_inf(self.settings.get("velocity_high_limit"))

    @velocity_high_limit.setter
    @lazy_init
    def velocity_high_limit(self, value):
        self.settings.set("velocity_high_limit", float_or_inf(value))

    @property
    @lazy_init
    def velocity_low_limit(self):
        """
        Return the limit max of velocity
        """
        return float_or_inf(self.settings.get("velocity_low_limit"))

    @velocity_low_limit.setter
    @lazy_init
    def velocity_low_limit(self, value):
        self.settings.set("velocity_low_limit", float_or_inf(value))

    def _set_jog_motion(self, motion, velocity):
        """Set jog velocity to controller

        Velocity is a signed value ; takes direction into account
        """
        velocity_in_steps = velocity * self.sign * self.steps_per_unit
        direction = -1 if velocity_in_steps < 0 else 1
        motion.jog_velocity = abs(velocity_in_steps)
        motion.direction = direction

        backlash = self._get_backlash_steps()
        if backlash:
            if math.copysign(direction, backlash) != direction:
                motion.backlash = backlash
        else:
            # don't do backlash correction
            motion.backlash = 0

    def _get_jog_motion(self):
        """Return motion object if axis is moving in jog mode

        Return values:
        - motion object, if axis is moving in jog mode
        - False if the jog move has been initiated by another BLISS
        - None if axis is not moving, or if there is no jog motion
        """
        if self.is_moving:
            if self._group_move.is_moving:
                for motions in self._group_move.motions_dict.values():
                    for motion in motions:
                        if motion.axis is self and motion.type == "jog":
                            return motion
            else:
                return False

    def _set_jog_velocity(self, new_velocity):
        """Set jog velocity

        If motor is moving, and we are in a jog move, the jog command is re-issued to
        set the new velocity.
        It is expected an error to be raised in case the controller does not support it.
        If the motor is not moving, only the setting is changed.

        Return values:
        - True if new velocity has been set
        - False if the jog move has been initiated by another BLISS ('external move')
        """
        motion = self._get_jog_motion()

        if motion is not None:
            if new_velocity == 0:
                self.stop()
            else:
                if motion:
                    self._set_jog_motion(motion, new_velocity)
                    self.controller.start_jog(
                        self, motion.jog_velocity, motion.direction
                    )
                    print(motion.user_msg)
                else:
                    # jog move has been started externally
                    return False

        if new_velocity:
            # it is None the first time the channel is initialized,
            # it can be 0 to stop the jog move in this case we don't update the setting
            self.settings.set("jog_velocity", new_velocity)

        return True

    @property
    @lazy_init
    def jog_velocity(self):
        """
        Return the current jog velocity.

        Return:
            float: current jog velocity (user units/second)
        """
        # Read -> Return velocity read from motor axis.
        _user_jog_vel = self.settings.get("jog_velocity")
        if _user_jog_vel is None:
            _user_jog_vel = self.velocity
        return _user_jog_vel

    @jog_velocity.setter
    @lazy_init
    def jog_velocity(self, new_velocity):
        new_velocity = float(
            new_velocity
        )  # accepts both float or numpy array of 1 element
        if not self._set_jog_velocity(new_velocity):
            # move started externally => use channel to inform
            self._jog_velocity_channel.value = new_velocity

    @property
    @lazy_init
    def config_jog_velocity(self) -> float:
        """
        Returns the config jog velocity (user_units/second).
        """
        return self.__config_jog_velocity

    @property
    @lazy_init
    def acceleration(self) -> float:
        """
        Returns the acceleration.
        """
        _acceleration = self.settings.get("acceleration")
        if _acceleration is None:
            _ctrl_acc = self.__controller.read_acceleration(self)
            _acceleration = _ctrl_acc / abs(self.steps_per_unit)

        return _acceleration

    @acceleration.setter
    @lazy_init
    def acceleration(self, new_acc: float):
        """
        Parameters:
            new_acc: new acceleration that has to be provided in user_units/s2.

        Return:
            acceleration: acceleration (user_units/s2)
        """
        if self.is_moving:
            raise RuntimeError(
                "Cannot set acceleration while axis '%s` is moving." % self.name
            )
        new_acc = float(new_acc)  # accepts both float or numpy array of 1 element
        # Converts into motor units to change acceleration of axis.
        self.__controller.set_acceleration(self, new_acc * abs(self.steps_per_unit))
        _ctrl_acc = self.__controller.read_acceleration(self)
        _acceleration = _ctrl_acc / abs(self.steps_per_unit)
        curr_acc = self.settings.get("acceleration")
        if curr_acc != _acceleration:
            print(
                f"'{self.name}` acceleration changed from {curr_acc} to {_acceleration}"
            )
        self.settings.set("acceleration", _acceleration)
        return _acceleration

    @property
    @lazy_init
    def config_acceleration(self):
        """
        Acceleration specified in IN-MEMORY config.

        Note
        ----
        this is not necessarily the current acceleration.
        """
        return self.__config_acceleration

    @property
    @lazy_init
    def acctime(self):
        """
        Return the current acceleration time.

        Return:
            float: current acceleration time (second)
        """
        return abs(self.velocity / self.acceleration)

    @acctime.setter
    @lazy_init
    def acctime(self, new_acctime):
        # Converts acctime into acceleration.
        new_acctime = float(
            new_acctime
        )  # accepts both float or numpy array of 1 element
        self.acceleration = self.velocity / new_acctime
        return abs(self.velocity / self.acceleration)

    @property
    def config_acctime(self):
        """
        Return the config acceleration time.
        """
        return abs(self.config_velocity / self.config_acceleration)

    @property
    @lazy_init
    def jog_acctime(self):
        """
        Return the current acceleration time for jog move.

        Return:
            float: current acceleration time for jog move (second)
        """
        return abs(self.jog_velocity / self.acceleration)

    @property
    def config_jog_acctime(self):
        """
        Return the config acceleration time.
        """
        return abs(self.config_jog_velocity) / self.config_acceleration

    @property
    def dial_limits(self):
        ll = float_or_inf(self.settings.get("low_limit"), inf_sign=-1)
        hl = float_or_inf(self.settings.get("high_limit"), inf_sign=1)
        return ll, hl

    @dial_limits.setter
    @lazy_init
    def dial_limits(self, limits):
        """
        Set low, high limits in dial units
        """
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .dial_limits = low, high")
        ll = float_or_inf(limits[0], inf_sign=-1)
        hl = float_or_inf(limits[1], inf_sign=1)
        self.settings.set("low_limit", ll)
        self.settings.set("high_limit", hl)

    @property
    def limits(self):
        """
        Return or set the current software limits in USER units.

        Return:
            tuple<float, float>: axis software limits (user units)

        Example:

            $ my_axis.limits = (-10,10)

        """
        return tuple(map(self.dial2user, self.dial_limits))

    @limits.setter
    def limits(self, limits):
        # Set limits (low, high) in user units.
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .limits = low, high")

        # accepts iterable (incl. numpy array)
        self.low_limit, self.high_limit = (
            float(x) if x is not None else None for x in limits
        )

    @property
    def low_limit(self):
        # Return Low Limit in USER units.
        ll, hl = self.dial_limits
        return self.dial2user(ll)

    @low_limit.setter
    @lazy_init
    def low_limit(self, limit):
        # Sets Low Limit
        # <limit> must be given in USER units
        # Saved in settings in DIAL units
        if limit is not None:
            limit = float(limit)  # accepts numpy array of 1 element, or float
            limit = self.user2dial(limit)
        self.settings.set("low_limit", limit)

    @property
    def high_limit(self):
        # Return High Limit in USER units.
        ll, hl = self.dial_limits
        return self.dial2user(hl)

    @high_limit.setter
    @lazy_init
    def high_limit(self, limit):
        # Sets High Limit (given in USER units)
        # Saved in settings in DIAL units.
        if limit is not None:
            limit = float(limit)  # accepts numpy array of 1 element, or float
            limit = self.user2dial(limit)
        self.settings.set("high_limit", limit)

    @property
    def config_limits(self):
        """
        Return a tuple (low_limit, high_limit) from IN-MEMORY config in
        USER units.
        """
        ll_dial = self.__config_low_limit
        hl_dial = self.__config_high_limit
        return tuple(map(self.dial2user, (ll_dial, hl_dial)))

    def _update_settings(self, state=None):
        """Update position and state in redis

        By defaul, state is read from hardware; otherwise the given state is used
        Position is always read.

        In case of an exception (represented as X) during one of the readings,
        state is set to FAULT:

        state | pos | axis state | axis pos
        ------|-----|-----------------------
          OK  | OK  |   state    |  pos
          X   | OK  |   FAULT    |  pos
          OK  |  X  |   FAULT    |  not updated
          X   |  X  |   FAULT    |  not updated
        """
        state_reading_exc = None

        if state is None:
            try:
                state = self.hw_state
            except BaseException as exc:
                # save exception to re-raise it afterwards
                state_reading_exc = exc
                state = AxisState("FAULT")
        try:
            self._update_dial()
        except BaseException:
            state = AxisState("FAULT")
            raise
        finally:
            self.settings.set("state", state)
            if state_reading_exc:
                raise state_reading_exc

    def dial2user(self, position, offset=None):
        """
        Translates given position from DIAL units to USER units

        Args:
            position (float): position in dial units

        Keyword Args:
            offset (float): alternative offset. None (default) means use current offset

        Return:
            float: position in axis user units
        """
        if position is None:
            # see limits
            return None
        if offset is None:
            offset = self.offset
        return (self.sign * position) + offset

    def user2dial(self, position):
        """
        Translates given position from user units to dial units

        Args:
            position (float): position in user units

        Return:
            float: position in axis dial units
        """
        return (position - self.offset) / self.sign

    def _get_encoder_delta_steps(self, encoder_dial_pos):
        """
        Return the difference between given encoder position and motor controller indexer, in steps
        """
        if self._encoder_read_mode:
            controller_steps = self.__controller.read_position(self)
            enc_steps = encoder_dial_pos * self.steps_per_unit
            return controller_steps - enc_steps
        return 0

    def _backlash_is_dial(self):
        return bool(self.config.config_dict.get("backlash_is_dial"))

    def _get_backlash_steps(self):
        backlash_steps = self.backlash * self.steps_per_unit
        if not self._backlash_is_dial():
            backlash_steps = backlash_steps * self.sign
        return backlash_steps

    def _get_motion(self, user_target_pos, polling_time=None) -> Motion | None:
        dial_target_pos = self.user2dial(user_target_pos)
        dial = self.dial  # read from encoder if self._encoder_read_mode
        target_pos = dial_target_pos * self.steps_per_unit
        delta = target_pos - dial * self.steps_per_unit

        # return if already in position (no motion)
        if self.controller._is_already_on_position(self, delta):
            return None

        motion = Motion(
            self,
            target_pos,
            delta,
        )

        # evaluate backlash correction
        backlash_str = ""
        if self.backlash:
            backlash = self._get_backlash_steps()
            if abs(delta) > 0 and math.copysign(delta, backlash) != delta:
                # move and backlash are not in the same direction;
                # apply backlash correction, the move will happen
                # in 2 steps
                backlash_str = f" (with {self.backlash} backlash)"  # in units
                motion.backlash = backlash  # in steps

        # check software limits (backlash included, encoder excluded)
        low_limit_msg = "%s: move to `%s'%s would exceed low limit (%s)"
        high_limit_msg = "%s: move to `%s'%s would exceed high limit (%s)"
        user_low_limit, user_high_limit = self.limits
        low_limit = self.user2dial(user_low_limit) * self.steps_per_unit
        high_limit = self.user2dial(user_high_limit) * self.steps_per_unit
        if high_limit < low_limit:
            high_limit, low_limit = low_limit, high_limit
            user_high_limit, user_low_limit = user_low_limit, user_high_limit
            high_limit_msg, low_limit_msg = low_limit_msg, high_limit_msg
        if motion.target_pos < low_limit:
            raise ValueError(
                low_limit_msg
                % (self.name, user_target_pos, backlash_str, user_low_limit)
            )
        if motion.target_pos > high_limit:
            raise ValueError(
                high_limit_msg
                % (self.name, user_target_pos, backlash_str, user_high_limit)
            )

        # evaluate encoder motion correction
        motion.encoder_delta = self._get_encoder_delta_steps(dial)

        if polling_time is not None:
            motion.polling_time = polling_time

        return motion

    @lazy_init
    def get_motion(
        self, user_target_pos, relative=False, polling_time=None
    ) -> Motion | None:
        """Prepare a motion. Internal usage only"""

        # To accept both float or numpy array of 1 element
        user_target_pos = float(user_target_pos)

        log_debug(
            self,
            "get_motion: user_target_pos=%g, relative=%r" % (user_target_pos, relative),
        )

        if relative:
            # start from last set position
            user_initial_pos = self._set_position
            user_target_pos += user_initial_pos

        # obtain motion object
        motion = self._get_motion(user_target_pos, polling_time)
        if motion is None:
            # Already in position, just update set_pos
            self._set_position = user_target_pos
            return None

        # check discrepancy
        check_discrepancy = self.config.get("check_discrepancy", bool, True) and (
            not (self._encoder_read_mode and not self._check_encoder)
        )
        if check_discrepancy:
            dial_initial_pos = self.dial
            hw_pos = self._hw_position
            diff_discrepancy = abs(dial_initial_pos - hw_pos)
            if diff_discrepancy > self.tolerance:
                raise RuntimeError(
                    "%s: discrepancy between dial (%f) and controller position (%f)\n \
                        diff=%g tolerance=%g => aborting movement."
                    % (
                        self.name,
                        dial_initial_pos,
                        hw_pos,
                        diff_discrepancy,
                        self.tolerance,
                    )
                )

        return motion

    def _set_moving_state(self, from_channel=False):
        self.__move_done.clear()
        self.__move_done_callback.clear()
        _emit_move_done(self, value=False, from_channel=from_channel)

        moving_state = AxisState("MOVING")
        if from_channel:
            event.send_safe(self, "state", moving_state)
        else:
            self.settings.set("state", moving_state)

    def _set_move_done(self, from_channel=False):
        with capture_exceptions(raise_index=0) as capture:
            with capture():
                if not from_channel:
                    self._update_settings()

            self.__move_done.set()

            with capture():
                _emit_move_done(self, value=True, from_channel=from_channel)

            self.__move_done_callback.set()

    def _check_ready(self):
        if not self.controller.check_ready_to_move(self, self.state):
            raise RuntimeError("axis %s state is " "%r" % (self.name, str(self.state)))

    @lazy_init
    def move(self, user_target_pos, wait=True, relative=False, polling_time=None):
        """
        Move axis to the given absolute/relative position

        Parameters:
            user_target_pos: float
                Destination (user units)
            wait : bool, optional
                Wait or not for end of motion
            relative : bool
                False if *user_target_pos* is given in absolute position or True if it is given in relative position
            polling_time : float
                Motion loop polling time (seconds)

        Raises:
            RuntimeError

        Returns:
            None

        """
        # accepts both floats and numpy arrays of 1 element
        user_target_pos = float(user_target_pos)

        if not numpy.isfinite(user_target_pos):
            raise ValueError(
                f"axis {self.name} cannot be moved to position: {user_target_pos}"
            )

        log_debug(
            self,
            "user_target_pos=%g  wait=%r relative=%r"
            % (user_target_pos, wait, relative),
        )
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            self._group_move = GroupMove()
            self._group_move.move(
                {self: user_target_pos},
                _prepare_one_controller_motions,
                _start_one_controller_motions,
                _stop_one_controller_motions,
                relative=relative,
                wait=False,
                polling_time=polling_time,
            )

        if wait:
            self.wait_move()

    def _handle_move(self, motion, ctrl_state_func="state", limit_error=True):
        state = None
        try:
            state = self._move_loop(motion.polling_time, ctrl_state_func, limit_error)
        finally:
            motion.last_state = state
        return state

    def _do_encoder_reading(self):
        enc_dial = self.encoder.read()
        curr_pos = self._update_dial()
        if abs(curr_pos - enc_dial) > self.encoder.tolerance:
            raise RuntimeError(
                f"'{self.name}' didn't reach final position."
                f"(enc_dial={enc_dial:10.5f}, curr_pos={curr_pos:10.5f} "
                f"diff={enc_dial-curr_pos:10.5f} enc.tol={self.encoder.tolerance:10.5f})"
            )

    @lazy_init
    def jog(self, velocity=None, reset_position=None, polling_time=None):
        """
        Start to move axis at constant velocity

        Args:
            velocity: signed velocity for constant speed motion
        """
        if velocity is not None:
            velocity = float(
                velocity
            )  # accepts both floats or numpy arrays of 1 element

            if self._get_jog_motion() is not None:
                # already in jog move
                self.jog_velocity = velocity
                return
        else:
            velocity = self.jog_velocity

        self._check_velocity_limits(velocity)

        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            if velocity == 0:
                return

            self.jog_velocity = velocity

            motion = Motion(self, None, None, motion_type="jog")
            motion.polling_time = polling_time
            motion.saved_velocity = self.velocity
            motion.reset_position = reset_position
            self._set_jog_motion(
                motion, velocity
            )  # this will complete motion configuration

            def start_jog(controller, motions):
                controller.start_jog(
                    motions[0].axis, motion.jog_velocity, motion.direction
                )

            def stop_one(controller, motions):
                controller.stop_jog(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_jog,
                stop_one,
                "_jog_move",
                wait=False,
            )

    def _jog_move(self, motion):
        return self._handle_move(motion)

    def _jog_cleanup(self, saved_velocity, reset_position):
        self.velocity = saved_velocity

        if reset_position is None:
            self.settings.clear("_set_position")
        elif reset_position == 0:
            self.__do_set_dial(0)
        elif callable(reset_position):
            reset_position(self)

    def rmove(self, user_delta_pos, wait=True, polling_time=None):
        """
        Move axis to the given relative position.

        Same as :meth:`move` *(relative=True)*

        Args:
            user_delta_pos: motor displacement (user units)
        Keyword Args:
            wait (bool): wait or not for end of motion
            polling_time (float): motion loop polling time (seconds)
        """
        log_debug(self, "user_delta_pos=%g  wait=%r" % (user_delta_pos, wait))
        return self.move(
            user_delta_pos, wait=wait, relative=True, polling_time=polling_time
        )

    def _move_loop(self, polling_time, ctrl_state_func, limit_error=True):
        state_funct = getattr(self.__controller, ctrl_state_func)
        while True:
            state = state_funct(self)
            self._update_settings(state)
            if not state.MOVING:
                if limit_error and (state.LIMPOS or state.LIMNEG):
                    raise AxisOnLimitError(
                        f"{self.name}: {str(state)} at {self.position}"
                    )
                elif state.OFF:
                    raise AxisOffError(f"{self.name}: {str(state)}")
                elif state.FAULT:
                    raise AxisFaultError(f"{self.name}: {str(state)}")
                return state
            gevent.sleep(polling_time)

    @lazy_init
    def stop(self, wait=True):
        """
        Stops the current motion

        If axis is not moving returns immediately

        Args:
            wait (bool): wait for the axis to decelerate before returning \
            [default: True]
        """
        if self.is_moving:
            if self._group_move._move_task:
                self._group_move.stop(wait)
            else:
                # move started externally
                self._move_stop_channel.value = True

            if wait:
                self.wait_move()

    def wait_move(self):
        """
        Wait for the axis to finish motion (blocks current :class:`Greenlet`)
        """
        try:
            self.__move_done_callback.wait()
        except BaseException:
            self.stop(wait=False)
            raise
        finally:
            self._group_move.wait()

    def _external_stop(self, stop):
        if stop:
            self.stop()

    @lazy_init
    def home(self, switch=1, wait=True, polling_time=None):
        """
        Searches the home switch

        Args:
            wait (bool): wait for search to finish [default: True]
        """
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            # create motion object for hooks
            motion = Motion(
                self,
                target_pos=switch,
                delta=None,
                motion_type="homing",
                target_name="home",
            )
            motion.polling_time = (
                self._polling_time if polling_time is None else polling_time
            )

            def start_one(controller, motions):
                controller.home_search(motions[0].axis, motions[0].target_pos)

            def stop_one(controller, motions):
                controller.stop(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_one,
                stop_one,
                "_wait_home",
                wait=False,
            )

        if wait:
            self.wait_move()

    def _wait_home(self, motion):
        return self._handle_move(motion, ctrl_state_func="home_state")

    @lazy_init
    def hw_limit(self, limit, wait=True, polling_time=None):
        """
        Go to a hardware limit

        Args:
            limit (int): positive means "positive limit"
            wait (bool): wait for axis to finish motion before returning \
            [default: True]
        """
        limit = int(limit)
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            motion = Motion(
                self,
                target_pos=limit,
                delta=None,
                motion_type="limit_search",
                target_name="lim+" if limit > 0 else "lim-",
            )
            motion.polling_time = (
                self._polling_time if polling_time is None else polling_time
            )

            def start_one(controller, motions):
                controller.limit_search(motions[0].axis, motions[0].target_pos)

            def stop_one(controller, motions):
                controller.stop(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_one,
                stop_one,
                "_wait_limit_search",
                wait=False,
            )

        if wait:
            self.wait_move()

    def _wait_limit_search(self, motion):
        return self._handle_move(motion, limit_error=False)

    def settings_to_config(
        self, velocity=True, acceleration=True, limits=True, sign=True, backlash=True
    ):
        """
        Set settings values in in-memory config then save it in file.
        Settings to save can be specified.
        """
        if velocity:
            ll, hl = self.velocity_limits
            self.__config.set("velocity", self.velocity)
            self.__config.set("velocity_low_limit", ll)
            self.__config.set("velocity_high_limit", hl)
        if acceleration:
            self.__config.set("acceleration", self.acceleration)
        if limits:
            ll, hl = self.dial_limits
            self.__config.set("low_limit", ll)
            self.__config.set("high_limit", hl)
        if sign:
            self.__config.set("sign", self.sign)
        if backlash:
            self.__config.set("backlash", self.backlash)

        if any((velocity, acceleration, limits, sign, backlash)):
            self.__config.save()
            self._init_config_properties(
                velocity=velocity,
                acceleration=acceleration,
                limits=limits,
                sign=sign,
                backlash=backlash,
            )

    def apply_config(
        self,
        reload=False,
        velocity=True,
        acceleration=True,
        limits=True,
        sign=True,
        backlash=True,
    ):
        """
        Applies configuration values (yml) to the current settings.

        Note
        ----
        This resets the axis settings to those specified in the config

        Parameters
        ----------
        reload : bool
            if True config files are reloaded by beacon.
        """
        if reload:
            self.config.reload()

        if self._closed_loop is not None:
            self._closed_loop.apply_config(reload)

        if self.encoder is not None:
            self.encoder.apply_config(reload)

        self._init_config_properties(
            velocity=velocity,
            acceleration=acceleration,
            limits=limits,
            sign=sign,
            backlash=backlash,
        )

        if velocity:
            self.settings.clear("velocity")
            self.settings.clear("velocity_low_limit")
            self.settings.clear("velocity_high_limit")
        if acceleration:
            self.settings.clear("acceleration")
        if limits:
            self.settings.clear("low_limit")
            self.settings.clear("high_limit")
        if sign:
            self.settings.clear("sign")
        if backlash:
            self.settings.clear("backlash")

        self._disabled = False
        self.settings.init()

        # update position (needed for sign change)
        pos = self.dial2user(self.dial)
        if self.position != pos:
            try:
                self.position = self.dial2user(self.dial)
            except NotImplementedError:
                pass

    @lazy_init
    def set_event_positions(self, positions):
        dial_positions = self.user2dial(numpy.array(positions, dtype=float))
        step_positions = dial_positions * self.steps_per_unit
        return self.__controller.set_event_positions(self, step_positions)

    @lazy_init
    def get_event_positions(self):
        step_positions = numpy.array(
            self.__controller.get_event_positions(self), dtype=float
        )
        dial_positions = self.dial2user(step_positions)
        return dial_positions / self.steps_per_unit

    @lazy_init
    def dataset_metadata(self):
        return {"name": self.name, "value": self.position}


class AxisState:
    """
    Standard states:
      MOVING  : 'Axis is moving'
      READY   : 'Axis is ready to be moved (not moving ?)'
      FAULT   : 'Error from controller'
      LIMPOS  : 'Hardware high limit active'
      LIMNEG  : 'Hardware low limit active'
      HOME    : 'Home signal active'
      OFF     : 'Axis power is off'
      DISABLED: 'Axis cannot move (must be enabled - not ready ?)'

    When creating a new instance, you can pass any number of arguments, each
    being either a string or tuple of strings (state, description). They
    represent custom axis states.
    """

    #: state regular expression validator
    STATE_VALIDATOR = re.compile(r"^[A-Z0-9]+\s*$")

    _STANDARD_STATES = {
        "READY": "Axis is READY",
        "MOVING": "Axis is MOVING",
        "FAULT": "Error from controller",
        "LIMPOS": "Hardware high limit active",
        "LIMNEG": "Hardware low limit active",
        "HOME": "Home signal active",
        "OFF": "Axis power is off",
        "DISABLED": "Axis cannot move",
    }

    _STANDARD_STATES_STYLES = {
        "READY": "class:success",
        "MOVING": "class:info",
        "FAULT": "class:danger",
        "LIMPOS": "class:warning",
        "LIMNEG": "class:warning",
        "HOME": "class:success",
        "OFF": "class:info",
        "DISABLED": "class:secondary",
    }

    @property
    def READY(self):
        """Axis is ready to be moved"""
        return "READY" in self._current_states

    @property
    def MOVING(self):
        """Axis is moving"""
        return "MOVING" in self._current_states

    @property
    def FAULT(self):
        """Error from controller"""
        return "FAULT" in self._current_states

    @property
    def LIMPOS(self):
        """Hardware high limit active"""
        return "LIMPOS" in self._current_states

    @property
    def LIMNEG(self):
        """Hardware low limit active"""
        return "LIMNEG" in self._current_states

    @property
    def OFF(self):
        """Axis power is off"""
        return "OFF" in self._current_states

    @property
    def HOME(self):
        """Home signal active"""
        return "HOME" in self._current_states

    @property
    def DISABLED(self):
        """Axis is disabled (must be enabled to move (not ready ?))"""
        return "DISABLED" in self._current_states

    def __init__(self, *states):
        """
        <*states> : can be one or many string or tuple of strings (state, description)
        """

        # set of active states.
        self._current_states = list()

        # dict of descriptions of states.
        self._state_desc = self._STANDARD_STATES

        for state in states:
            if isinstance(state, tuple):
                self.create_state(*state)
                self.set(state[0])
            else:
                if isinstance(state, AxisState):
                    state = state.current_states()
                self._set_state_from_string(state)

    def states_list(self):
        """
        Return a list of available/created states for this axis.
        """
        return list(self._state_desc)

    def _check_state_name(self, state_name):
        if not isinstance(state_name, str) or not AxisState.STATE_VALIDATOR.match(
            state_name
        ):
            raise ValueError(
                "Invalid state: a state must be a string containing only block letters"
            )

    def _has_custom_states(self):
        return self._state_desc is not AxisState._STANDARD_STATES

    def create_state(self, state_name, state_desc=None):
        """
        Adds a new custom state

        Args:
            state_name (str): name of the new state
        Keyword Args:
            state_desc (str): state description [default: None]

        Raises:
            ValueError: if state_name is invalid
        """
        # Raises ValueError if state_name is invalid.
        self._check_state_name(state_name)
        if state_desc is not None and "|" in state_desc:
            raise ValueError(
                "Invalid state: description contains invalid character '|'"
            )

        # if it is the first time we are creating a new state, create a
        # private copy of standard states to be able to modify locally
        if not self._has_custom_states():
            self._state_desc = AxisState._STANDARD_STATES.copy()

        if state_name not in self._state_desc:
            # new description is put in dict.
            if state_desc is None:
                state_desc = "Axis is %s" % state_name
            self._state_desc[state_name] = state_desc

            # Makes state accessible via a class property.
            # NO: we can't, because the objects of this class will become unpickable,
            # as the class changes...
            # Error message is: "Can't pickle class XXX: it's not the same object as XXX"
            # add_property(self, state_name, lambda _: state_name in self._current_states)

    """
    Flags ON a given state.
    ??? what about other states : clear other states ???  -> MG : no
    ??? how to flag OFF ???-> no : on en cree un nouveau.
    """

    def set(self, state_name):
        """
        Activates the given state on this AxisState

        Args:
            state_name (str): name of the state to activate

        Raises:
            ValueError: if state_name is invalid
        """
        if state_name in self._state_desc:
            if state_name not in self._current_states:
                self._current_states.append(state_name)

                # Mutual exclusion of READY and MOVING
                if state_name == "READY":
                    if self.MOVING:
                        self._current_states.remove("MOVING")
                if state_name == "MOVING":
                    if self.READY:
                        self._current_states.remove("READY")
        else:
            raise ValueError("state %s does not exist" % state_name)

    def unset(self, state_name):
        """
        Deactivates the given state on this AxisState

        Args:
            state_name (str): name of the state to deactivate

        Raises:
            ValueError: if state_name is invalid
        """
        self._current_states.remove(state_name)

    def clear(self):
        """Clears all current states"""
        # Flags all states off.
        self._current_states = list()

    @property
    def current_states_names(self):
        """
        Return a list of the current states names
        """
        return self._current_states[:]

    def current_states(self):
        """
        Return a string of current states.

        Return:
            str: *|* separated string of current states or string *UNKNOWN* \
            if there is no current state
        """
        states = [
            "%s%s"
            % (
                state.rstrip(),
                (
                    " (%s)" % self._state_desc[state]
                    if self._state_desc.get(state)
                    else ""
                ),
            )
            for state in map(str, self._current_states)
        ]

        if len(states) == 0:
            return "UNKNOWN"

        return " | ".join(states)

    def _set_state_from_string(self, state):
        # is state_name a full list of states returned by self.current_states() ?
        # (copy constructor)
        if "(" in state:
            full_states = [s.strip() for s in state.split("|")]
            p = re.compile(r"^([A-Z0-9]+)\s\((.+)\)", re.DOTALL)
            for full_state in full_states:
                m = p.match(full_state)
                state = m.group(1)
                desc = m.group(2)
                self.create_state(state, desc)
                self.set(state)
        else:
            if state != "UNKNOWN":
                self.create_state(state)
                self.set(state)

    def __str__(self):
        return self.current_states()

    def __repr__(self):
        return "AxisState: %s" % self.__str__()

    def __contains__(self, other):
        if isinstance(other, str):
            if not self._current_states:
                return other == "UNKNOWN"
            return other in self._current_states
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, str):
            warnings.warn("Use: **%s in state** instead" % other, DeprecationWarning)
            return self.__contains__(other)
        elif isinstance(other, AxisState):
            return set(self._current_states) == set(other._current_states)
        else:
            return NotImplemented

    def new(self, share_states=True):
        """
        Create a new AxisState which contains the same possible states but no
        current state.

        If this AxisState contains custom states and *share_states* is True
        (default), the possible states are shared with the new AxisState.
        Otherwise, a copy of possible states is created for the new AxisState.

        Keyword Args:
            share_states: If this AxisState contains custom states and
                          *share_states* is True (default), the possible states
                          are shared with the new AxisState. Otherwise, a copy
                          of possible states is created for the new AxisState.

        Return:
            AxisState: a copy of this AxisState with no current states
        """
        result = AxisState()
        if self._has_custom_states() and not share_states:
            result._state_desc = self._state_desc.copy()
        else:
            result._state_desc = self._state_desc
        return result


class ModuloAxis(Axis):
    def __init__(self, *args, **kwargs):
        Axis.__init__(self, *args, **kwargs)

        self._modulo = self.config.get("modulo", float)
        self._in_prepare_move = False

    def __calc_modulo(self, pos):
        return pos % self._modulo

    @property
    def dial(self):
        d = super(ModuloAxis, self).dial
        if self._in_prepare_move:
            return d
        else:
            return self.__calc_modulo(d)

    @dial.setter
    def dial(self, value):
        super(ModuloAxis, self.__class__).dial.fset(self, value)
        return self.dial

    def get_motion(self, user_target_pos, *args, **kwargs):
        user_target_pos = self.__calc_modulo(user_target_pos)
        self._in_prepare_move = True
        try:
            return Axis.get_motion(self, user_target_pos, *args, **kwargs)
        finally:
            self._in_prepare_move = False


class NoSettingsAxis(Axis):
    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        for setting_name in self.settings.setting_names:
            self.settings.disable_cache(setting_name)


class CalcAxis(Axis):
    @property
    def state(self):
        return self.controller.state(self)

    @property
    def hw_state(self):
        return self.controller.hw_state(self)

    def sync_hard(self):
        """Forces an axis synchronization with the hardware"""
        for pseudo in self.controller.pseudos:
            if pseudo.is_moving:
                return

        self.controller.sync_hard()

    def update_position(self):
        deprecated_warning(
            kind="method",
            name="update_position",
            replacement="sync_hard",
            reason="for homogeneity reasons",
            since_version="1.11",
            skip_backtrace_count=5,
            only_once=False,
        )
        return self.sync_hard()

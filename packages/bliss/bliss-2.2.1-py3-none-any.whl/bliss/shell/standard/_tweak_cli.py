# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Tweak command-line tool to adjust position of motors with keypad.

Example:
  DEMO [2]: mm2.tw()

    NAME      POSITION     START POS     STEP_SIZE
  -------------------------------------------------
  ▶ mm2   244.41185 mm   (241.41185)  [step size=1]
    [COUNT] [count time=1 s]

Example:
  DEMO [4]: tweak_cli(mm2, mm3, counter=diot)
  INFO: starting Scan(name=ct, path='not saved')
                  diot  =       47.3727      (      47.3727       /s)  simulation_diode_sampling_controller
  INFO: starting Scan(name=ct, path='not saved')
                  diot  =       51.3161      (      51.3161       /s)  simulation_diode_sampling_controller

    NAME      POSITION     START POS     STEP_SIZE
  -------------------------------------------------
  ▶ mm2   244.41185 mm   (241.41185)  [step size=1]
    mm3   -17.43234 nm   (-17.43234)  [step size=1]
    [count time=1 s] [COUNT]
"""

from __future__ import annotations

from bliss.common.logtools import disable_print

from bliss.shell.standard import mv, mvr
from bliss.shell.standard import text_block
from bliss.common.utils import (
    typecheck,
    custom_error_msg,
    shorten_signature,
)
from bliss.common.types import _scannable_or_name


# TODO: Define default step size depending on motor ? or provided by user? how ?
# TODO: Print limits ?
# TODO: Properly capture Ctrl-c -> try (not bind)
# TODO: Properly capture ValueError on move to avoid to quit on limit error.
# TODO: less verbose count ? how ? select a single counter to monitor ?
#       remove " INFO : starting Scan(name=ct, path='not saved')"
# TODO: allow MG as count argument
# TODO: param for a function to be executed after move or on demand ?


def print_help(params):
    print("tweak_cli(axis* [, counter=cnt] [, exp=0.1]) usage:")
    print("                + - : increase/decrease step size of selected motor by 10%")
    print("                * / : multiply / divide step size of selected motor by 2")
    print("                  = : restore default step size of selected motor")
    print("                ← → : move selected motor")
    print("                ↑ ↓ : change selected motor (indicated by the marck: ▶)")
    print("        PgUp⇞ PgDn⇟ : multiply / divide count time by 2")
    print("                  b : move Back all motors to start positions")
    print("                  c : Count After Move on/off")
    print("          esc 🅀  🅇  : Quit")
    print("               ? 🄷  : Help")
    print("")


# TODO: signature for counter
@custom_error_msg(
    TypeError,
    "intended usage: tweak_cli(axis1, axis2, ... ) Hint:",
    display_original_msg=True,
)
@shorten_signature(annotations={"axes": "axis1, axis2, ... "}, hidden_kwargs=[])
@typecheck
def tweak_cli(*axes: _scannable_or_name, counter=None, exp=1):
    """
    Tweak command: allow a quick and accurate adjustment of the position of
    one or more motors via keyboard keys.
    """
    axes = list(axes)

    params = {
        "CAM": True,  # Count after move
        "count_time": exp,
        "counter": counter,
        "start_pos": dict.fromkeys(axes),
        "step_inc": dict.fromkeys(axes, 1.1),
        "step_size": dict.fromkeys(axes, 1),
        "default_step_size": dict.fromkeys(axes, 1),
        "mot_idx": 1,
        "selected_axis": axes[0],
    }

    def after_move():
        """
        Action(s) to do after a move (ex: a count)
        """
        from bliss.common.scans import ct

        nonlocal params

        if params["CAM"]:
            if params["counter"] is not None:
                ct(params["count_time"], params["counter"])
            else:
                ct(params["count_time"])

    def render():
        """
        Build the prompt to display:
        * one line per axis
        * one line for status parameter: COUNT
        ex:
          ▶ mm1 15.2524 parsec    [step size=1] (start pos)
            mm2     211.433 mm    [step size=1] ()
            [COUNT] [count time=1 s]
        """
        nonlocal params
        nonlocal axes

        cam = "COUNT" if params["CAM"] else ""
        # verb = "VERBOSE" if params["verbose"] else ""
        # sep = " | " if params["CAM"] and params["verbose"] else ""

        name_length = params["max_name_length"]
        pos_length = params["max_pos_and_unit_length"] + 2

        #### axes status_line
        status_line = ""

        # headers
        status_line += f"  {'NAME':>{name_length}} {'POSITION':>{pos_length}} {'START POS':>{pos_length}}     STEP_SIZE\n"
        status_line += "-" * (name_length + pos_length * 2 + 20)
        status_line += "\n"

        # mot lines
        for idx, axis in enumerate(axes):
            mot_unit = (" " + axis.unit) if axis.unit else ""
            step = params["step_size"][axis]
            spos = params["start_pos"][axis]
            mark = "  "
            if params["mot_idx"] == idx + 1:
                mark = "▶ "
            pos = f"{axis.position:.{axis.display_digits}f}{mot_unit}"
            start_pos = f"({spos})"
            status_line += f"{mark}{axis.name:>{name_length}} "
            status_line += f" {pos:>{pos_length}}"
            status_line += f" {start_pos:>{pos_length}}"
            status_line += f"  [step size={step:g}]\n"

        # common status_line
        count_t = f"[count time={params['count_time']:.4g} s]" if params["CAM"] else ""
        status_line += f"  [{cam}] {count_t} "

        status_lines_count = len(axes) + 3

        return status_lines_count, status_line

    # Check parameters: number of axes.
    if not axes:
        print("")
        print_help(params)
        return

    # Get fields sizes
    max_name_length = 0
    max_pos_and_unit_length = 0

    for axis in axes:
        params["start_pos"][axis] = axis.position
        max_name_length = max(max_name_length, len(axis.name))
        unit_len = len(axis.unit) if axis.unit else 0
        max_pos_and_unit_length = max(
            max_pos_and_unit_length,
            unit_len + len(f"{axis.position:.{axis.display_digits}f}"),
        )

    params["max_name_length"] = max_name_length
    params["max_pos_and_unit_length"] = max_pos_and_unit_length

    k_list = ["escape", "pageup", "pagedown", "up", "down", "left", "right"]
    k_list.extend(["+", "-", "*", "/", "=", "?"])
    k_list.extend(["b", "c", "x", "q", "h"])
    k_list.extend(["B", "C", "X", "Q", "H"])

    # Treat received events.
    tips = "[Q]uit  [H]elp"
    with text_block(render, key_bindings=k_list, extra_status_bar=tips) as tblock:
        while True:
            key = tblock.wait_key_pressed().lower()

            if key in ["h", "?"]:
                print_help(params)
            elif key in ["x", "q", "escape", "c-c"]:
                break

            elif key == "b":
                print("Move back all axes to start position")
                with disable_print():
                    for axis in axes:
                        mv(axis, params["start_pos"][axis])

            # UP DOWN to select axis
            elif key == "up":
                smi = params["mot_idx"]
                smi -= 1
                if smi < 1:
                    smi = len(axes)
                params["mot_idx"] = smi  # 1..N
                params["selected_axis"] = axes[smi - 1]
            elif key == "down":
                smi = params["mot_idx"]
                smi += 1
                if smi > len(axes):
                    smi = 1
                params["mot_idx"] = smi  # 1..N
                params["selected_axis"] = axes[smi - 1]

            # 'c'ount  'v'erbose
            elif key == "c":
                params["CAM"] = not params["CAM"]
            elif key == "pageup":
                params["count_time"] *= 2
            elif key == "pagedown":
                params["count_time"] /= 2

            # step size
            elif key == "+":
                params["step_size"][params["selected_axis"]] *= params["step_inc"][
                    params["selected_axis"]
                ]
            elif key == "-":
                params["step_size"][params["selected_axis"]] /= params["step_inc"][
                    params["selected_axis"]
                ]
            elif key == "*":
                params["step_size"][params["selected_axis"]] *= 2
            elif key == "/":
                params["step_size"][params["selected_axis"]] /= 2
            elif key == "=":
                params["step_size"][params["selected_axis"]] = params[
                    "default_step_size"
                ][params["selected_axis"]]

            # move selected axis
            elif key == "left":
                # axis = axes[0]
                axis = params["selected_axis"]
                with disable_print():
                    mvr(axis, -params["step_size"][axis])
                after_move()

            elif key == "right":
                # axis = axes[0]
                axis = params["selected_axis"]
                with disable_print():
                    mvr(axis, params["step_size"][axis])
                after_move()

            else:
                print("Unhandled key: {key}")

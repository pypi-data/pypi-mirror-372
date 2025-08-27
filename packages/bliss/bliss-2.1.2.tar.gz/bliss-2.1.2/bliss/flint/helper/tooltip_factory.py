# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
import numbers


class TooltipFactory:

    _STYLE = 'style="width: 100%; margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; border-collapse: collapse"'

    _STYLE_PAD = 'style="padding-left: 0.1em;"'

    def __init__(self):
        self.__text = ""

    def isEmpty(self) -> bool:
        return self.__text == ""

    def addTitle(self, label: str, pre: str | None = None):
        if pre is None:
            pre = ""
        self.__text += f'<tr><td style="padding-right: 0.1em;">{pre}</td><td colspan="4"><b>{label}</b></td></tr>'

    def addQuantity(
        self,
        label: str,
        value: str | numbers.Integral | numbers.Real,
        unit: str | None = None,
        pre: str | None = None,
        ndigits: int = 3,
    ):
        if unit is None:
            unit = " "
        if pre is None:
            pre = " "
        if isinstance(value, numbers.Integral):
            part1 = str(value)
            part2 = ""
        elif isinstance(value, numbers.Real):
            text = f"{value:.{ndigits}f}"
            parts = text.split(".")
            part1 = parts[0]
            if len(parts) > 1:
                part2 = f"{parts[1]}"
            else:
                part2 = ""
        else:
            part1 = str(value)
            part2 = None

        if part2 is None:
            formatted = f'<td align="right" colspan="3" style="padding-left: 0.1em;">{part1}</td>'
        else:
            # NOTE: A normal dot char can be wrapped sometimes despirte the use of nowrap
            if part2 == "":
                dot = ""
            else:
                dot = "<sub><b>⋅</b></sub>"
            formatted = f'<td align="right" style="padding-left: 0.1em;">{part1}</td><td align="left">{dot}{part2}</td>'
        self.__text += f'<tr><td style="padding-right: 0.1em;">{pre}</td><td><b>{label}</b></td>{formatted}<td {self._STYLE_PAD}>{unit}</td></tr>'

    def addSeparator(self):
        self.__text += '<tr><td style="font-size:1px" colspan="5"><hr /></td></tr>'

    def text(self):
        return f"<table {self._STYLE}>{self.__text}</table>"

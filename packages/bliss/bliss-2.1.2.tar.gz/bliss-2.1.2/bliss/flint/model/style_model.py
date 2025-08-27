# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""This module provides object to model styles.
"""

from __future__ import annotations
from typing import NamedTuple

import enum


class DescriptiveValue(NamedTuple):
    """Allow to describe value of the enums"""

    code: object
    name: str


class DescriptiveEnum(enum.Enum):
    @classmethod
    def fromCode(classobject, code: object):
        for value in classobject:
            if value.value == code:
                return value
            elif isinstance(value.value, DescriptiveValue):
                if value.code == code:
                    return value
        raise ValueError(
            "Value %s not part of the enum %s" % (code, classobject.__name__)
        )

    @property
    def code(self):
        if isinstance(self.value, DescriptiveValue):
            return self.value.code
        raise AttributeError()


class FillStyle(DescriptiveEnum):
    NO_FILL = DescriptiveValue(None, "No fill")
    SCATTER_INTERPOLATION = DescriptiveValue("scatter-interpolation", "Interpolation")
    SCATTER_REGULAR_GRID = DescriptiveValue("scatter-regular-grid", "Regular grid")
    SCATTER_IRREGULAR_GRID = DescriptiveValue(
        "scatter-irregular-grid", "Irregular grid"
    )


class LineStyle(DescriptiveEnum):
    NO_LINE = DescriptiveValue(None, "No line")
    SCATTER_SEQUENCE = DescriptiveValue("scatter-sequence", "Sequence of points")


class SymbolStyle(DescriptiveEnum):
    NO_SYMBOL = DescriptiveValue(None, "No symbol")
    CIRCLE = DescriptiveValue("o", "Circle")
    PLUS = DescriptiveValue("+", "Plus")
    CROSS = DescriptiveValue("x", "Cross")
    POINT = DescriptiveValue(".", "Point")


class IndexedColor:
    def color(self) -> tuple[int, int, int]:
        raise NotImplementedError


class _Style(NamedTuple):
    lineStyle: str | LineStyle | None
    lineColor: tuple[int, int, int] | IndexedColor | None
    linePalette: int | None
    lineWidth: float | None
    symbolStyle: str | SymbolStyle | None
    symbolSize: float | None
    symbolColor: tuple[int, int, int] | None
    colormapLut: str | None
    fillStyle: str | FillStyle | None


class Style(_Style):
    def __new__(
        cls,
        lineStyle: str | LineStyle | None = None,
        lineColor: tuple[int, int, int] | IndexedColor | None = None,
        linePalette: int | None = None,
        lineWidth: float | None = None,
        symbolStyle: str | SymbolStyle | None = None,
        symbolSize: float | None = None,
        symbolColor: tuple[int, int, int] | None = None,
        colormapLut: str | None = None,
        fillStyle: str | FillStyle | None = None,
        style: Style | None = None,
    ):
        if style is not None:
            if lineStyle is None:
                lineStyle = style.lineStyle
            if lineColor is None:
                lineColor = style.lineColor
            if linePalette is None:
                linePalette = style.linePalette
            if lineWidth is None:
                lineWidth = style.lineWidth
            if symbolStyle is None:
                symbolStyle = style.symbolStyle
            if symbolSize is None:
                symbolSize = style.symbolSize
            if symbolColor is None:
                symbolColor = style.symbolColor
            if colormapLut is None:
                colormapLut = style.colormapLut
            if fillStyle is None:
                fillStyle = style.fillStyle

        try:
            symbolStyle = SymbolStyle.fromCode(symbolStyle)
        except ValueError:
            pass

        try:
            lineStyle = LineStyle.fromCode(lineStyle)
        except ValueError:
            pass

        try:
            fillStyle = FillStyle.fromCode(fillStyle)
        except ValueError:
            pass

        return super().__new__(
            cls,
            lineStyle=lineStyle,
            lineColor=lineColor,
            linePalette=linePalette,
            lineWidth=lineWidth,
            symbolStyle=symbolStyle,
            symbolSize=symbolSize,
            symbolColor=symbolColor,
            colormapLut=colormapLut,
            fillStyle=fillStyle,
        )

    @property
    def lineColor(self):
        lineColor = super(Style, self).lineColor
        if lineColor is None:
            return None
        if isinstance(lineColor, tuple):
            return lineColor
        return lineColor.color()


def symbol_to_silx(value: str | SymbolStyle | None):
    if value is None or value == SymbolStyle.NO_SYMBOL:
        return " "
    if isinstance(value, SymbolStyle):
        return value.code
    return str(value)

# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Compatibility layer over pickle to deal with renamed modules
"""

from __future__ import annotations

import pickle
import io


_MODULE_MAPPING: dict[tuple[str, str], tuple[str, str]] = {
    # Flint < 0.14
    ("bliss.flint.widgets.plot_helper", "PlotConfiguration"): (
        "bliss.flint.widgets.viewer.viewer_configuration",
        "ViewerConfiguration",
    ),
    # Flint < 2.0
    ("bliss.flint.widgets.utils.plot_helper", "PlotConfiguration"): (
        "bliss.flint.widgets.viewer.viewer_configuration",
        "ViewerConfiguration",
    ),
}


class _Unpickler(pickle.Unpickler):
    """Compatibility layer to unpickle old objects"""

    def find_class(self, module_name: str, class_name: str):
        module_def = _MODULE_MAPPING.get((module_name, class_name), None)
        if module_def is not None:
            module_name, class_name = module_def
        return pickle.Unpickler.find_class(self, module_name, class_name)


def loads(data: bytes) -> object:
    return _Unpickler(io.BytesIO(data)).load()


def dumps(obj: object) -> bytes:
    return pickle.dumps(obj)

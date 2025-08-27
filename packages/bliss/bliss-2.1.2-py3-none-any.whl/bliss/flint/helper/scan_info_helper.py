# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides helper to read scan_info.
"""
from __future__ import annotations

from ..model import scan_model
from ..model import plot_model


def removed_same_plots(plots, remove_plots) -> list[plot_model.Plot]:
    """Returns plots from an initial list of `plots` in which same plots was
    removed."""
    if remove_plots == []:
        return list(plots)
    result = []
    for p in plots:
        for p2 in remove_plots:
            if p.hasSameTarget(p2):
                break
        else:
            result.append(p)
            continue
    return result


def get_full_title(scan: scan_model.Scan | None) -> str:
    """Returns from scan_info a readable title"""
    if scan is None:
        return "No scan"
    scan_info = scan.scanInfo()
    if scan_info is None:
        return "No scan title"
    title = scan_info.get("title", "No scan title")
    scan_nb = scan_info.get("scan_nb", None)
    if scan_nb is not None:
        text = f"{title} (#{scan_nb})"
    else:
        text = f"{title}"
    return text

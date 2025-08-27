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
from bliss.flint.model import scan_model


_SCAN_CATEGORY = {
    None: "unknown",
    # A single measurement
    "ct": "point",
    # Many measurements
    "timescan": "nscan",
    "loopscan": "nscan",
    "lookupscan": "nscan",
    "pointscan": "nscan",
    "ascan": "nscan",
    "a2scan": "nscan",
    "a3scan": "nscan",
    "a4scan": "nscan",
    "anscan": "nscan",
    "dscan": "nscan",
    "d2scan": "nscan",
    "d3scan": "nscan",
    "d4scan": "nscan",
    "dnscan": "nscan",
    "limatake": "nscan",
    # Many measurements using 2 correlated axes
    "amesh": "mesh",
    "dmesh": "mesh",
}


def get_scan_category(
    scan_info: dict | None = None, scan_type: str | None = None
) -> str | None:
    """
    Returns a scan category for the given scan_info.

    Returns:
        One of "point", "nscan", "mesh" or None if nothing matches.
    """
    if scan_info is not None:
        scan_type = scan_info.get("type", None)
    return _SCAN_CATEGORY.get(scan_type, None)


def parse_features(scan_info: dict) -> scan_model.ScanFeatures:
    scan_type = scan_info.get("type", None)
    npoints = scan_info.get("npoints", None)
    flags = scan_model.ScanFeatures.NONE
    if scan_type == "timescan":
        flags = flags | scan_model.ScanFeatures.INFINITY_SCAN
    if npoints == 0:
        flags = flags | scan_model.ScanFeatures.INFINITY_SCAN

    category = _SCAN_CATEGORY.get(scan_type, None)
    if category == "point":
        flags = flags | scan_model.ScanFeatures.DEFAULT_POINT
    if category == "nscan":
        flags = flags | scan_model.ScanFeatures.DEFAULT_NSCAN
    if category == "mesh":
        flags = flags | scan_model.ScanFeatures.DEFAULT_MESH

    return flags

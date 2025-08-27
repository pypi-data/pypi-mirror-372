# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Business function when a curve plot is updated from a new scan.
"""

from __future__ import annotations

from bliss.flint.model import plot_model
from bliss.flint.model import plot_item_model
from bliss.flint.model import scan_model
from bliss.flint.helper import model_helper


def resolveCurvePlotUpdate(
    previousScan: scan_model.Scan | None,
    previousPlot: plot_model.Plot | None,
    newScan: scan_model.Scan,
    newPlot: plot_model.Plot,
) -> plot_model.Plot:
    """Resolve the merge between the previous plot and the new plot using
    business constraints

    Returns the plot to use. This can be a new plot instance or one passed by
    argument, which was edited, or not.
    """
    display_extra = newScan.scanInfo().get("display_extra", {})

    if previousScan is not None:
        useDefaultPlot = display_extra.get("displayed_channels", None) is not None
    else:
        useDefaultPlot = True

    if (
        previousScan is not None
        and previousPlot is not None
        and previousPlot.xaxisEditSource() == "user"
    ):
        xaxes = model_helper.getMostUsedXChannelPerMasters(previousScan, previousPlot)
    else:
        xaxes = None

    if useDefaultPlot or previousPlot is None:
        pass
    else:
        userEditTime = previousPlot.userEditTime()
        # FIXME: It would be good to hide this parsing
        scanPlotselectTime = display_extra.get("plotselect_time", None)
        if userEditTime is not None:
            if scanPlotselectTime is None or userEditTime > scanPlotselectTime:
                counterLocked = True
            else:
                counterLocked = False
        else:
            counterLocked = False

        if counterLocked:
            with newPlot.transaction():
                selection = model_helper.getChannelNamesDisplayedAsValue(previousPlot)
                model_helper.updateDisplayedChannelNames(
                    newPlot, newScan, selection, ignoreMissingChannels=True
                )
                model_helper.reorderDisplayedItems(newPlot, selection)
                model_helper.copyItemsFromChannelNames(previousPlot, newPlot, newScan)
        else:
            # Only update the config (don't create new curve items)
            with previousPlot.transaction():
                # Clean up temporary items
                for item in list(previousPlot.items()):
                    if isinstance(item, plot_model.NotReused):
                        try:
                            previousPlot.removeItem(item)
                        except Exception:
                            pass

                # Reuse only available values
                # FIXME: Make it work first for curves, that's the main use case
                if isinstance(previousPlot, plot_item_model.CurvePlot):
                    model_helper.copyItemsFromChannelNames(
                        previousPlot, newPlot, newScan
                    )

    # Finally protect against missing channels
    model_helper.discardMissingChannels(newPlot, newScan)

    model_helper.selectSomethingToPlotIfNone(newPlot, newScan)

    if xaxes:
        model_helper.updateXAxisPerMasters(newScan, newPlot, xaxes)

    if previousPlot:
        previousPlot.copyEditTags(newPlot)

    return newPlot

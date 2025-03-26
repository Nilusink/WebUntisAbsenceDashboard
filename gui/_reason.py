"""
gui/_reason.py

Project: WebUntisAbsenceDashboard
"""

from __future__ import annotations
from typing import Any
from matplotlib.container import BarContainer

from analysis import Analysis

from ._ctk_figure import CTkFigure


##################################################
#                     Code                       #
##################################################

class ReasonCompact(CTkFigure):
    """
    bar plot showing the most used absence reasons
    """

    _bar_container: BarContainer | None = None

    def _plot(self) -> None:
        """
        Create bar-plot showcasing the most used absence reasons
        """

        reasons: dict[str, int] = {}
        for person in Analysis.all_data:
            for absence in person:
                # if not in reasons yet, create
                if absence["Reason of absence"] not in reasons:
                    reasons[absence["Reason of absence"]] = 0

                # increase reason count by 1
                reasons[absence["Reason of absence"]] += 1

        # sort by most used
        reason_strings = sorted(reasons.keys(), key=lambda x: reasons[x], reverse=True)
        reason_values = [reasons[r] for r in reason_strings]

        # plot graph
        if self._bar_container:
            del self._bar_container
        self._bar_container = self._ax.bar(reason_strings, reason_values)
        self._ax.set_xticks(range(len(reason_strings)))  # Set tick positions
        self._ax.set_xticklabels(reason_strings, rotation=45, ha="right")  # Set tick labels
        self._ax.set_title("Reasons of Absence")

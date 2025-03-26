"""
gui/_dashboard.py

Project: WebUntisAbsenceDashboard
"""

from customtkinter import CTkFrame
from typing import Any, Callable, Literal

from ._time_absence import TimeAbsenceCompact
from ._heatmap import HeatmapCompact
from ._reason import ReasonCompact


##################################################
#                     Code                       #
##################################################

DashboardElements = Literal["TimeAbsence"]


class Dashboard(CTkFrame):
    """
    Dashboard-Frame containing compact graphs
    """
    __time_absence_compact: TimeAbsenceCompact
    __reason_compact: ReasonCompact
    __heatmap_compact: HeatmapCompact

    __callback_open: Callable[[DashboardElements], Any]

    def __init__(self, master: Any, callback_open: Callable[[DashboardElements], Any]) -> None:
        super().__init__(master)

        self.__callback_open = callback_open

        self.__time_absence_compact = TimeAbsenceCompact(self)
        self.__reason_compact = ReasonCompact(self)
        self.__heatmap_compact = HeatmapCompact(self)

        self.__time_absence_compact.bind("<Button-1>", lambda e: self.__callback_open("TimeAbsence"))


        self.__time_absence_compact.grid(row=0, column=0, columnspan=2, sticky="NSEW", padx=25, pady=25)
        self.__reason_compact.grid(row=1, column=0, sticky="NSEW", padx=25, pady=25)
        self.__heatmap_compact.grid(row=1, column=1, sticky="NSEW", padx=25, pady=25)

        self.grid_columnconfigure("all", weight=1)
        self.grid_rowconfigure("all", weight=1)

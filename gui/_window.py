"""
gui/_window.py

Project: WebUntisAbsenceDashboard
"""

from typing import Any

from analysis import Analysis
from constants import DATA_DIR

from ._dashboard import Dashboard, DashboardElements
from ._time_absence import TimeAbsenceFull
from ._dnd_ctk import DragNDropCTk


##################################################
#                     Code                       #
##################################################

class Window(DragNDropCTk):
    """
    CTk with Drag and Drop functionality
    """

    __dashboard: Dashboard

    __time_absence_full: TimeAbsenceFull

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Init CTk-Window with Drag and Drop functionality

        :param args: Additional positional arguments to be passed to the superclass initializer.
        :param kwargs: Additional keyword arguments to be passed to the superclass initializer.
        """
        super().__init__(DATA_DIR, self.__on_drop, *args, **kwargs)

        self.__dashboard = Dashboard(self, self.open)
        self.__time_absence_full = TimeAbsenceFull(self)
        self.__dashboard.pack(fill="both", expand=True)

        self.title("WebUntisAbsenceDashboard")
        self.geometry(f"{self.winfo_screenwidth() // 2}x{self.winfo_screenheight() // 2}")
        self.after(1, lambda: self.state("zoom"))

    def __on_drop(self, files: list[str]) -> None:
        Analysis.reload()

    def open(self, element: DashboardElements) -> None:
        print("OPEN", element)
        if element == "TimeAbsence":
            self.__time_absence_full.pack(fill="both", expand=True)

        self.__dashboard.pack_forget()

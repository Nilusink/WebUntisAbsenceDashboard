"""
gui/_ctk_graph.py

Project: WebUntisAbsenceDashboard
"""

from typing import Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from customtkinter import CTkFrame

from analysis import Analysis


##################################################
#                     Code                       #
##################################################

class _ColoredFigure(Figure):
    """
    A matplotlib Figure themed like customtkinter
    """
    _BG_COLOR: str = "#2B2B2B"
    _TEXT_COLOR: str = "#FFFFFF"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.patch.set_facecolor(self._BG_COLOR)

    def add_subplot(self, *args, **kwargs) -> Axes:  # noqa
        subplot: Axes = super().add_subplot(*args, **kwargs)
        subplot.set_facecolor(self._BG_COLOR)
        subplot.tick_params(colors=self._TEXT_COLOR)
        for spine in subplot.spines.values():
            spine.set_color(self._TEXT_COLOR)

        # Replace legend method
        _original_legend = subplot.legend

        def custom_legend(*args: Any, **kwargs: Any) -> Any:
            legend_obj = _original_legend(*args, **kwargs)
            legend_obj.get_frame().set_facecolor(self._BG_COLOR)
            for text in legend_obj.get_texts():
                text.set_color(self._TEXT_COLOR)
            return legend_obj

        subplot.legend = custom_legend

        # Replace grid method
        _original_grid = subplot.grid

        def custom_grid(*args: Any, **kwargs: Any):
            kwargs["color"] = kwargs.get("color", self._TEXT_COLOR)
            return _original_grid(*args, **kwargs)

        subplot.grid = custom_grid

        # Replace set_title
        _original_set_title = subplot.set_title

        def custom_set_title(label, fontdict=None, loc=None, pad=None, *, y=None, **kwargs):
            kwargs["color"] = kwargs.get("color", self._TEXT_COLOR)
            return _original_set_title(label, fontdict, loc, pad, y=y, **kwargs)

        subplot.set_title = custom_set_title

        return subplot


class CTkFigure(CTkFrame):
    """
    Matplotlib Figure for Customtkinter with automatic layout adjustment
    """
    _SHOW_TOOLBAR: bool = False

    _fig: _ColoredFigure
    _ax: Axes
    __canvas: FigureCanvasTkAgg

    _BG_COLOR: str = "#2B2B2B"
    _TEXT_COLOR: str = "#FFFFFF"

    def __init__(self, master: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(master)
        # Enable automatic layout adjustments
        kwargs["constrained_layout"] = True
        self._fig = _ColoredFigure(*args, **kwargs)
        self._ax = self._fig.add_subplot()

        self.__canvas = FigureCanvasTkAgg(self._fig, master=self)
        # Now pack the canvas widget
        self.__canvas.get_tk_widget().pack(fill="both", expand=True)

        if self._SHOW_TOOLBAR:
            self.toolbar = NavigationToolbar2Tk(self.__canvas, self)
            self.toolbar.update()
            self.toolbar.pack(side="top", fill="x")

        Analysis.add_reload(self.reload)
        self.reload()

    def _plot(self) -> None:
        """
        Reload the plot. Overwrite this method!
        """
        ...

    def reload(self) -> None:
        self._plot()
        self.__canvas.draw()

    def bind(self, sequence=None, command=None, add=True):
        self.__canvas.get_tk_widget().bind(sequence, command, add)

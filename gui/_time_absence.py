"""
gui/_time_absence.py

Project: WebUntisAbsenceDashboard
"""

from typing import Any

from analysis import Analysis
from constants import EXCUSE_STATUS
from time_corrector import ExcuseStatus

from ._ctk_figure import CTkFigure

from tkinter import Frame


##################################################
#                     Code                       #
##################################################

class TimeAbsenceCompact(CTkFigure):
    """
    Plot a person's absence while keeping track of which names are already displayed.
    """
    _plot_lines: dict

    def __init__(self, master: Any, *args: Any, **kwargs: Any) -> None:
        self._plot_lines = {}

        super().__init__(master, *args, **kwargs)

    def _plot(self) -> None:
        # Gather new names from Analysis.time_data
        new_names = {name for _, _, name in Analysis.time_data}
        current_names = set(self._plot_lines.keys())

        # Remove lines for names not present anymore
        for name in current_names - new_names:
            self._plot_lines[name].remove()
            del self._plot_lines[name]

        # Build a mapping from name to its total absence time.
        # Assumes Analysis.time_data and Analysis.total_times are parallel.
        total_time_by_name = {name: total for (_, _, name), total in zip(Analysis.time_data, Analysis.total_times)}

        # Update existing lines or create new ones
        for xs, ys_cumm, name in Analysis.time_data:
            if name in self._plot_lines:
                self._plot_lines[name].set_data(xs, ys_cumm)
            else:
                new_line, = self._ax.step(xs, ys_cumm, label=name, where="post")
                self._plot_lines[name] = new_line

        # Update legend sorted by total absence time (descending)
        sorted_names = sorted(self._plot_lines.keys(), key=lambda n: total_time_by_name.get(n, 0), reverse=True)
        sorted_handles = [self._plot_lines[name] for name in sorted_names]
        self._ax.legend(sorted_handles, sorted_names, loc='center left', bbox_to_anchor=(1, 0.5))

        self._ax.grid(alpha=0.3)

        # Set title based on excuse status
        if EXCUSE_STATUS == ExcuseStatus.both:
            title = "Total absences"
        elif EXCUSE_STATUS == ExcuseStatus.excused:
            title = "Excused absences"
        else:
            title = "Unexcused absences"

        try:
            self._ax.set_title(f"{title} (AVG: {sum(Analysis.total_times) / len(Analysis.total_times):.2f})")
        except ZeroDivisionError:
            self._ax.set_title(title)

        # Add hover annotation
        if not hasattr(self, '_hover_text'):
            self._hover_text = self._ax.annotate(
                "", xy=(0, 0), xytext=(0, 0), textcoords="data",
                bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->")
            )
            self._hover_text.set_visible(False)
            self._ax.figure.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def on_hover(self, event: Any) -> None:
        """
        Display the name of the line at the current mouse position.
        """
        ...


class TimeAbsenceFull(TimeAbsenceCompact):
    """
    Time absence plot view toolbar and name on hover
    """
    _SHOW_TOOLBAR = True

    def on_hover(self, event: Any) -> None:
        """
        Display the name of the line at the current mouse position.
        """
        if event.inaxes != self._ax:
            self._hover_text.set_visible(False)
            self._ax.figure.canvas.draw_idle()
            return

        visible = False
        for line in self._plot_lines.values():
            contains, _ = line.contains(event)
            if contains:
                self._hover_text.set_text(line.get_label())
                # Place annotation exactly at the mouse data coordinates
                self._hover_text.xy = (event.xdata, event.ydata)
                self._hover_text.set_position((event.xdata, event.ydata))
                self._hover_text.set_visible(True)
                visible = True
                break

        if not visible:
            self._hover_text.set_visible(False)
        self._ax.figure.canvas.draw_idle()

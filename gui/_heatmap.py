"""
gui/_reason.py

Project: WebUntisAbsenceDashboard
"""

from typing import Any

from matplotlib import ticker
from matplotlib.container import BarContainer

from analysis import Analysis
from gui._ctk_figure import CTkFigure
from time_corrector import TIME_PERIODS


##################################################
#                     Code                       #
##################################################

class HeatmapCompact(CTkFigure):
    """
    Creates a heatmap showing what periods where absent the most
    """

    __bars: list[BarContainer] = []

    def __init__(self, master: Any, *args, **kwargs) -> None:
        super().__init__(master, *args, **kwargs)

        self._ax.invert_yaxis()

    def _plot(self) -> None:
        periods_per_day = {i: {j: 0 for j in range(len(TIME_PERIODS))} for i in range(5)}

        # parse all data and assign to correct period
        for person in Analysis.all_data:
            for absence in person:
                weekday = absence["start"].weekday()
                start_time = absence["start"].time()
                end_time = absence["end"].time()

                for i, period in enumerate(TIME_PERIODS):

                    # check for overlaps
                    try:
                        if max(start_time, period[0]) < min(end_time, period[1]):
                            periods_per_day[weekday][i] += 1

                    except KeyError:
                        print(f"Invalid absence: {absence['start'].strftime("%A, %b %d, %Y, %I:%M %p")}")

        # period with maximum number of absences (for color)
        max_per_period = max([periods_per_day[day][period] for day in periods_per_day for period in periods_per_day[day]])

        # define weekdays for use in heatmap
        days = ["Mon", "Tue", "Wed", "Thur", "Fri"]

        for bar_container in self.__bars:
            del bar_container
        self.__bars = []

        for i, day in enumerate(days):
            for p in range(len(TIME_PERIODS)):
                period = periods_per_day[i][p]

                self.__bars.append(self._ax.bar(
                    [day,],
                    [50,],
                    bottom=60*TIME_PERIODS[p][0].hour + TIME_PERIODS[p][0].minute,
                    color=self.__color_gradient(period, max_per_period) if period > 0 else self._BG_COLOR
                ))

        self._ax.set_title("Absence Heatmap")

        self._ax.yaxis.set_major_formatter(ticker.FuncFormatter(self.minutes_to_time))

    @staticmethod
    def __color_gradient(value: float, max_value: float) -> tuple[float, float, float]:
        """
        Maps a value from 0 (green) to max_value (red).

        Parameters:
            value (float): The input value in range [0, max_value]
            max_value (float): The maximum possible value

        Returns:
            (r, g, b) tuple representing the RGB color
        """
        # Ensure value is within bounds
        value = max([0, min(value, max_value)])

        # Compute interpolation ratio (0 = green, 1 = red)
        ratio = value / max_value

        # Interpolate red and green channels
        r = ratio  # Red increases
        g = (1 - ratio)  # Green decreases
        b = 0  # No blue in the gradient

        return r, g, b

    def minutes_to_time(self, x, pos):
        # Convert minutes from 12:00 to clock time.
        # 0 minutes = 12:00, 60 = 13:00, etc.
        total_minutes = int(x)
        hour = (total_minutes // 60) % 24
        minute = total_minutes % 60
        return f"{hour:02d}:{minute:02d}"

"""
analysis.py

Project: WebUntisAbsenceDashboard
"""

from datetime import datetime, date, timedelta
from typing import Callable, Any
from os import path

from constants import SEP, CONST_BREAKS, DATA_DIR, EXCUSE_STATUS, FILES
from time_corrector import AbsenceLine, ExcuseStatus, read_csv


class _Analysis:
    __reload_callbacks: list[Callable[[], Any]]

    def __init__(self) -> None:
        self.__reload_callbacks = []

        self.reload()

    def add_reload(self, reload: Callable[[], Any]) -> None:
        self.__reload_callbacks.append(reload)

    def reload(self) -> None:
        # plot absences over time
        total_times = []
        all_data: list[list[AbsenceLine]] = []

        self.time_data = []
        for file in FILES():
            total, data = self.__get_data(
                path.join(DATA_DIR, file),
                EXCUSE_STATUS
            )

            if total > 0:
                total_times.append(total)

            all_data.append(data)

        self.total_times = total_times
        self.all_data = all_data

        for reload_callback in self.__reload_callbacks:
            reload_callback()

    def __get_data(
            self,
            file_path: str,
            status: ExcuseStatus
    ) -> tuple[float, list[AbsenceLine]]:
        """
        plot a persons absence

        :param file_path:  CSV file
        :param status: can be excused, not excused or both
        :return: total absence in school hours
        """
        original_data, corrected = read_csv(file_path, sep=SEP)

        if corrected:
            print(f"file: ", file_path)

        data = []
        delta_data = []
        for line in original_data:
            if status == ExcuseStatus.excused and line["Status"] != "entsch.":
                continue

            elif status == ExcuseStatus.not_excused and line["Status"] != "nicht entsch.":
                continue

            # show all over 1 year
            data.append(line)
            line = line.copy()  # disassociate to not tamper with data permanently
            if line["start"].month > 7:
                if line["start"].year != 2024:
                    line["start"] = line["start"].replace(year=2024)
                    line["end"] = line["end"].replace(year=2024)

            else:
                if line["start"].year != 2025:
                    line["start"] = line["start"].replace(year=2025)
                    line["end"] = line["end"].replace(year=2025)

            delta_data.append(self.__calculate_time(line, in_school_hours=True))

        # sum all data for one day
        new_delta_data = []
        for line in delta_data:
            d, hours_diff = line

            # check if last date is same as new
            if len(new_delta_data) > 0:
                if new_delta_data[-1][0] == d:
                    new_delta_data[-1] = (d, new_delta_data[-1][1] + hours_diff)
                    continue

            # if not, just append
            new_delta_data.append((d, hours_diff))

        # convert to x and y lists
        xs = []
        ys = []
        for line in delta_data:
            d, delta = line

            xs.append(d)
            ys.append(delta)

        # sum all y values
        ys_cumm = self.__cumsum(ys)

        name = (
            f"{original_data[0]['Full name']} "
            f"{original_data[0]['First name']} "
            f"({original_data[0]['Class']}"
        )

        if len(xs) == 0:
            print(f"No \"{status}\" absences for {name})")
            return 0, []

        name += f", {ys_cumm[-1].__ceil__():.0f} h)"

        xs.append(date.today() + timedelta(days=1))
        ys_cumm.append(ys_cumm[-1])

        self.time_data.append((xs, ys_cumm, name))

        return ys_cumm[-1], data

    def __calculate_time(self, line: dict, in_school_hours: bool = True) -> tuple[date, float]:
        """
        calculate the missing time from a line

        :param line: line to calculate
        :param in_school_hours: 60 min or 50 min intervals
        """
        start: datetime = line["start"]
        end: datetime = line["end"]

        # get date
        d = start.date()

        # Compute the difference
        time_diff = end - start

        ## check if there is a break in the specified time frame
        if in_school_hours:
            for b in CONST_BREAKS:
                if start.time() < b[0] <= end.time():
                    time_diff -= b[2]

        hours_diff = time_diff.total_seconds() / 3600

        # convert to 50 min intervals
        if in_school_hours:
            hours_diff = hours_diff * 6/5

        return d, hours_diff

    def __cumsum(self, data: list[float]) -> list[float]:
        """
        convert individual times to total times
        """
        curr_total = 0
        out = []
        for d in data:
            curr_total += d

            out.append(curr_total)

        return out


Analysis = _Analysis()

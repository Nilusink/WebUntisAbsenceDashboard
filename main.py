"""
main.py

Author:
Nilusink
"""
from datetime import datetime, date, time, timedelta
import matplotlib.gridspec as gridspec
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import os

from time_corrector import read_csv, ExcuseStatus, AbsenceLine, TIME_PERIODS


# settings
SEP: str = "\t"
DATA_DIR: str = "./data/"
EXCUSE_STATUS: ExcuseStatus = ExcuseStatus.both
CONST_BREAKS: list[tuple[time, time, timedelta]] = [
    (time(9, 40), time(9, 55), timedelta(minutes=15)),
    (time(11, 35), time(11, 40), timedelta(minutes=5)),
    (time(15, 0), time(15, 15), timedelta(minutes=15))
]


def calculate_time(line: dict, in_school_hours: bool = True) -> tuple[date, float]:
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


def cumsum(data: list[float]) -> list[float]:
    """
    convert individual times to total times
    """
    curr_total = 0
    out = []
    for d in data:
        curr_total += d

        out.append(curr_total)

    return out


def plot_absence(
        file_path: str,
        context: Axes,
        status: ExcuseStatus
) -> tuple[float, list[AbsenceLine]]:
    """
    plot a persons absence

    :param file_path:  CSV file
    :param context: matplotlib context
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

        delta_data.append(calculate_time(line, in_school_hours=True))

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
    ys_cumm = cumsum(ys)

    name = (
        f"{original_data[0]['Full name']} "
        f"{original_data[0]['First name']} "
        f"({original_data[0]['Class']}"
    )

    if len(xs) == 0:
        print(f"No \"{status}\" absences for {name})")
        return 0, []

    name += f", {ys_cumm[-1].__ceil__():.0f} h)"

    # plot graph
    context.step(xs, ys_cumm, label=name, where="pre")

    return ys_cumm[-1], data


def absence_reason(data: list[list[AbsenceLine]], context: Axes) -> None:
    """
    bar plot showing the most used absence reasons
    """
    reasons: dict[str, int] = {}
    for person in data:
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
    context.bar(reason_strings, reason_values)
    context.set_xticks(range(len(reason_strings)))  # Set tick positions
    context.set_xticklabels(reason_strings, rotation=45, ha="right")  # Set tick labels
    context.set_title("Reasons of Absence")

def color_gradient(value: float, max_value: float) -> tuple[float, float, float]:
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


def absence_heatmap(data: list[list[AbsenceLine]], context: Axes) -> None:
    """
    creates a heatmap showing what periods where absent the most
    """
    periods_per_day = {i: {j: 0 for j in range(len(TIME_PERIODS))} for i in range(5)}

    # parse all data and assign to correct period
    for person in data:
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
    for i, day in enumerate(days):
        for p in range(len(TIME_PERIODS)):
            period = periods_per_day[i][p]

            context.bar(
                [day,],
                [50,],
                bottom=60*TIME_PERIODS[p][0].hour + TIME_PERIODS[p][0].minute,
                color=color_gradient(period, max_per_period) if period > 0 else (1, 1, 1)
            )

    context.set_title("Absence Heatmap")


def main() -> None:
    # plot people
    files = [file for file in os.listdir(DATA_DIR) if file.endswith(".csv")]

    # exit if no files were selected
    if len(files) == 0:
        exit(0)

    # plot files
    # Create figure
    fig = plt.figure(figsize=(12, 6))
    gs = gridspec.GridSpec(2, 2, height_ratios=[3, 2])  # Top graph gets more height

    # create subplots
    ax1 = fig.add_subplot(gs[0, :])  # Span across both columns
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[1, 1])

    # plot absences over time
    total_times = []
    all_data: list[list[AbsenceLine]] = []
    for file in files:
        total, data = plot_absence(
            os.path.join(DATA_DIR, file),
            ax1,
            EXCUSE_STATUS
        )

        if total > 0:
            total_times.append(total)

        all_data.append(data)

    # remove second plot on top
    absence_reason(all_data, ax2)
    absence_heatmap(all_data, ax3)

    # plot
    # Get handles and labels
    handles, labels = ax1.get_legend_handles_labels()

    # Sort labels and handles together
    sorted_handles_labels = sorted(
        zip(labels, handles),
        key=lambda x: total_times[labels.index(x[0])],  # Sorting by total_times
        reverse=True
    )
    sorted_labels, sorted_handles = zip(*sorted_handles_labels)

    # Apply sorted legend to axes[0]
    ax1.legend(sorted_handles, sorted_labels)
    ax1.grid()

    # plot settings
    if EXCUSE_STATUS == ExcuseStatus.both:
        ax1.set_title(f"Total absences")

    elif EXCUSE_STATUS == ExcuseStatus.excused:
        ax1.set_title(f"Excused absences")

    else:
        ax1.set_title(f"Unexcused absences")

    plt.show()


if __name__ == "__main__":
    main()

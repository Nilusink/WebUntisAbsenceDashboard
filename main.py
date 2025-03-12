"""
main.py

Author:
Nilusink
"""
from datetime import datetime, date, time, timedelta
# from tkinter import filedialog as fd
import matplotlib.pyplot as plt
import os


# settings
SEP: str = "\t"
DATA_DIR: str = "./data/"
CONST_BREAKS: list[tuple[time, time, timedelta]] = [
    (time(9, 40), time(9, 55), timedelta(minutes=15)),
    (time(11, 35), time(11, 40), timedelta(minutes=5)),
    (time(15, 0), time(15, 15), timedelta(minutes=15))
]


# multi lang support
TIME_FORMATS: dict[str, str] = {  # first key content -> time format
    "Full name": "%b %d, %Y, %I:%M %p",
    "Langname": "%d.%m.%Y, %H:%M"
}
TRANSLATION_KEY: list[tuple[str, list[str]]] = [
    ("Full name", ["Langname"]),
    ("First name", ["Vorname"]),
    ("ID", []),
    ("Class", ["Klasse"]),
    ("Start date", ["Beginndatum"]),
    ("Start time", ["Beginnzeit"]),
    ("End date", ["Enddatum"]),
    ("End time", ["Endzeit"]),
    ("Interruptions", ["Unterbrechungen"]),
    ("Reason of absence", ["Abwesenheitsgrund"]),
    ("Text/Reason", ["Text/Grund"]),
    ("Excuse number", ["Entschuldigungsnummer"]),
    ("Status", []),
    ("Text for the excuse", ["Entschuldigungstext"]),
    ("reported by student", ["gemeldet von Schüler*in"])
]


def read_csv(file: str, sep: str = ";") -> list[dict]:
    """
    read a csv file
    """
    with open(file, "r", encoding="utf-8") as file:
        lines = file.readlines()

        headers = lines[0].split(sep)

        # choose time format based on csv file language
        try:
            time_format = TIME_FORMATS[headers[0]]

        except KeyError:
            raise RuntimeError("Unsupported CSV Language")

        # translate csv keys to english
        for i in range(len(headers)):
            if headers[i] in TRANSLATION_KEY[i][1]:
                headers[i] = TRANSLATION_KEY[i][0]

        out = []
        for line in lines[1:]:
            line = dict(zip(headers, line.split(sep)))

            # convert time to datetime
            line["start"] = datetime.strptime(
                f"{line['Start date']}, {line['Start time']}",
                time_format
            )
            line["end"] = datetime.strptime(
                f"{line['End date']}, {line['End time']}",
                time_format
            )

            out.append(line)

        return out


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


def plot_absence(file_path: str, context: type[plt]) -> float:
    """
    plot a persons absence

    :param file_path:  CSV file
    :param context: matplotlib context
    :return: total absence in school hours
    """
    data = read_csv(file_path, sep=SEP)

    delta_data = []
    for line in data:
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

    name = (f"{data[0]['Full name']} "
            f"{data[0]['First name']} "
            f"({data[0]['Class']}, "
            f"{ys_cumm[-1].__ceil__():.0f} h)")

    context.plot(xs, ys_cumm, label=name)

    return ys_cumm[-1]


def main() -> None:
    # plot people
    # files = fd.askopenfilenames(
    #     filetypes=[("CSV files", "*.csv")],
    #     title="Open absence file",
    # )

    files = [file for file in os.listdir(DATA_DIR) if file.endswith(".csv")]

    if len(files) == 0:
        exit(0)

    # plot files
    total_times = []
    for file in files:
        total_times.append(plot_absence(os.path.join(DATA_DIR, file), plt))

    # plot
    # Get handles and labels
    handles, labels = plt.gca().get_legend_handles_labels()

    # Sort labels and handles together
    sorted_handles_labels = sorted(
        zip(labels, handles),
        key=lambda x: total_times[labels.index(x[0])],
        reverse=True
    )
    sorted_labels, sorted_handles = zip(*sorted_handles_labels)

    # Apply sorted legend
    plt.legend(sorted_handles, sorted_labels)

    # plot settings
    # plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()

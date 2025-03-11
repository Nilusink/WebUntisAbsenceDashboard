"""
main.py

Author:
Nilusink
"""
from tkinter import filedialog as fd
from datetime import datetime, date
import matplotlib.pyplot as plt


# settings
SEP: str = "\t"


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

        try:
            time_format = TIME_FORMATS[headers[0]]

        except KeyError:
            raise RuntimeError("Unsupported CSV Language")

        for i in range(len(headers)):
            if headers[i] in TRANSLATION_KEY[i][1]:
                print(f"Translating {headers[i]} -> {TRANSLATION_KEY[i][0]}")
                headers[i] = TRANSLATION_KEY[i][0]

        out = []
        for line in lines[1:]:
            line = dict(zip(headers, line.split(sep)))

            # convert time to datetime
            line["start"] = datetime.strptime(
                f"{line["Start date"]}, {line["Start time"]}",
                time_format
            )
            line["end"] = datetime.strptime(
                f"{line["End date"]}, {line["End time"]}",
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
    start = line["start"]
    end = line["end"]

    # get date
    d = start.date()

    # Compute the difference
    time_diff = end - start
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


def plot_absence(file_path: str, context: type[plt]) -> None:
    """
    plot a persons absence
    :param file_path: absence CSV file
    :param context: matplotlib context
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
            f"{ys_cumm[-1]:.0f} h)")

    context.plot(xs, ys_cumm, label=name)


def main() -> None:
    # plot people
    files = fd.askopenfilenames(
        filetypes=[("CSV files", "*.csv")],
        title="Open absence file",
        # initialdir="/",
    )

    for file in files:
        plot_absence(file, plt)
        # plot_absence("./AbsenceList_20250311_1008.csv", plt)

    # plot
    plt.legend()
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()

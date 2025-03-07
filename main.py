"""
main.py

Took: 27 Mins

Author:
Nilusink
"""
from datetime import datetime, date
import matplotlib.pyplot as plt


FILEPATH: str = "./AbsenceList_20250307_0903.csv"
SEP: str = "\t"


def read_csv(file: str, sep: str = ";") -> list[dict]:
    """
    read a csv file
    """
    with open(file, "r", encoding="utf-8") as file:
        lines = file.readlines()

        headers = lines[0].split(sep)

        out = []
        for line in lines[1:]:
            out.append(dict(zip(headers, line.split(sep))))

        return out


def calculate_time(line: dict, in_school_hours: bool = True) -> tuple[date, float]:
    """
    calculate the missing time from a line

    :param line: line to calculate
    :param in_school_hours: 60 min or 50 min intervals
    """
    start = datetime.strptime(f"{line["Start date"]}, {line["Start time"]}", "%b %d, %Y, %I:%M %p")
    end = datetime.strptime(f"{line["End date"]}, {line["End time"]}", "%b %d, %Y, %I:%M %p")

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


def main() -> None:
    data = read_csv(FILEPATH, sep=SEP)

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

    print(f"total time: {ys_cumm[-1]:.1f}")

    # plot
    plt.plot(xs, ys_cumm)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()

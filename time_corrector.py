"""
time_corrector.py

corrects absence files with more marked absence hours then
school hours (example: 25h a day of absence in my file)

Author:
Nilusink
"""
from tkinter.filedialog import askopenfilename
from datetime import time, datetime, timedelta
from enum import Enum
import typing as tp
import os


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


# types
# type Period = tuple[time, time]
Period = tuple


AbsenceLine = tp.TypedDict(
    "AbsenceLine",
    {
        "Full name": str,
        "First name": str,
        "ID": str,
        "Class": str,
        "Start date": str,
        "Start time": str,
        "End date": str,
        "End time": str,
        "Interruptions": tp.Optional[str],  # Might be empty
        "Reason of absence": str,
        "Text/Reason": tp.Optional[str],  # Might be empty
        "Excuse Number": int,
        "Status": str,
        "Text for the Excuse": tp.Optional[str],  # Might be empty
        "Reported by Student": bool,
        "start": tp.Optional[datetime],
        "end": tp.Optional[datetime]
    }
)


class ExcuseStatus(Enum):
    not_excused = "not excused"
    excused = "excused"
    both = "both"


# classes
class TimeTable:
    """
    basic timetable (only long breaks (lunch brake) included)
    does not describe what lessons are at which times, just
    at which times there is school
    """
    def __init__(
            self,
            monday_periods: list[Period],
            tuesday_periods: list[Period],
            wednesday_periods: list[Period],
            thursday_periods: list[Period],
            friday_periods: list[Period]
    ) -> None:
        self._periods = [
            monday_periods,
            tuesday_periods,
            wednesday_periods,
            thursday_periods,
            friday_periods
        ]

    def check_correct_absence(self, absence_line: AbsenceLine) -> tuple[list[AbsenceLine], bool]:
        """
        checks if an absence is correct. If not, corrects absence.
        """
        corrected_absences = []
        initial_absences: list[tuple[datetime, datetime]] = []

        # extract date
        start_date = absence_line["start"].date()
        end_date = absence_line["end"].date()

        # multi-day absence
        if start_date != end_date:
            print(f"multy-day: {absence_line['start'].date()}, "
                  f"{absence_line['start'].strftime('%H:%M, %A')} - "
                  f"{absence_line['end'].date()}, "
                  f"{absence_line['end'].strftime('%H:%M, %A')}")

            for i in range((end_date - start_date).days + 1):
                date = start_date + timedelta(days=i)

                corrected_start = datetime.combine(date, time(0, 0))
                corrected_end = datetime.combine(date, time(23, 59))

                if date == start_date:
                    corrected_start = datetime.combine(date, absence_line["start"].time())

                elif date == end_date:
                    corrected_end = datetime.combine(date, absence_line["end"].time())

                initial_absences.append((corrected_start, corrected_end))

                print(f" * {corrected_start.date()}, "
                  f"{corrected_start.strftime('%H:%M, %A')} - "
                  f"{corrected_end.date()}, "
                  f"{corrected_end.strftime('%H:%M, %A')}")

        # single-day absences
        else:
            initial_absences.append((absence_line["start"], absence_line["end"]))

        corrected = False
        for absence in initial_absences:
            absence_start = absence[0].time()
            absence_end = absence[1].time()

            weekday = absence[0].weekday()  # Monday = 0, Sunday = 6

            try:
                school_periods = self._periods[weekday]

            # absence on invalid weekday
            except IndexError:
                print(f"invalid absence: ({absence[0].date()}, "
                      f"{absence[0].strftime('%A')})")
                continue

            for period_start, period_end in school_periods:
                if absence_end <= period_start or absence_start >= period_end:
                    continue  # Absence is completely outside this period, skip

                # Calculate the valid overlapping period
                corrected_start = max(absence_start, period_start)
                corrected_end = min(absence_end, period_end)

                # keep track if an absence was corrected
                if corrected_start != absence_start or corrected_end != absence_end:
                    corrected = True

                if corrected_start < corrected_end:  # Ensure valid period
                    corrected_absence = absence_line.copy()

                    # correct times
                    start_date = absence[0].date()
                    end_date = absence[1].date()

                    corrected_absence["start"] = datetime.combine(start_date, corrected_start)
                    corrected_absence["end"] = datetime.combine(end_date, corrected_end)

                    corrected_absence["Start time"] = corrected_start.strftime("%I:%M %p")
                    corrected_absence["End time"] = corrected_end.strftime("%I:%M %p")

                    corrected_absences.append(corrected_absence)

            if corrected:
                print(f"corrected ({absence[0].date()}, "
                      f"{absence[0].strftime('%A')}): "
                      f"{absence_start} - {absence_end} -> {'; '.join(a['Start time'] + '-' + a['End time'] for a in corrected_absences)}")

        return corrected_absences, corrected


# functions
def read_csv(file: str, sep: str = ";") -> tuple[list[AbsenceLine], bool]:
    """
    read a csv file

    :return: lines as dict, bool: absence was corrected [y/n]
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
        corrected = False
        for line in lines[1:]:
            line: AbsenceLine = dict(zip(headers, line.split(sep)))

            # convert time to datetime
            line["start"] = datetime.strptime(
                f"{line['Start date']}, {line['Start time']}",
                time_format
            )
            line["end"] = datetime.strptime(
                f"{line['End date']}, {line['End time']}",
                time_format
            )

            if line["start"].month > 7:
                year = line["start"].year

            else:
                year = line["start"].year - 1  # set to starting year (2024/2025 -> 2024)

            # try to correct with timetable
            if year in TIMETABLES and line["Class"] in TIMETABLES[year]:
                data, c = TIMETABLES[year][line["Class"]].check_correct_absence(line)
                out.extend(data)

                if c:
                    corrected = True

            else:
                out.append(line)

        return out, corrected


def write_csv(data: list[AbsenceLine], out_path: str, sep: str) -> None:
    """
    dump the corrected data to a csv file
    """
    # remove keys not present in original CSV
    for line in data:
        line.pop("start")
        line.pop("end")

    # open file
    with open(out_path, "w") as out:
        # write headers
        headers = list(data[0].keys())
        out.write(sep.join([h.strip() for h in headers]) + "\n")

        # write data
        for line in data:
            out.write(sep.join(v.strip() for v in line.values()) + "\n")


def main() -> None:
    file = askopenfilename(
        filetypes=[("Absence Files", "*.csv"), ("Backup Absence Files", "*.csv.bup")],
        title="Select Absence File",
    )

    if not file:
        return

    data, was_corrected = read_csv(file, sep="\t")

    if was_corrected:
        print(f"Corrected Absence File: {file}")
        # write corrected file
        directory = os.path.dirname(file)
        filename = os.path.basename(file)

        write_csv(
            data,
            os.path.join(directory, "Corrected_"+filename),
            sep="\t"
        )

    else:
        if data[0]["Class"] not in TIMETABLES:
            print(f"Class not found for Absence File: {file} ({data[0]['Class']}")
            return

        print(f"No corrections made for {file}")


# predefined timetables
TIMETABLES = {
    2024: {
        "5AHEL": TimeTable(
            [
                (time(8, 00), time(13, 20)),
                (time(14, 10), time(16, 55))
            ],
            [
                (time(8, 00), time(12, 30)),
                (time(13, 20), time(16, 55))
            ],
            [
                (time(8, 00), time(13, 20)),
            ],
            [
                (time(8, 00), time(13, 20)),
            ],
            [
                (time(8, 00), time(8, 50)),
                (time(9, 55), time(13, 20))
            ]
        ),
        "5CHEL": TimeTable(
            [
                (time(8, 00), time(12, 30)),
                (time(13, 20), time(16, 55))
            ],
            [
                (time(8, 00), time(13, 20)),
                (time(14, 10), time(16, 55))
            ],
            [
                (time(8, 00), time(11, 35)),
                (time(12, 30), time(14, 10))
            ],
            [
                (time(8, 00), time(11, 35)),
                (time(12, 30), time(16, 55))
            ],
            [
                (time(8, 00), time(12, 30)),
            ]
        ),
        "4BHEL": TimeTable(
            [
                (time(8, 00), time(12, 30)),
                (time(13, 20), time(16, 5))
            ],
            [
                (time(8, 00), time(12, 30)),
                (time(13, 20), time(16, 55))
            ],
            [
                (time(8, 00), time(12, 30)),
                (time(13, 20), time(16, 55))
            ],
            [
                (time(8, 00), time(13, 20)),
            ],
            [
                (time(8, 00), time(13, 20)),
                (time(14, 10), time(16, 55))
            ]
        ),
    }
}
TIME_PERIODS = [
    (time(8, 00), time(8, 50)),
    (time(8, 50), time(9, 40)),
    (time(9, 55), time(10, 45)),
    (time(10, 45), time(11, 35)),
    (time(11, 40), time(12, 30)),
    (time(12, 30), time(13, 20)),
    (time(13, 20), time(14, 10)),
    (time(14, 10), time(15, 00)),
    (time(15, 15), time(16, 5)),
    (time(16, 5), time(16, 55)),
]


if __name__ == "__main__":
    main()

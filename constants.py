"""
constants.py

Project: WebUntisAbsenceDashboard
"""

from datetime import time, timedelta
from os import listdir

from time_corrector import ExcuseStatus

SEP: str = "\t"
DATA_DIR: str = "./data/"
EXCUSE_STATUS: ExcuseStatus = ExcuseStatus.both
CONST_BREAKS: list[tuple[time, time, timedelta]] = [
    (time(9, 40), time(9, 55), timedelta(minutes=15)),
    (time(11, 35), time(11, 40), timedelta(minutes=5)),
    (time(15, 0), time(15, 15), timedelta(minutes=15))
]

FILES = lambda: [file for file in listdir(DATA_DIR) if file.endswith(".csv")]

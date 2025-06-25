# WebUntis Absence Dashboard

This repository contains a couple of small scripts that work with absence CSV files exported from WebUntis.

## Requirements

- Python 3.12
- The dependencies listed in `requirements.txt`

Install the dependencies using pip:

```bash
python3.12 -m pip install -r requirements.txt
```

## Running the scripts

`time_corrector.py` can correct absence CSV files using predefined timetables. `main.py` reads the corrected CSV files and displays some plots.

Run either script with Python 3.12:

```bash
python3.12 time_corrector.py
python3.12 main.py
```


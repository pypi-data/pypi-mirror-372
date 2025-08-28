[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/NEMO-Reports?label=python)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/nemo-reports?label=pypi%20version)](https://pypi.org/project/NEMO-Reports/)

# NEMO Reports

This plugin for NEMO adds a variety of reports.

# Compatibility:

NEMO/NEMO-CE >= 7.0.0 ----> NEMO-Reports >= 2.0.0

NEMO >= 4.5.0 ----> NEMO-Reports >= 1.6.0

NEMO >= 4.3.0 ----> NEMO-Reports >= 1.0.0

# Installation

`pip install NEMO-reports[NEMO]`

# Add NEMO Reports

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_reports', # This needs to be before NEMO_billing (if installed) and NEMO
    '...'
    'NEMO_billing', # Optional
    '...'
    'NEMO',
    '...'
]
```

# Usage
Simply navigate to the `Reports` page in the `Administration` menu.

For non-administrator users, permissions are given per report, via `Detailed administration -> Users` (search for "report" in the permissions list)

## Options
Some options are available in `Customization -> Reports`:

* First day of the week (Sunday/Monday)
* Default report date range
* Excluding projects from report data
* Display format for duration

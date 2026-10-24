# Financial Market Anomaly Detection System

An end-to-end quantitative system designed to ingest financial market time-series data, validate data hygiene, compute robust statistical metrics and anomalies, evaluate synthetic scenarios, and generate executive reports.

## Project Status
- **Current Milestone:** Phase 1, Step 1.1 (Repository Skeleton, Environment & Configuration)
- **Status:** Initialized project structure, setuptools build configuration, centralized configuration module, and configuration unit tests.

## Directory Structure

```text
financial-market-anomaly-detection/
├── data/
│   ├── raw/                  # Raw, unvalidated market data downloads (.gitkeep)
│   └── processed/            # Cleaned, validated, and normalized datasets (.gitkeep)
├── notebooks/                # Exploratory data analysis and prototyping (.gitkeep)
├── reports/
│   └── figures/              # Generated plots and figures (.gitkeep)
├── src/
│   └── market_anomaly/       # Core package source tree
│       ├── __init__.py       # Package initializer
│       └── config.py         # Centralized configuration & path definitions
├── tests/
│   └── test_config.py        # Configuration and path resolution smoke tests
├── .gitignore                # Git ignore rules
├── pyproject.toml            # Project packaging specification and pytest options
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Setup & Installation (Windows PowerShell)

Follow these exact Windows PowerShell instructions to set up your environment, install the package in editable mode, and run test suites:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
pytest -v
```

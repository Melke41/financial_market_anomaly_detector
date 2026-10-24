"""Unit tests for market_anomaly.config."""

import importlib
from pathlib import Path


def test_import_market_anomaly() -> None:
    """Verify that market_anomaly and market_anomaly.config can be imported cleanly."""
    market_anomaly = importlib.import_module("market_anomaly")
    config = importlib.import_module("market_anomaly.config")
    assert market_anomaly is not None
    assert config is not None


def test_project_root_and_paths() -> None:
    """Verify that PROJECT_ROOT exists and contains pyproject.toml."""
    from market_anomaly.config import (
        DATA_DIR,
        FIGURES_DIR,
        PROCESSED_DATA_DIR,
        PROJECT_ROOT,
        RAW_DATA_DIR,
        REPORTS_DIR,
    )

    assert isinstance(PROJECT_ROOT, Path)
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()
    assert (PROJECT_ROOT / "pyproject.toml").is_file()

    # Verify derived directory paths
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert RAW_DATA_DIR == DATA_DIR / "raw"
    assert PROCESSED_DATA_DIR == DATA_DIR / "processed"
    assert REPORTS_DIR == PROJECT_ROOT / "reports"
    assert FIGURES_DIR == REPORTS_DIR / "figures"


def test_column_definitions() -> None:
    """Verify column tuples and that PRICE_COLUMNS is a subset of REQUIRED_OHLCV_COLUMNS."""
    from market_anomaly.config import (
        DEFAULT_TICKERS,
        PRICE_COLUMNS,
        REQUIRED_OHLCV_COLUMNS,
    )

    assert isinstance(REQUIRED_OHLCV_COLUMNS, tuple)
    assert isinstance(PRICE_COLUMNS, tuple)
    assert isinstance(DEFAULT_TICKERS, tuple)

    assert REQUIRED_OHLCV_COLUMNS == ("Open", "High", "Low", "Close", "Volume")
    assert PRICE_COLUMNS == ("Open", "High", "Low", "Close")

    # PRICE_COLUMNS must be a strict subset of REQUIRED_OHLCV_COLUMNS
    assert set(PRICE_COLUMNS).issubset(set(REQUIRED_OHLCV_COLUMNS))
    assert len(DEFAULT_TICKERS) > 0


def test_numerical_constants() -> None:
    """Verify numerical constants have expected values and types."""
    from market_anomaly.config import (
        DEFAULT_MAX_CALENDAR_GAP_DAYS,
        DEFAULT_MAX_FLAT_DAYS,
        DEFAULT_MIN_ROWS,
        DEFAULT_ROLLING_WINDOW,
        DEFAULT_Z_THRESHOLD,
        MAD_NORMAL_CONSISTENCY_CONSTANT,
        TRADING_DAYS_PER_YEAR,
    )

    assert isinstance(TRADING_DAYS_PER_YEAR, int)
    assert TRADING_DAYS_PER_YEAR == 252

    assert isinstance(MAD_NORMAL_CONSISTENCY_CONSTANT, float)
    assert MAD_NORMAL_CONSISTENCY_CONSTANT == 1.4826

    assert isinstance(DEFAULT_MIN_ROWS, int)
    assert DEFAULT_MIN_ROWS == 30

    assert isinstance(DEFAULT_MAX_FLAT_DAYS, int)
    assert DEFAULT_MAX_FLAT_DAYS == 5

    assert isinstance(DEFAULT_MAX_CALENDAR_GAP_DAYS, int)
    assert DEFAULT_MAX_CALENDAR_GAP_DAYS == 7

    assert isinstance(DEFAULT_ROLLING_WINDOW, int)
    assert DEFAULT_ROLLING_WINDOW == 20

    assert isinstance(DEFAULT_Z_THRESHOLD, float)
    assert DEFAULT_Z_THRESHOLD == 3.0

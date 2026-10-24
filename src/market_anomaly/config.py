"""Centralized configuration module for the Financial Market Anomaly Detection System."""

from pathlib import Path

# Dynamic directory resolution
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
DATA_DIR: Path = PROJECT_ROOT / "data"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
FIGURES_DIR: Path = REPORTS_DIR / "figures"

# Immutable schema and ticker constants
REQUIRED_OHLCV_COLUMNS: tuple[str, ...] = ("Open", "High", "Low", "Close", "Volume")
PRICE_COLUMNS: tuple[str, ...] = ("Open", "High", "Low", "Close")
DEFAULT_TICKERS: tuple[str, ...] = ("AAPL", "MSFT", "SPY", "GLD")

# Numerical constants for market analysis and anomaly detection
TRADING_DAYS_PER_YEAR: int = 252
DEFAULT_MIN_ROWS: int = 30
DEFAULT_MAX_FLAT_DAYS: int = 5
DEFAULT_MAX_CALENDAR_GAP_DAYS: int = 7
DEFAULT_ROLLING_WINDOW: int = 20
DEFAULT_Z_THRESHOLD: float = 3.0
MAD_NORMAL_CONSISTENCY_CONSTANT: float = 1.4826

__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "REPORTS_DIR",
    "FIGURES_DIR",
    "REQUIRED_OHLCV_COLUMNS",
    "PRICE_COLUMNS",
    "DEFAULT_TICKERS",
    "TRADING_DAYS_PER_YEAR",
    "DEFAULT_MIN_ROWS",
    "DEFAULT_MAX_FLAT_DAYS",
    "DEFAULT_MAX_CALENDAR_GAP_DAYS",
    "DEFAULT_ROLLING_WINDOW",
    "DEFAULT_Z_THRESHOLD",
    "MAD_NORMAL_CONSISTENCY_CONSTANT",
]

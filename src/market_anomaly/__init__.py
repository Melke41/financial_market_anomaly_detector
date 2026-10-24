"""Financial Market Anomaly Detection System."""

from market_anomaly.data_validation import (
    DataValidationError,
    ValidationResult,
    assert_valid_ohlcv,
    validate_ohlcv_dataframe,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "DataValidationError",
    "ValidationResult",
    "validate_ohlcv_dataframe",
    "assert_valid_ohlcv",
]

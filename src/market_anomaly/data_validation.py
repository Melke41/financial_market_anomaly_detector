"""Read-only data validation gatekeeper for OHLCV financial market time-series."""

from dataclasses import dataclass
from typing import Any

import pandas as pd

from market_anomaly.config import (
    DEFAULT_MAX_CALENDAR_GAP_DAYS,
    DEFAULT_MAX_FLAT_DAYS,
    DEFAULT_MIN_ROWS,
    PRICE_COLUMNS,
    REQUIRED_OHLCV_COLUMNS,
)


class DataValidationError(ValueError):
    """Raised when an OHLCV DataFrame fails critical validation checks."""

    pass


@dataclass(frozen=True)
class ValidationResult:
    """Immutable diagnostic results from OHLCV DataFrame validation."""

    is_valid: bool
    row_count: int
    missing_columns: tuple[str, ...]
    is_datetime_index: bool
    is_monotonic_increasing: bool
    duplicate_timestamp_count: int
    null_counts: dict[str, int]
    non_positive_price_count: int
    ohlc_violation_count: int
    negative_volume_count: int
    zero_volume_count: int
    max_consecutive_flat_close_days: int
    large_calendar_gaps: tuple[tuple[str, str, int], ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_ohlcv_dataframe(
    df: pd.DataFrame,
    *,
    required_columns: tuple[str, ...] = REQUIRED_OHLCV_COLUMNS,
    price_columns: tuple[str, ...] = PRICE_COLUMNS,
    min_rows: int = DEFAULT_MIN_ROWS,
    max_flat_days: int = DEFAULT_MAX_FLAT_DAYS,
    max_calendar_gap_days: int = DEFAULT_MAX_CALENDAR_GAP_DAYS,
) -> ValidationResult:
    """Perform comprehensive, strictly read-only validation of an OHLCV DataFrame.

    This function never mutates the input DataFrame. It evaluates structural schema,
    index integrity, mathematical envelope rules, and market anomalies, categorizing
    issues into critical errors (is_valid = False) and non-fatal warnings.

    Parameters
    ----------
    df : pd.DataFrame
        The input market data DataFrame to inspect.
    required_columns : tuple[str, ...], default REQUIRED_OHLCV_COLUMNS
        Columns required to be present with numeric dtypes.
    price_columns : tuple[str, ...], default PRICE_COLUMNS
        Price columns required to be strictly positive (> 0).
    min_rows : int, default DEFAULT_MIN_ROWS
        Minimum required row count.
    max_flat_days : int, default DEFAULT_MAX_FLAT_DAYS
        Threshold for consecutive flat Close prices triggering a warning.
    max_calendar_gap_days : int, default DEFAULT_MAX_CALENDAR_GAP_DAYS
        Calendar day gap threshold triggering a warning.

    Returns
    -------
    ValidationResult
        Frozen diagnostic summary of all checks, errors, and warnings.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Structural dimensions & columns
    row_count: int = len(df)
    missing_columns: tuple[str, ...] = tuple(c for c in required_columns if c not in df.columns)
    present_required_cols: list[str] = [c for c in required_columns if c in df.columns]

    # Rule B.1: Empty or Insufficient rows
    if row_count == 0:
        errors.append("DataFrame is empty (0 rows).")
    elif row_count < min_rows:
        errors.append(f"Insufficient rows: DataFrame has {row_count} rows, minimum required is {min_rows}.")

    # Rule B.2: Missing Required Columns
    if missing_columns:
        errors.append(f"Missing required column(s): {list(missing_columns)}.")

    # Rule B.3: Non-Numeric Required Columns
    non_numeric_cols: tuple[str, ...] = tuple(
        c for c in present_required_cols if not pd.api.types.is_numeric_dtype(df[c].dtype)
    )
    if non_numeric_cols:
        errors.append(f"Non-numeric required column(s): {list(non_numeric_cols)}.")

    # 2. Index integrity
    is_datetime_index: bool = isinstance(df.index, pd.DatetimeIndex)
    is_monotonic_increasing: bool = bool(df.index.is_monotonic_increasing) if hasattr(df.index, "is_monotonic_increasing") else False
    duplicate_timestamp_count: int = int(df.index.duplicated().sum()) if hasattr(df.index, "duplicated") else 0

    # Rule B.4: DatetimeIndex Check
    if not is_datetime_index:
        errors.append(f"Index is not a pd.DatetimeIndex (found {type(df.index).__name__}).")

    # Rule B.5: Monotonic Ordering Check
    if not is_monotonic_increasing:
        errors.append("Index is not monotonically increasing.")

    # Rule B.6: Duplicate Timestamp Check
    if duplicate_timestamp_count > 0:
        errors.append(f"Index contains {duplicate_timestamp_count} duplicate timestamp(s).")

    # 3. Null values check across present required columns
    null_counts: dict[str, int] = {str(c): int(df[c].isna().sum()) for c in present_required_cols}
    total_nulls = sum(null_counts.values())
    if total_nulls > 0:
        null_details = {k: v for k, v in null_counts.items() if v > 0}
        errors.append(f"Found null values in required columns: {null_details}.")

    # 4. Non-positive prices check (Rule B.8)
    numeric_price_cols = [
        c for c in price_columns if c in df.columns and pd.api.types.is_numeric_dtype(df[c].dtype)
    ]
    non_positive_price_count: int = 0
    if numeric_price_cols and row_count > 0:
        price_sub = df[numeric_price_cols]
        non_positive_price_count = int((price_sub <= 0).any(axis=1).sum())
        if non_positive_price_count > 0:
            errors.append(f"Found {non_positive_price_count} row(s) with non-positive prices (<= 0).")

    # 5. OHLC Logical Envelope Violations (Rule B.9)
    # Envelope requires High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close
    envelope_cols = ["Open", "High", "Low", "Close"]
    can_check_envelope = all(
        c in df.columns and pd.api.types.is_numeric_dtype(df[c].dtype) for c in envelope_cols
    )
    ohlc_violation_count: int = 0
    if can_check_envelope and row_count > 0:
        sub = df[envelope_cols]
        complete_mask = sub.notna().all(axis=1)
        if complete_mask.any():
            h = sub.loc[complete_mask, "High"]
            l = sub.loc[complete_mask, "Low"]
            o = sub.loc[complete_mask, "Open"]
            c = sub.loc[complete_mask, "Close"]
            viol_mask = (h < l) | (h < o) | (h < c) | (l > o) | (l > c)
            ohlc_violation_count = int(viol_mask.sum())
            if ohlc_violation_count > 0:
                errors.append(
                    f"Found {ohlc_violation_count} row(s) violating OHLC logical envelope "
                    "(High must be >= Open, Close, Low; Low must be <= Open, Close, High)."
                )

    # 6. Negative Volume Check (Rule B.10)
    negative_volume_count: int = 0
    if "Volume" in df.columns and pd.api.types.is_numeric_dtype(df["Volume"].dtype) and row_count > 0:
        vol_clean = df["Volume"].dropna()
        negative_volume_count = int((vol_clean < 0).sum())
        if negative_volume_count > 0:
            errors.append(f"Found {negative_volume_count} row(s) with negative Volume (< 0).")

    # 7. Non-Fatal Warnings (Rule C)
    # Warning C.1: Zero Volume
    zero_volume_count: int = 0
    if "Volume" in df.columns and pd.api.types.is_numeric_dtype(df["Volume"].dtype) and row_count > 0:
        vol_clean = df["Volume"].dropna()
        zero_volume_count = int((vol_clean == 0).sum())
        if zero_volume_count > 0:
            warnings.append(f"Found {zero_volume_count} row(s) with zero Volume.")

    # Warning C.2: Consecutive Flat Close Streak
    max_consecutive_flat_close_days: int = 0
    if "Close" in df.columns and pd.api.types.is_numeric_dtype(df["Close"].dtype) and row_count > 0:
        close_clean = df["Close"].dropna()
        if len(close_clean) >= 1:
            diff_mask = close_clean != close_clean.shift()
            run_ids = diff_mask.cumsum()
            max_consecutive_flat_close_days = int(run_ids.value_counts().max())
            if max_consecutive_flat_close_days >= max_flat_days:
                warnings.append(
                    f"Detected streak of {max_consecutive_flat_close_days} consecutive flat Close "
                    f"trading days (warning threshold >= {max_flat_days})."
                )

    # Warning C.3: Large Calendar Gaps
    large_calendar_gaps_list: list[tuple[str, str, int]] = []
    if is_datetime_index and is_monotonic_increasing and duplicate_timestamp_count == 0 and row_count > 1:
        dt_series = df.index.to_series()
        day_diffs = dt_series.diff().dt.days
        for i in range(1, len(df.index)):
            gap = day_diffs.iloc[i]
            if pd.notna(gap) and int(gap) > max_calendar_gap_days:
                prev_ts = df.index[i - 1]
                curr_ts = df.index[i]
                prev_str = (
                    prev_ts.strftime("%Y-%m-%d")
                    if prev_ts.hour == 0 and prev_ts.minute == 0 and prev_ts.second == 0
                    else prev_ts.isoformat()
                )
                curr_str = (
                    curr_ts.strftime("%Y-%m-%d")
                    if curr_ts.hour == 0 and curr_ts.minute == 0 and curr_ts.second == 0
                    else curr_ts.isoformat()
                )
                large_calendar_gaps_list.append((prev_str, curr_str, int(gap)))

        if large_calendar_gaps_list:
            warnings.append(
                f"Detected {len(large_calendar_gaps_list)} calendar gap(s) exceeding {max_calendar_gap_days} days."
            )

    large_calendar_gaps: tuple[tuple[str, str, int], ...] = tuple(large_calendar_gaps_list)
    is_valid: bool = len(errors) == 0

    return ValidationResult(
        is_valid=is_valid,
        row_count=row_count,
        missing_columns=missing_columns,
        is_datetime_index=is_datetime_index,
        is_monotonic_increasing=is_monotonic_increasing,
        duplicate_timestamp_count=duplicate_timestamp_count,
        null_counts=null_counts,
        non_positive_price_count=non_positive_price_count,
        ohlc_violation_count=ohlc_violation_count,
        negative_volume_count=negative_volume_count,
        zero_volume_count=zero_volume_count,
        max_consecutive_flat_close_days=max_consecutive_flat_close_days,
        large_calendar_gaps=large_calendar_gaps,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def assert_valid_ohlcv(
    df: pd.DataFrame,
    **kwargs: Any,
) -> ValidationResult:
    """Validate an OHLCV DataFrame and raise DataValidationError if invalid.

    Parameters
    ----------
    df : pd.DataFrame
        Input OHLCV DataFrame.
    **kwargs : Any
        Optional keyword arguments passed directly to validate_ohlcv_dataframe.

    Returns
    -------
    ValidationResult
        Diagnostic summary from validation.

    Raises
    ------
    DataValidationError
        If any critical validation errors are encountered.
    """
    result = validate_ohlcv_dataframe(df, **kwargs)
    if not result.is_valid:
        error_summary = "; ".join(result.errors)
        raise DataValidationError(f"OHLCV DataFrame validation failed ({len(result.errors)} errors): {error_summary}")
    return result


__all__ = [
    "DataValidationError",
    "ValidationResult",
    "validate_ohlcv_dataframe",
    "assert_valid_ohlcv",
]

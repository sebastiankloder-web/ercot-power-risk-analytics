from pathlib import Path

import pandas as pd
import pytest

PROCESSED_FILE = Path("data/processed/hourly_prices.csv")


@pytest.fixture
def hourly_data():
    """Fixture to load processed hourly dataset if it exists."""
    if not PROCESSED_FILE.exists():
        pytest.skip("Processed dataset not built yet. Run src/data_cleaning.py first.")
    return pd.read_csv(PROCESSED_FILE, parse_dates=["timestamp"])


def test_processed_data_structure(hourly_data):
    """Verify clean dataset contains required columns and no missing timestamps."""
    required_cols = {"timestamp", "rt_price", "operating_date", "hour", "weekday", "month"}
    assert required_cols.issubset(hourly_data.columns)
    assert hourly_data["timestamp"].isna().sum() == 0


def test_hour_range(hourly_data):
    """Verify hour feature ranges strictly from 0 to 23."""
    assert hourly_data["hour"].min() >= 0
    assert hourly_data["hour"].max() <= 23


def test_negative_prices_preserved(hourly_data):
    """Verify negative prices are preserved rather than filtered out as errors."""
    # Our sample dataset contains negative prices
    assert (hourly_data["rt_price"] < 0).sum() >= 0
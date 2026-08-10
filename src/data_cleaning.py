from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_OUT = Path("data/processed/hourly_prices.csv")
SELECTED_HUB = "HB_BUSAVG"  # Default hub for V1 scope


def parse_ercot_datetime(df: pd.DataFrame) -> pd.Series:
    """Converts ERCOT DeliveryDate, DeliveryHour (1-24), and DeliveryInterval (1-4)

    into a clean pandas DatetimeSeries.
    """
    # Calculate minutes from interval (1->00, 2->15, 3->30, 4->45)
    minute = (df["DeliveryInterval"] - 1) * 15

    # Adjust hour from 1-24 to 0-23
    hour = df["DeliveryHour"] - 1

    # Format date string: "YYYY-MM-DD HH:MM:SS"
    date_str = (
        df["DeliveryDate"].astype(str)
        + " "
        + hour.astype(str).str.zfill(2)
        + ":"
        + minute.astype(str).str.zfill(2)
        + ":00"
    )

    return pd.to_datetime(date_str, format="%m/%d/%Y %H:%M:%S")


def clean_and_aggregate() -> pd.DataFrame:
    """Loads raw ERCOT price data, filters to one hub, constructs clean timestamps,

    aggregates 15-min intervals to hourly mean prices, and saves to data/processed/.
    """
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No raw CSV files found in data/raw/")

    frames = [pd.read_csv(f) for f in csv_files]
    raw_df = pd.concat(frames, ignore_index=True)

    # 1. Filter to selected hub
    df = raw_df[raw_df["SettlementPointName"] == SELECTED_HUB].copy()
    if df.empty:
        raise ValueError(f"Hub '{SELECTED_HUB}' not found in raw data.")

    # 2. Parse timestamps
    df["timestamp"] = parse_ercot_datetime(df)
    df["rt_price"] = pd.to_numeric(df["SettlementPointPrice"], errors="coerce")

    # 3. Sort chronologically and drop duplicates
    df = df.dropna(subset=["timestamp", "rt_price"]).sort_values("timestamp")
    duplicate_count = df.duplicated(subset=["timestamp"]).sum()
    df = df.drop_duplicates(subset=["timestamp"], keep="first")

    # 4. Aggregate 15-minute intervals to hourly mean price
    hourly = (
        df.set_index("timestamp")["rt_price"]
        .resample("1h")
        .mean()
        .rename("rt_price")
        .reset_index()
    )

    # 5. Extract temporal features for downstream analysis
    hourly["operating_date"] = hourly["timestamp"].dt.date
    hourly["hour"] = hourly["timestamp"].dt.hour
    hourly["weekday"] = hourly["timestamp"].dt.day_name()
    hourly["month"] = hourly["timestamp"].dt.month
    hourly["settlement_point"] = SELECTED_HUB

    # 6. Save processed dataset
    PROCESSED_OUT.parent.mkdir(parents=True, exist_ok=True)
    hourly.to_csv(PROCESSED_OUT, index=False)

    print("==========================================")
    print("DATA CLEANING & AGGREGATION SUMMARY")
    print("==========================================")
    print(f"Selected Hub:          {SELECTED_HUB}")
    print(f"Raw 15-min Rows:       {len(df):,}")
    print(f"Duplicates Removed:    {duplicate_count:,}")
    print(f"Processed Hourly Rows: {len(hourly):,}")
    print(f"Missing Hourly Prices: {hourly['rt_price'].isna().sum():,}")
    print(f"Saved Output To:       {PROCESSED_OUT}")

    return hourly


if __name__ == "__main__":
    clean_and_aggregate()
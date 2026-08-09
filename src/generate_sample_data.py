from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")


def create_mock_ercot_data(filename="ercot_rtm_sample_2026.csv"):
    """Generates 1 month of 15-minute ERCOT Real-Time Settlement Point Prices

    matching ERCOT's official MIS report schema.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 30 days of 15-minute settlement intervals
    dates = pd.date_range(
        start="2026-05-01 00:00", end="2026-05-31 23:45", freq="15min"
    )

    hubs = ["HB_BUSAVG", "HB_NORTH", "HB_WEST", "HB_HOUSTON"]
    records = []

    np.random.seed(42)  # Fixed seed for reproducible sample generation

    for hub in hubs:
        # Intraday pattern (~$30 average with daytime peak)
        base_price = 30 + 15 * np.sin(np.pi * dates.hour / 12)
        noise = np.random.normal(0, 8, len(dates))

        # Add scarcity spikes and negative oversupply prices
        spikes = np.random.choice(
            [0, 250, 1200], size=len(dates), p=[0.98, 0.015, 0.005]
        )
        negatives = np.random.choice(
            [0, -45],
            size=len(dates),
            p=[0.96, 0.04] if hub == "HB_WEST" else [0.99, 0.01],
        )

        final_prices = base_price + noise + spikes + negatives

        for dt, price in zip(dates, final_prices):
            records.append(
                {
                    "DeliveryDate": dt.strftime("%m/%d/%Y"),
                    "DeliveryHour": dt.hour + 1,  # ERCOT Hours 1-24
                    "DeliveryInterval": (dt.minute // 15) + 1,
                    "SettlementPointName": hub,
                    "SettlementPointPrice": round(price, 2),
                    "DSTFlag": "N",
                }
            )

    df = pd.DataFrame(records)
    out_path = RAW_DIR / filename
    df.to_csv(out_path, index=False)
    print(f"[SUCCESS] Created raw source file: {out_path} ({len(df):,} rows)")


if __name__ == "__main__":
    create_mock_ercot_data()
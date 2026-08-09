from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")


def inspect_raw_files():
    """Audits raw CSV files in data/raw/ and prints summary metadata."""
    csv_files = list(RAW_DIR.glob("*.csv"))

    if not csv_files:
        print("[ERROR] No CSV files found in data/raw/")
        return

    for file_path in csv_files:
        print("\n==========================================")
        print(f"INSPECTING SOURCE FILE: {file_path.name}")
        print("==========================================")

        df = pd.read_csv(file_path)

        print(f"\n1. Total Records: {len(df):,} rows")
        print("\n2. Columns & Data Types:")
        print(df.dtypes)

        print("\n3. First 3 Sample Rows:")
        print(df.head(3))

        if "SettlementPointName" in df.columns:
            print("\n4. Available Trading Hubs / Settlement Points:")
            print(df["SettlementPointName"].unique())

        if "SettlementPointPrice" in df.columns:
            prices = df["SettlementPointPrice"]
            print("\n5. Price Distribution Summary ($/MWh):")
            print(f"   Min Price:  ${prices.min():.2f}")
            print(f"   Max Price:  ${prices.max():.2f}")
            print(f"   Mean Price: ${prices.mean():.2f}")
            print(f"   Missing Values: {prices.isna().sum()}")


if __name__ == "__main__":
    inspect_raw_files()
    
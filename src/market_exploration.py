from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROCESSED_FILE = Path("data/processed/hourly_prices.csv")
TABLES_DIR = Path("results/tables")
FIGURES_DIR = Path("results/figures")


def calculate_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates descriptive statistical properties of the hourly price series."""
    prices = df["rt_price"].dropna()

    stats = {
        "Total Hourly Rows": len(prices),
        "Mean Price ($/MWh)": round(prices.mean(), 2),
        "Median Price ($/MWh)": round(prices.median(), 2),
        "Std Dev ($/MWh)": round(prices.std(), 2),
        "Min Price ($/MWh)": round(prices.min(), 2),
        "Max Price ($/MWh)": round(prices.max(), 2),
        "Negative Price Count": (prices < 0).sum(),
        "Negative Price Frequency (%)": round((prices < 0).mean() * 100, 2),
        "Spike Count (> $100/MWh)": (prices > 100).sum(),
        "Spike Frequency (%)": round((prices > 100).mean() * 100, 2),
    }

    summary_df = pd.DataFrame([stats])
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(TABLES_DIR / "market_summary_stats.csv", index=False)
    return summary_df


def generate_exploration_plots(df: pd.DataFrame):
    """Generates time-series, distribution, and hourly boxplot figures."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Apply clean plotting style
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Figure 1: Time Series Plot (Full Scale vs Clipped Scale)
    _fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df["timestamp"], df["rt_price"], color="#1f77b4", linewidth=0.8)
    ax1.set_title("ERCOT Real-Time Hourly Prices (Full Scale with Spikes)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Price ($/MWh)")
    ax1.axhline(0, color="red", linestyle="--", alpha=0.6, label="Negative Price Threshold ($0)")
    ax1.legend(loc="upper right")

    # Zoomed view (clipped between -$50 and $150 to show normal operating regime)
    ax2.plot(df["timestamp"], df["rt_price"], color="#1f77b4", linewidth=0.8)
    ax2.set_ylim(-50, 150)
    ax2.set_title("ERCOT Real-Time Hourly Prices (Zoomed View: -$50 to $150/MWh)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Timestamp")
    ax2.set_ylabel("Price ($/MWh)")
    ax2.axhline(0, color="red", linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "01_time_series.png", dpi=300)
    plt.close()

    # Figure 2: Price Distribution Histogram (Log Scale to show Fat Tails)
    plt.figure(figsize=(10, 5))
    sns.histplot(df["rt_price"], bins=50, kde=True, color="#2ca02c")
    plt.axvline(df["rt_price"].mean(), color="orange", linestyle="-", linewidth=2, label=f"Mean (${df['rt_price'].mean():.2f})")
    plt.axvline(df["rt_price"].median(), color="blue", linestyle="--", linewidth=2, label=f"Median (${df['rt_price'].median():.2f})")
    plt.title("Distribution of ERCOT Hourly Prices (Showing Fat Right Tail)", fontsize=12, fontweight="bold")
    plt.xlabel("Price ($/MWh)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "02_price_histogram.png", dpi=300)
    plt.close()

    # Figure 3: Intraday Hour-of-Day Boxplot
    plt.figure(figsize=(12, 6))
    sns.boxplot(x="hour", y="rt_price", data=df, color="#9467bd", fliersize=2)
    plt.ylim(-50, 200)  # Clip outliers for clean visualization of hourly quartiles
    plt.title("Intraday Hourly Price Distribution (Hour 0 to Hour 23)", fontsize=12, fontweight="bold")
    plt.xlabel("Operating Hour of Day (0-23)")
    plt.ylabel("Price ($/MWh)")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "03_intraday_boxplot.png", dpi=300)
    plt.close()

    print(f"[SUCCESS] Saved 3 exploration figures to: {FIGURES_DIR}")


def run_market_exploration():
    """Loads processed hourly data and executes full exploration suite."""
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError("Processed data not found. Run src/data_cleaning.py first.")

    df = pd.read_csv(PROCESSED_FILE, parse_dates=["timestamp"])
    summary_df = calculate_summary_stats(df)
    
    print("\n==========================================")
    print("MARKET SUMMARY STATISTICS")
    print("==========================================")
    for col in summary_df.columns:
        print(f"{col:<30}: {summary_df[col].iloc[0]}")
    
    generate_exploration_plots(df)


if __name__ == "__main__":
    run_market_exploration()
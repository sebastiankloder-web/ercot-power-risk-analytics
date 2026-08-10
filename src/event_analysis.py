from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROCESSED_FILE = Path("data/processed/hourly_prices.csv")
TABLES_DIR = Path("results/tables")
FIGURES_DIR = Path("results/figures")


def calculate_max_consecutive(series_bool: pd.Series) -> int:
    """Calculates the maximum consecutive sequence of True values in a boolean Series."""
    # Group consecutive True values and find max length
    return int((series_bool != series_bool.shift()).cumsum()[series_bool].value_counts().max() if series_bool.any() else 0)


def analyze_events(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes negative price events, scarcity spikes, and tail concentration ratios."""
    prices = df["rt_price"].dropna()
    total_hours = len(prices)

    # 1. Negative Price Analysis (< $0/MWh)
    is_neg = prices < 0
    neg_count = is_neg.sum()
    neg_freq = (neg_count / total_hours) * 100
    max_neg_run = calculate_max_consecutive(is_neg)
    min_price = prices.min()

    # 2. Scarcity Spike Analysis (> $100/MWh and > $250/MWh)
    is_spike_100 = prices > 100
    spike_100_count = is_spike_100.sum()
    spike_100_freq = (spike_100_count / total_hours) * 100
    max_spike_run = calculate_max_consecutive(is_spike_100)
    max_price = prices.max()

    # 3. Tail Concentration Ratios
    abs_prices = prices.abs().sort_values(ascending=False)
    total_abs_sum = abs_prices.sum()

    top_1_pct_count = max(1, int(np.ceil(0.01 * total_hours)))
    top_5_pct_count = max(1, int(np.ceil(0.05 * total_hours)))

    conc_1_pct = (abs_prices.iloc[:top_1_pct_count].sum() / total_abs_sum) * 100
    conc_5_pct = (abs_prices.iloc[:top_5_pct_count].sum() / total_abs_sum) * 100

    metrics = {
        "Total Hours Evaluated": total_hours,
        "Negative Price Hours (< $0)": neg_count,
        "Negative Price Frequency (%)": round(neg_freq, 2),
        "Max Consecutive Negative Hours": max_neg_run,
        "Min Observed Price ($/MWh)": round(min_price, 2),
        "Spike Hours (> $100/MWh)": spike_100_count,
        "Spike Frequency (%)": round(spike_100_freq, 2),
        "Max Consecutive Spike Hours": max_spike_run,
        "Max Observed Price ($/MWh)": round(max_price, 2),
        "Top 1% Tail Concentration Ratio (%)": round(conc_1_pct, 2),
        "Top 5% Tail Concentration Ratio (%)": round(conc_5_pct, 2),
    }

    summary_df = pd.DataFrame([metrics])

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(TABLES_DIR / "event_analysis_summary.csv", index=False)
    return summary_df


def plot_tail_concentration(df: pd.DataFrame):
    """Generates a Lorenz-style concentration curve showing cumulative tail weight."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    prices = df["rt_price"].dropna().abs().sort_values(ascending=False).values
    cum_prices = np.cumsum(prices) / np.sum(prices) * 100
    cum_hours = (np.arange(1, len(prices) + 1) / len(prices)) * 100

    plt.figure(figsize=(10, 6))
    plt.plot(cum_hours, cum_prices, color="#d62728", linewidth=2.5, label="ERCOT Price Magnitude Concentration")
    plt.plot([0, 100], [0, 100], color="black", linestyle="--", alpha=0.6, label="Uniform Distribution (Baseline)")

    # Highlight Top 5% point
    top_5_idx = int(np.ceil(0.05 * len(prices))) - 1
    plt.scatter([cum_hours[top_5_idx]], [cum_prices[top_5_idx]], color="blue", s=80, zorder=5)
    plt.annotate(
        f"Top 5% Hours = {cum_prices[top_5_idx]:.1f}% Total Magnitude",
        xy=(cum_hours[top_5_idx], cum_prices[top_5_idx]),
        xytext=(cum_hours[top_5_idx] + 10, cum_prices[top_5_idx] - 15),
        arrowprops={"facecolor": "black", "shrink": 0.05, "width": 1, "headwidth": 6},
        fontsize=10,
        fontweight="bold",
    )

    plt.title("Tail Concentration Curve (Lorenz Curve of Absolute Prices)", fontsize=12, fontweight="bold")
    plt.xlabel("Percentage of Total Operating Hours (%)")
    plt.ylabel("Percentage of Cumulative Price Magnitude (%)")
    plt.xlim(0, 100)
    plt.ylim(0, 105)
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "04_tail_concentration.png", dpi=300)
    plt.close()

    print(f"[SUCCESS] Saved tail concentration curve to: {FIGURES_DIR / '04_tail_concentration.png'}")


def run_event_analysis():
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError("Processed dataset missing. Run src/data_cleaning.py first.")

    df = pd.read_csv(PROCESSED_FILE, parse_dates=["timestamp"])
    summary_df = analyze_events(df)

    print("\n==========================================")
    print("EXTREME EVENT & TAIL CONCENTRATION SUMMARY")
    print("==========================================")
    for col in summary_df.columns:
        print(f"{col:<35}: {summary_df[col].iloc[0]}")

    plot_tail_concentration(df)


if __name__ == "__main__":
    run_event_analysis()
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_cleaning import clean_and_aggregate
from src.event_analysis import run_event_analysis
from src.fetch_real_data import fetch_ercot_real_data
from src.market_exploration import run_market_exploration
from src.risk_metrics import run_risk_analysis


def run_full_pipeline():
    start_time = time.time()
    print("==================================================")
    print("  ERCOT POWER PRICE RISK & MARKET ANALYTICS FRAMEWORK  ")
    print("==================================================")

    print("\n[STAGE 1/5] Fetching Live ERCOT Market Data...")
    fetch_ercot_real_data(days_back=7)

    print("\n[STAGE 2/5] Cleaning & Aggregating Hourly Prices...")
    clean_and_aggregate()

    print("\n[STAGE 3/5] Executing Market Exploration & Figure Generation...")
    run_market_exploration()

    print("\n[STAGE 4/5] Computing Historical VaR, Expected Shortfall & Drawdown...")
    run_risk_analysis()

    print("\n[STAGE 5/5] Performing Extreme Event Analysis & Tail Concentration...")
    run_event_analysis()

    elapsed = time.time() - start_time
    print("\n==================================================")
    print(f" PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.2f} SECONDS")
    print(" All figures saved to:  results/figures/")
    print(" All tables saved to:   results/tables/")
    print("==================================================")


if __name__ == "__main__":
    run_full_pipeline()
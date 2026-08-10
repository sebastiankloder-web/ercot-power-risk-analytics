from pathlib import Path

import pandas as pd

PROCESSED_FILE = Path("data/processed/hourly_prices.csv")
TABLES_DIR = Path("results/tables")


def historical_var_es(losses: pd.Series, confidence: float = 0.95) -> dict:
    """Calculates Historical Value-at-Risk (VaR) and Expected Shortfall (ES).

    Parameters:
        losses: pd.Series of loss values (where positive values indicate financial loss).
        confidence: Confidence level (e.g., 0.95 or 0.99).

    Returns:
        dict containing confidence, VaR, and Expected Shortfall.
    """
    clean_losses = pd.Series(losses).dropna().astype(float)
    if clean_losses.empty:
        raise ValueError("Loss series is empty.")

    # Historical quantile loss threshold
    var = float(clean_losses.quantile(confidence))

    # Tail losses at or beyond VaR
    tail = clean_losses[clean_losses >= var]
    es = float(tail.mean())

    return {
        "confidence": confidence,
        "var": round(var, 2),
        "expected_shortfall": round(es, 2),
    }


def calculate_max_drawdown(cumulative_pnl: pd.Series) -> float:
    """Calculates peak-to-trough Maximum Drawdown on a cumulative P&L series."""
    clean_pnl = pd.Series(cumulative_pnl).dropna().astype(float)
    running_peak = clean_pnl.cummax()
    drawdown = clean_pnl - running_peak
    return round(float(drawdown.min()), 2)


def build_risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Derives hourly price changes, builds illustrative 1 MWh long exposure P&L,

    and computes risk metrics.
    """
    prices = df["rt_price"].dropna()

    # 1. Hourly price changes (\Delta P)
    price_changes = prices.diff().dropna()

    # 2. Illustrative 1 MWh Long Exposure Loss Series (Loss = - \Delta P)
    losses = -price_changes

    # 3. Cumulative P&L for Drawdown calculation
    pnl = price_changes.cumsum()

    # 4. Compute VaR & ES at 95% and 99%
    var_95 = historical_var_es(losses, 0.95)
    var_99 = historical_var_es(losses, 0.99)
    mdd = calculate_max_drawdown(pnl)

    risk_metrics = {
        "Metric Scope": "1 MWh Long Hourly Exposure",
        "Price Level Mean ($)": round(prices.mean(), 2),
        "Price Change Std ($)": round(price_changes.std(), 2),
        "Historical VaR (95%) ($)": var_95["var"],
        "Expected Shortfall (95%) ($)": var_95["expected_shortfall"],
        "Historical VaR (99%) ($)": var_99["var"],
        "Expected Shortfall (99%) ($)": var_99["expected_shortfall"],
        "Maximum Drawdown ($)": mdd,
    }

    summary_df = pd.DataFrame([risk_metrics])

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(TABLES_DIR / "risk_summary.csv", index=False)
    return summary_df


def run_risk_analysis():
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError("Processed dataset missing. Run src/data_cleaning.py first.")

    df = pd.read_csv(PROCESSED_FILE, parse_dates=["timestamp"])
    risk_df = build_risk_summary(df)

    print("\n==========================================")
    print("QUANTITATIVE RISK & TAIL METRICS")
    print("==========================================")
    for col in risk_df.columns:
        print(f"{col:<30}: {risk_df[col].iloc[0]}")


if __name__ == "__main__":
    run_risk_analysis()
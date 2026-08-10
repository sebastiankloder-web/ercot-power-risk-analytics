import pandas as pd
import pytest

from src.risk_metrics import calculate_max_drawdown, historical_var_es


def test_expected_shortfall_is_at_least_var():
    """Verify that Expected Shortfall (tail mean) >= VaR threshold."""
    losses = pd.Series([0, 1, 2, 3, 4, 10, 20, 50, 100])
    result = historical_var_es(losses, confidence=0.80)

    assert result["expected_shortfall"] >= result["var"]


def test_max_drawdown_calculation():
    """Verify peak-to-trough drawdown calculation using known series."""
    # Peak is at 8, lowest subsequent point before recovery is 2 (Drawdown = 2 - 8 = -6)
    cumulative_pnl = pd.Series([0, 5, 3, 8, 2, 6])
    assert calculate_max_drawdown(cumulative_pnl) == -6.0


def test_empty_loss_series_raises_error():
    """Verify error handling on empty data series."""
    with pytest.raises(ValueError):
        historical_var_es(pd.Series([]), 0.95)
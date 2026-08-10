import pandas as pd

from src.event_analysis import analyze_events, calculate_max_consecutive


def test_calculate_max_consecutive():
    """Verify max consecutive run tracking for boolean series."""
    series = pd.Series([False, True, True, True, False, True, True])
    assert calculate_max_consecutive(series) == 3


def test_tail_concentration_bounds():
    """Verify top 1% and 5% tail concentration ratios are bounded between 0% and 100%."""
    data = pd.DataFrame({"rt_price": [10.0, 20.0, -50.0, 100.0, 500.0, 30.0, 25.0, -10.0, 15.0, 40.0]})
    summary = analyze_events(data)

    conc_1 = summary["Top 1% Tail Concentration Ratio (%)"].iloc[0]
    conc_5 = summary["Top 5% Tail Concentration Ratio (%)"].iloc[0]

    assert 0 <= conc_1 <= 100
    assert 0 <= conc_5 <= 100
    assert conc_5 >= conc_1
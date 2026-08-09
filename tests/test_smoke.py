def test_environment_smoke():
    """Smoke test to verify pytest framework and core libraries operate as expected."""
    import numpy as np
    import pandas as pd

    data = [10.0, 20.0, 30.0]
    series = pd.Series(data)

    assert series.mean() == 20.0
    assert np.isnan(np.nan)
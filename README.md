# ERCOT Power Price Risk & Market Analytics Framework

## North-Star Question
How is risk distributed in ERCOT real-time power prices, when do extreme and negative-price events occur, and what do those patterns reveal about tail risk in a volatile commodity market?

## Project Scope (V1)
* **Trading Hub**: All ERCOT prices
* **Aggregation**: Hourly prices derived from real-time settlement intervals
* **Risk Metrics**: Historical VaR, Expected Shortfall, Tail Concentration

## Setup & Execution
1. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
2. Run tests: `python -m pytest`

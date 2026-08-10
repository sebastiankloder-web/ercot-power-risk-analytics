@echo off
echo =========================================
echo Executing ERCOT Price Risk Pipeline
echo =========================================

python src/data_cleaning.py
python src/run_project.py
pytest -v

echo =========================================
echo Execution complete.
echo =========================================

from pathlib import Path

# Project root: FloodRiskPrediction
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Correct location of the prepared dataset
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "historical_severity_model_data.csv"
)

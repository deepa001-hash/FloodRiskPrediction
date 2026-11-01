
import pandas as pd
from pathlib import Path

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "raw"

floods = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)
rainfall = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)
metadata = pd.read_csv(
    DATA_DIR / "metadata_indofloods.csv"
)

print("\nFLOOD EVENT COLUMNS")
print(floods.columns.tolist())

print("\nPRECIPITATION COLUMNS")
print(rainfall.columns.tolist())

print("\nMETADATA COLUMNS")
print(metadata.columns.tolist())

print("\nSAMPLE FLOOD EVENTS")
print(floods.head(3).to_string(index=False))

print("\nSAMPLE RAINFALL RECORDS")
print(rainfall.head(3).to_string(index=False))

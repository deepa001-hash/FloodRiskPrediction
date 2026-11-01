
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw"

rainfall = pd.read_csv(
    DATA_PATH / "precipitation_variables_indofloods.csv"
)
flood = pd.read_csv(
    DATA_PATH / "floodevents_indofloods.csv"
)

print("RAINFALL DATA")
print("Rows:", len(rainfall))
print("Unique EventIDs:", rainfall["EventID"].nunique())
print("Duplicate EventIDs:", rainfall["EventID"].duplicated().sum())

print("\nEVENT ID MATCH CHECK")
flood_ids = set(flood["EventID"].dropna())
rainfall_ids = set(rainfall["EventID"].dropna())

print("Flood events:", len(flood_ids))
print("Rainfall events:", len(rainfall_ids))
print("Events in both:", len(flood_ids & rainfall_ids))
print("Flood events without rainfall:", len(flood_ids - rainfall_ids))
print("Rainfall events without flood record:", len(rainfall_ids - flood_ids))

print("\nRAINFALL-EVENT DATE CHECK")
flood["Start Date"] = pd.to_datetime(
    flood["Start Date"], errors="coerce"
)

print("Missing start dates:", flood["Start Date"].isna().sum())
print("Earliest event:", flood["Start Date"].min())
print("Latest event:", flood["Start Date"].max())

print("\nRAINFALL VALUE CHECK")
rainfall_cols = [
    col for col in rainfall.columns
    if col.startswith("T") and col.endswith("d")
]

print("Rainfall columns:", rainfall_cols)
print("Missing rainfall values:",
      rainfall[rainfall_cols].isna().sum().sum())
print("Negative rainfall values:",
      (rainfall[rainfall_cols] < 0).sum().sum())

print("\nRAINFALL SUMMARY")
print(rainfall[rainfall_cols].describe().round(2))

print("\nSCRIPT COMPLETED")

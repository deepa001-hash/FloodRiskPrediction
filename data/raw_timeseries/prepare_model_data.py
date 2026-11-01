
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW = PROJECT_ROOT / "data" / "raw"
PROCESSED = PROJECT_ROOT / "data" / "processed"

PROCESSED.mkdir(parents=True, exist_ok=True)

flood = pd.read_csv(RAW / "floodevents_indofloods.csv")
rainfall = pd.read_csv(
    RAW / "precipitation_variables_indofloods.csv"
)

# Merge by the unique event identifier
df = flood.merge(
    rainfall,
    on="EventID",
    how="inner",
    validate="one_to_one"
)

# Keep the recorded label and rainfall windows
rainfall_cols = [
    f"T{i}d" for i in range(1, 11)
]

model_df = df[
    ["EventID", "Start Date", "Flood Type"] + rainfall_cols
].copy()

# Remove rows without a usable target or rainfall features
model_df = model_df.dropna(
    subset=["Flood Type"] + rainfall_cols
)

output = PROCESSED / "historical_severity_model_data.csv"
model_df.to_csv(output, index=False)

print("Dataset prepared successfully")
print("Shape:", model_df.shape)
print("\nFlood Type counts:")
print(model_df["Flood Type"].value_counts())
print("\nSaved to:", output)
print("\nReminder: this is historical severity data,")
print("not a validated future flood-warning dataset.")

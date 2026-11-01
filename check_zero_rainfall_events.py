
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

rain_cols = [f"T{i}d" for i in range(1, 11)]

# Find records where all ten rainfall values are zero
zero_mask = (df[rain_cols] == 0).all(axis=1)
zero_df = df[zero_mask].copy()

print("\n========== ZERO RAINFALL ANALYSIS ==========")

print("Total all-zero rainfall records:", len(zero_df))

print("\nFlood Type distribution:")
print(zero_df["Flood Type"].value_counts())

print("\nGauge distribution:")
print(zero_df["GaugeID"].value_counts().head(20))

print("\nEvents by year:")
zero_df["Year"] = pd.to_datetime(
    zero_df["Start Date"], errors="coerce"
).dt.year
print(zero_df["Year"].value_counts().sort_index().to_string())

print("\nEvent details:")
print(
    zero_df[
        ["EventID", "GaugeID", "Start Date", "Flood Type",
         "Station", "River Name/ Tributory/ SubTributory"]
    ].to_string(index=False)
)

print("\n========== COMPLETE ==========")

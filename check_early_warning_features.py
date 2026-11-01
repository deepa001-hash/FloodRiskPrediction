
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

print("\n========== DATASET INFORMATION ==========")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\n========== AVAILABLE COLUMNS ==========")
for col in df.columns:
    print("-", col)

print("\n========== DATE INFORMATION ==========")
for col in ["Start Date", "End Date", "Start_date", "End_date"]:
    if col in df.columns:
        print(f"\n{col}:")
        print("Minimum:", df[col].min())
        print("Maximum:", df[col].max())

print("\n========== RAINFALL FEATURES ==========")
rainfall_cols = [f"T{i}d" for i in range(1, 11)]
print(df[rainfall_cols].describe())

print("\n========== TARGET DISTRIBUTION ==========")
print(df["Flood Type"].value_counts(dropna=False))

print("\n========== GAUGE INFORMATION ==========")
if "GaugeID" in df.columns:
    print("Unique gauges:", df["GaugeID"].nunique())
    print("Events per gauge:")
    print(df["GaugeID"].value_counts().describe())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum().to_string())

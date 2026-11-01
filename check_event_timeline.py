
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

# Convert event dates
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")

print("\n========== EVENT DATE CHECK ==========")
print("Invalid start dates:", df["Start Date"].isna().sum())
print("Invalid end dates:", df["End Date"].isna().sum())
print("End before start:",
      (df["End Date"] < df["Start Date"]).sum())

print("\n========== EVENT ID CHECK ==========")
print("Unique EventIDs:", df["EventID"].nunique())
print("Duplicate EventIDs:", df["EventID"].duplicated().sum())

print("\n========== GAUGE DISTRIBUTION ==========")
gauge_summary = df.groupby("GaugeID").agg(
    Total_Events=("EventID", "count"),
    First_Event=("Start Date", "min"),
    Last_Event=("Start Date", "max")
)

print("Number of gauges:", len(gauge_summary))
print("\nGauges with the most events:")
print(
    gauge_summary.sort_values(
        "Total_Events", ascending=False
    ).head(15).to_string()
)

print("\n========== RAINFALL FEATURE CHECK ==========")
rain_cols = [f"T{i}d" for i in range(1, 11)]

# Check whether rainfall values are generally cumulative
for col in rain_cols:
    print(
        col,
        "Mean:", round(df[col].mean(), 2),
        "Median:", round(df[col].median(), 2)
    )

print("\n========== DATE COLUMN COMPARISON ==========")
for col in ["Start Date", "Start_date", "End Date", "End_date"]:
    if col in df.columns:
        print(
            col,
            "Minimum:", df[col].min(),
            "Maximum:", df[col].max()
        )

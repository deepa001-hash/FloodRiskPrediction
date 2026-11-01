
import pandas as pd
from pathlib import Path

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
FILE = (
    BASE_DIR / "data" / "raw_timeseries"
    / "rwl_tel_hr_maharashtra_sw_006_2021_2025.csv"
)

cols = [
    "Station",
    "River",
    "District",
    "Data Acquisition Time",
    "River Water Level Telemetry Hourly (meter)",
    "MeanSeaLevel",
    "RL_of_zeroGauge",
]

df = pd.read_csv(FILE, usecols=cols, low_memory=False)

time_col = "Data Acquisition Time"
level_col = "River Water Level Telemetry Hourly (meter)"

df[time_col] = pd.to_datetime(
    df[time_col], format="%d-%m-%Y %H:%M", errors="coerce"
)
df[level_col] = pd.to_numeric(df[level_col], errors="coerce")

print("Total records:", len(df))
print("Unique stations:", df["Station"].nunique())
print("Unique rivers:", df["River"].nunique())
print("Invalid timestamps:", df[time_col].isna().sum())
print("Invalid water levels:", df[level_col].isna().sum())

print("\nRecords per station:")
print(
    df.groupby("Station").size()
      .sort_values(ascending=False)
      .head(15).to_string()
)

print("\nWater-level summary:")
print(df[level_col].describe().to_string())

print("\nLowest 10 readings:")
print(
    df.nsmallest(10, level_col)[
        ["Station", time_col, level_col, "MeanSeaLevel",
         "RL_of_zeroGauge"]
    ].to_string(index=False)
)

print("\nHighest 10 readings:")
print(
    df.nlargest(10, level_col)[
        ["Station", time_col, level_col, "MeanSeaLevel",
         "RL_of_zeroGauge"]
    ].to_string(index=False)
)

print("\nSample station summaries:")
print(
    df.groupby("Station")[level_col]
      .agg(["count", "min", "median", "max"])
      .sort_values("count", ascending=False)
      .head(10).to_string()
)

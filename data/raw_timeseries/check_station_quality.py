
import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction")

FILE = (
    BASE_DIR / "data" / "raw_timeseries"
    / "rwl_tel_hr_maharashtra_sw_006_2021_2025.csv"
)

df = pd.read_csv(
    FILE,
    usecols=[
        "Station",
        "River",
        "District",
        "Data Acquisition Time",
        "River Water Level Telemetry Hourly (meter)",
        "MeanSeaLevel",
        "RL_of_zeroGauge",
    ],
    low_memory=False,
)

time_col = "Data Acquisition Time"
level_col = "River Water Level Telemetry Hourly (meter)"

df[time_col] = pd.to_datetime(
    df[time_col],
    format="%d-%m-%Y %H:%M",
    errors="coerce",
)

df[level_col] = pd.to_numeric(df[level_col], errors="coerce")

# Identify repeated sentinel values
print("\n=== SPECIAL VALUE CHECK ===")
print("Readings equal to -99.999:", (df[level_col] == -99.999).sum())
print("MeanSeaLevel equal to zero:", (df["MeanSeaLevel"] == 0).sum())

print("\n=== UNIQUE RIVERS ===")
print(df["River"].value_counts(dropna=False).to_string())

print("\n=== READINGS PER STATION ===")
print("Stations:", df["Station"].nunique())

# Calculate statistics separately for every station
station_stats = (
    df.groupby(["Station", "River", "District"], dropna=False)
    .agg(
        records=(level_col, "size"),
        minimum=(level_col, "min"),
        median=(level_col, "median"),
        maximum=(level_col, "max"),
        mean_sea_level=("MeanSeaLevel", "median"),
        zero_gauge=("RL_of_zeroGauge", "median"),
    )
    .reset_index()
)

print("\n=== STATION SUMMARY: LOWEST MEDIANS ===")
print(
    station_stats.sort_values("median")
    .head(15).to_string(index=False)
)

print("\n=== STATION SUMMARY: HIGHEST MAXIMUMS ===")
print(
    station_stats.sort_values("maximum", ascending=False)
    .head(15).to_string(index=False)
)

# Inspect timestamps and intervals for the most frequently recorded station
station = df["Station"].value_counts().index[0]
one = df[df["Station"] == station].copy()
one = one.sort_values(time_col)

intervals = one[time_col].diff().dropna().dt.total_seconds() / 60

print(f"\n=== TIMESTAMP INTERVALS: {station} ===")
print(intervals.describe().to_string())
print("\nMost common intervals in minutes:")
print(intervals.value_counts().head(10).to_string())

# Save station-level summary for later investigation
output = BASE_DIR / "data" / "processed" / "station_quality_summary.csv"
output.parent.mkdir(parents=True, exist_ok=True)
station_stats.to_csv(output, index=False)

print(f"\nStation summary saved to: {output}")

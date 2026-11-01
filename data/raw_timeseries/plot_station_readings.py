
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
        "Data Acquisition Time",
        "River Water Level Telemetry Hourly (meter)",
    ],
)

df["Data Acquisition Time"] = pd.to_datetime(
    df["Data Acquisition Time"],
    format="%d-%m-%Y %H:%M",
    errors="coerce",
)

level_col = "River Water Level Telemetry Hourly (meter)"

df[level_col] = pd.to_numeric(df[level_col], errors="coerce")

station = df[df["Station"] == "Kashyapi Dam"].copy()
station = station.sort_values("Data Acquisition Time")

# Inspect the transition from low readings to readings above 600
transition = station[
    (station[level_col] < 100)
    | (station[level_col] > 600)
]

print("=== FIRST 15 LOW READINGS ===")
print(
    station[station[level_col] < 100]
    .head(15)
    .to_string(index=False)
)

print("\n=== LAST 15 LOW READINGS ===")
print(
    station[station[level_col] < 100]
    .tail(15)
    .to_string(index=False)
)

print("\n=== FIRST 15 READINGS ABOVE 600 ===")
print(
    station[station[level_col] > 600]
    .head(15)
    .to_string(index=False)
)

print("\n=== RECORD COUNT BY VALUE RANGE ===")
print(
    pd.cut(
        station[level_col],
        bins=[-float("inf"), 100, 600, 700, float("inf")],
        labels=["Below 100", "100–600", "600–700", "Above 700"],
    ).value_counts().to_string()
)

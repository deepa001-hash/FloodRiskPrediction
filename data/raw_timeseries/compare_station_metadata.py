
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
        "Agency",
        "Is_DischargeDataAvailable",
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

for name in ["Kashyapi Dam", "Ozarkhed Dam"]:
    station = df[df["Station"] == name].sort_values(time_col)

    print(f"\n{'=' * 20} {name} {'=' * 20}")
    print("Records:", len(station))

    for column in [
        "River",
        "District",
        "Agency",
        "MeanSeaLevel",
        "RL_of_zeroGauge",
        "Is_DischargeDataAvailable",
    ]:
        print(f"\n{column}:")
        print(station[column].value_counts(dropna=False).head(10).to_string())

    print("\nReadings around 30 December 2021:")
    sample = station[
        (station[time_col] >= "2021-12-29")
        & (station[time_col] <= "2021-12-31 23:59:59")
    ]

    print(
        sample[
            [
                time_col,
                level_col,
                "MeanSeaLevel",
                "RL_of_zeroGauge",
            ]
        ].to_string(index=False)
    )

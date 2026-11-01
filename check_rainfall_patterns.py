
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

rain_cols = [f"T{i}d" for i in range(1, 11)]

print("\nAverage rainfall for each Flood Type:\n")

print(
    df.groupby("Flood Type")[rain_cols]
    .mean()
    .round(2)
    .T
)

print("\nMedian rainfall for each Flood Type:\n")

print(
    df.groupby("Flood Type")[rain_cols]
    .median()
    .round(2)
    .T
)

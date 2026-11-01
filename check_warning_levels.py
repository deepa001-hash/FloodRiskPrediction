
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

for col in ["Peak Flood Level (m)", "Danger Level"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=["Peak Flood Level (m)", "Danger Level", "Flood Type"]
).copy()

df["Crossed_Danger"] = (
    df["Peak Flood Level (m)"] >= df["Danger Level"]
)

print("\nFlood Type vs Danger Level:")
print(pd.crosstab(
    df["Flood Type"],
    df["Crossed_Danger"],
    margins=True
))

print("\nPercentage crossing danger level by Flood Type:")
print(
    df.groupby("Flood Type")["Crossed_Danger"]
    .mean()
    .mul(100)
    .round(2)
)

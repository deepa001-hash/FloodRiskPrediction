import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "precipitation_variables_indofloods.csv"
)

df = pd.read_csv(FILE)

rain_cols = [f"T{i}d" for i in range(1, 11)]

for col in rain_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["GaugeID"] = df["EventID"].str.rsplit("-", n=1).str[0]

df["All_Zero"] = df[rain_cols].eq(0).all(axis=1)

result = df.groupby("GaugeID").agg(
    Total_Records=("EventID", "count"),
    Zero_Records=("All_Zero", "sum")
)

result["Zero_Percentage"] = (
    result["Zero_Records"] / result["Total_Records"] * 100
)

result = result[result["Zero_Records"] > 0]
result = result.sort_values("Zero_Percentage", ascending=False)

print("\n========== ZERO RAINFALL PERCENTAGE BY GAUGE ==========")
print(result.round(2).to_string())

print("\n========== COMPLETE ==========")
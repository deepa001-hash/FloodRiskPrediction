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

all_zero = df[rain_cols].eq(0).all(axis=1)

print("\n========== ORIGINAL RAINFALL CSV CHECK ==========")
print("Total rainfall records:", len(df))
print("All-zero records:", int(all_zero.sum()))

print("\nMissing values in rainfall columns:")
print(df[rain_cols].isna().sum())

print("\nFirst 10 all-zero records:")
print(
    df.loc[all_zero, ["EventID"] + rain_cols]
    .head(10)
    .to_string(index=False)
)

print("\n========== TEST COMPLETED ==========")
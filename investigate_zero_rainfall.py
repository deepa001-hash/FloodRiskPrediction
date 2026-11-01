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
zero_df = df.loc[all_zero].copy()

# Extract gauge and event number from EventID
zero_df["GaugeID"] = zero_df["EventID"].str.rsplit("-", n=1).str[0]

# Extract year from EventID's matching event data is not possible here,
# so display the original IDs and gauge counts.
print("\n========== ZERO RAINFALL INVESTIGATION ==========")

print("\nZero-rainfall records by gauge:")
print(zero_df["GaugeID"].value_counts().to_string())

print("\nAll-zero records:")
print(zero_df[["EventID", "GaugeID"]].to_string(index=False))

print("\n========== COMPLETE ==========")

import pandas as pd
from pathlib import Path

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "raw_timeseries"

file_path = DATA_DIR / "rwl_tel_hr_maharashtra_sw_006_2021_2025.csv"

df = pd.read_csv(file_path, low_memory=False)

print("Shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head().to_string())

print("\nMissing values per column:")
print(df.isna().sum().to_string())

print("\nDate range:")
date_col = next(
    (c for c in df.columns if "time" in c.lower() or "date" in c.lower()),
    None
)

if date_col:
    dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
    print("Start:", dates.min())
    print("End:", dates.max())
    print("Invalid timestamps:", dates.isna().sum())
else:
    print("No obvious date/time column found.")

print("\nPotential water-level columns:")
for col in df.columns:
    if "level" in col.lower() or "water" in col.lower():
        print(col)

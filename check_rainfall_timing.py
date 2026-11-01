
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

rainfall_cols = [f"T{i}d" for i in range(1, 11)]

print("\n========== RAINFALL DATA CHECK ==========")

# Check missing and negative rainfall values
print("\nMissing rainfall values:")
print(df[rainfall_cols].isnull().sum())

print("\nNegative rainfall values:")
print((df[rainfall_cols] < 0).sum())

# Check cumulative rainfall consistency
print("\nCumulative rainfall consistency:")

for i in range(1, 10):
    current_col = f"T{i}d"
    next_col = f"T{i+1}d"

    inconsistent = (
        df[next_col] < df[current_col]
    ).sum()

    print(
        f"{next_col} < {current_col}: {inconsistent} records"
    )

# Check how much rainfall is zero
print("\nZero rainfall records:")

for col in rainfall_cols:
    zero_count = (df[col] == 0).sum()
    print(f"{col}: {zero_count}")

# Display sample records
print("\n========== SAMPLE RECORDS ==========")

print(
    df[
        ["EventID", "Start Date", "Flood Type"] + rainfall_cols
    ].head(15).to_string(index=False)
)

print("\n========== CHECK COMPLETE ==========")

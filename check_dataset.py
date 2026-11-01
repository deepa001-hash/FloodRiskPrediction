
import pandas as pd
from pathlib import Path

file_path = Path("flood_ml_dataset.csv")

if not file_path.exists():
    raise FileNotFoundError(
        f"Cannot find {file_path.resolve()}. "
        "Check your project's working directory."
    )

df = pd.read_csv(file_path)

print("=" * 60)
print("DATASET QUALITY CHECK")
print("=" * 60)

print("\n1. Dataset shape:")
print(df.shape)

print("\n2. Column names:")
print(df.columns.tolist())

print("\n3. Missing values per column:")
missing = df.isnull().sum()
print(missing[missing > 0] if missing.any() else "No missing values")

print("\n4. Duplicate rows:")
print(df.duplicated().sum())

print("\n5. Duplicate EventIDs:")
if "EventID" in df.columns:
    print(df["EventID"].duplicated().sum())
else:
    print("EventID column not found")

print("\n6. Target distribution:")
if "Flood Type" in df.columns:
    print(df["Flood Type"].value_counts())
    print("\nTarget percentages:")
    print((df["Flood Type"].value_counts(normalize=True) * 100).round(2))
else:
    print("'Flood Type' column not found")

print("\n7. Numeric column summary:")
print(df.select_dtypes(include="number").describe().round(2).to_string())

print("\n8. Data types:")
print(df.dtypes.to_string())

print("\n" + "=" * 60)
print("QUALITY CHECK COMPLETED")
print("=" * 60)

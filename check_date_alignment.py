
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

date_cols = ["Start Date", "Start_date", "End Date", "End_date"]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")

print("\n========== DATE DIFFERENCE ANALYSIS ==========")

df["Start_Date_Difference"] = (
    df["Start Date"] - df["Start_date"]
).dt.days

df["End_Date_Difference"] = (
    df["End Date"] - df["End_date"]
).dt.days

print("\nStart Date difference:")
print(df["Start_Date_Difference"].describe())

print("\nEnd Date difference:")
print(df["End_Date_Difference"].describe())

print("\nRows where Start Date and Start_date differ:")
print(
    df.loc[
        df["Start_Date_Difference"] != 0,
        ["EventID", "GaugeID", "Start Date", "Start_date",
         "Start_Date_Difference"]
    ].head(15).to_string(index=False)
)

print("\n========== RAINFALL EXAMPLES ==========")
print(
    df[["EventID", "Start Date"] +
       [f"T{i}d" for i in range(1, 11)]].head(10).to_string(index=False)
)

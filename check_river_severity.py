
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

river_col = "River Name/ Tributory/ SubTributory"

# Count records for each river
river_counts = df.groupby(river_col).agg(
    Total_Events=("Flood Type", "count"),
    Severe_Events=("Flood Type", lambda x: (x == "Severe Flood").sum())
)

river_counts["Severe_Percentage"] = (
    river_counts["Severe_Events"] /
    river_counts["Total_Events"] * 100
).round(2)

# Keep rivers with at least 30 events
river_counts = river_counts[
    river_counts["Total_Events"] >= 30
]

print("\nRiver-wise flood severity:")
print(
    river_counts.sort_values(
        "Total_Events", ascending=False
    ).head(20).to_string()
)


import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "raw"

events = pd.read_csv(DATA_DIR / "floodevents_indofloods.csv")
metadata = pd.read_csv(DATA_DIR / "metadata_indofloods.csv")

events["GaugeID"] = events["EventID"].str.replace(
    r"-\d+$", "", regex=True
)

merged = events.merge(
    metadata[["GaugeID", "Danger Level"]],
    on="GaugeID",
    how="left"
)

merged["Expected Type"] = (
    merged["Peak Flood Level (m)"] > merged["Danger Level"]
).map({
    True: "Severe Flood",
    False: "Flood"
})

valid = merged.dropna(
    subset=["Peak Flood Level (m)", "Danger Level", "Flood Type"]
).copy()

valid["Matches Rule"] = (
    valid["Flood Type"] == valid["Expected Type"]
)

print("Events with usable levels:", len(valid))
print("Labels matching documented rule:",
      int(valid["Matches Rule"].sum()))
print("Labels not matching rule:",
      int((~valid["Matches Rule"]).sum()))

print("\nMismatched records:")
print(
    valid.loc[
        ~valid["Matches Rule"],
        ["EventID", "Peak Flood Level (m)",
         "Danger Level", "Flood Type", "Expected Type"]
    ].head(20).to_string(index=False)
)


import pandas as pd
from pathlib import Path

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

valid = merged.dropna(
    subset=["Peak Flood Level (m)", "Danger Level", "Flood Type"]
).copy()

valid["Expected Type"] = (
    valid["Peak Flood Level (m)"] >= valid["Danger Level"]
).map({
    True: "Severe Flood",
    False: "Flood"
})

valid["Matches Rule"] = valid["Flood Type"] == valid["Expected Type"]

print("Events checked:", len(valid))
print("Matching labels:", int(valid["Matches Rule"].sum()))
print("Mismatched labels:", int((~valid["Matches Rule"]).sum()))

print("\nMismatches:")
print(
    valid.loc[
        ~valid["Matches Rule"],
        ["EventID", "Peak Flood Level (m)",
         "Danger Level", "Flood Type", "Expected Type"]
    ].to_string(index=False)
)

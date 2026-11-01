
import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(DATA_DIR / "floodevents_indofloods.csv")
metadata = pd.read_csv(DATA_DIR / "metadata_indofloods.csv")

flood["GaugeID"] = flood["EventID"].str.extract(r"(gauge-\d+)-")
metadata["GaugeID"] = metadata["GaugeID"].astype(str).str.extract(
    r"(gauge-\d+)"
)

checked = flood.merge(
    metadata[["GaugeID", "Station", "State", "Danger Level", "Reliability"]],
    on="GaugeID",
    how="left"
)

valid = checked.dropna(
    subset=["Peak Flood Level (m)", "Danger Level", "Flood Type"]
).copy()

valid["Expected Type"] = valid["Peak Flood Level (m)"].gt(
    valid["Danger Level"]
).map({True: "Severe Flood", False: "Flood"})

mismatches = valid[valid["Flood Type"] != valid["Expected Type"]]

print("Number of mismatches:", len(mismatches))
print(
    mismatches[
        [
            "EventID",
            "Station",
            "State",
            "Peak Flood Level (m)",
            "Danger Level",
            "Flood Type",
            "Reliability",
        ]
    ].to_string(index=False)
)

# Test two possible rules for defining Severe Flood

valid["Expected Type >"] = (
    valid["Peak Flood Level (m)"] >
    valid["Danger Level"]
).map({True: "Severe Flood", False: "Flood"})

valid["Expected Type >="] = (
    valid["Peak Flood Level (m)"] >=
    valid["Danger Level"]
).map({True: "Severe Flood", False: "Flood"})

print("\nMatches using > rule:",
      (valid["Flood Type"] == valid["Expected Type >"]).sum(),
      "out of", len(valid))

print("Matches using >= rule:",
      (valid["Flood Type"] == valid["Expected Type >="]).sum(),
      "out of", len(valid))

print("\nMismatches using >= rule:")
print(
    valid[valid["Flood Type"] != valid["Expected Type >="]][
        ["EventID", "Peak Flood Level (m)",
         "Danger Level", "Flood Type"]
    ].to_string(index=False)
)

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(DATA_DIR / "floodevents_indofloods.csv")
rain = pd.read_csv(DATA_DIR / "precipitation_variables_indofloods.csv")

data = flood.merge(rain, on="EventID", how="inner")

print("Flood type counts:")
print(data["Flood Type"].value_counts())

print("\nAverage rainfall variables by flood type:")
print(
    data.groupby("Flood Type")[
        [f"T{i}d" for i in range(1, 11)]
    ].mean().round(2)
)

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

columns = [f"T{i}d" for i in range(2, 11)]

violations = 0

for i in range(len(columns) - 1):
    earlier = columns[i]
    later = columns[i + 1]

    count = (rain[earlier] > rain[later]).sum()
    violations += count

    print(f"{earlier} > {later}: {count} rows")

print("\nTotal adjacent-window violations:", violations)

print("\nRainfall data summary:")
print(rain[[f"T{i}d" for i in range(1, 11)]].describe().round(2))

print("\nNegative rainfall values:")
rain_columns = [f"T{i}d" for i in range(1, 11)]
print((rain[rain_columns] < 0).sum())

print("\nZero rainfall values:")
print((rain[rain_columns] == 0).sum())

print("\nTop 10 events by T10d rainfall:")

top_rainfall = rain.nlargest(10, "T10d")

print(
    top_rainfall[
        ["EventID"] + [f"T{i}d" for i in range(1, 11)]
    ].to_string(index=False)
)

from pathlib import Path
import pandas as pd

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

metadata = pd.read_csv(
    DATA_DIR / "metadata_indofloods.csv"
)

top = rain.nlargest(10, "T10d").copy()

top["GaugeID"] = top["EventID"].str.extract(
    r"(gauge-\d+)"
)

metadata["GaugeID"] = metadata["GaugeID"].astype(str).str.extract(
    r"(gauge-\d+)"
)

result = top.merge(
    metadata[
        ["GaugeID", "Station", "State", "Reliability",
         "Latitude", "Longitude"]
    ],
    on="GaugeID",
    how="left"
)

print(
    result[
        ["EventID", "Station", "State", "Reliability",
         "T10d", "Latitude", "Longitude"]
    ].to_string(index=False)
)

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

top = rain.nlargest(10, "T10d")

result = top.merge(
    flood[["EventID", "Start Date", "End Date"]],
    on="EventID",
    how="left"
)

result["Start Date"] = pd.to_datetime(
    result["Start Date"], errors="coerce"
)

print("\nDates of the top 10 rainfall events:")
print(
    result[
        ["EventID", "Start Date", "End Date", "T10d"]
    ].to_string(index=False)
)

print("\nMonth counts:")
print(result["Start Date"].dt.month.value_counts().sort_index())

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

print("\nT10d rainfall distribution:")
print(
    rain["T10d"].describe(
        percentiles=[0.50, 0.90, 0.95, 0.99, 0.995]
    )
)

print("\nLargest 20 T10d values:")
print(
    rain[["EventID", "T10d"]]
    .nlargest(20, "T10d")
    .to_string(index=False)
)

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

# Combine flood labels with rainfall features
df = flood[["EventID", "Flood Type"]].merge(
    rain,
    on="EventID",
    how="inner",
    validate="one_to_one"
)

# Define candidate input features and target
features = [f"T{i}d" for i in range(1, 11)]
target = "Flood Type"

print("Dataset shape:", df.shape)
print("\nInput features:")
print(features)

print("\nTarget distribution:")
print(df[target].value_counts(dropna=False))

print("\nMissing values in input features:")
print(df[features].isna().sum())

print("\nMissing target labels:", df[target].isna().sum())

print("\nPreview:")
print(df[["EventID"] + features + [target]].head())

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

# Extract the gauge ID from each event ID
flood["GaugeID"] = flood["EventID"].str.extract(
    r"^(.*)-\d+$"
)

print("Total events:", len(flood))
print("Unique gauges:", flood["GaugeID"].nunique())
print("Events per gauge:")
print(flood["GaugeID"].value_counts().describe())

print("\nGauges with the most recorded events:")
print(flood["GaugeID"].value_counts().head(10))

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

flood["GaugeID"] = flood["EventID"].str.extract(
    r"^(.*)-\d+$"
)

events_per_gauge = flood["GaugeID"].value_counts()

print("Total events:", len(flood))
print("Unique gauges:", flood["GaugeID"].nunique())
print("Gauges with more than one event:",
      (events_per_gauge > 1).sum())
print("Gauges with only one event:",
      (events_per_gauge == 1).sum())
print("Events from the 10 most frequent gauges:",
      events_per_gauge.head(10).sum())

import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

flood = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv"
)

flood["Start Date"] = pd.to_datetime(
    flood["Start Date"], errors="coerce"
)

print("Missing or invalid start dates:",
      flood["Start Date"].isna().sum())

print("Earliest event:",
      flood["Start Date"].min())

print("Latest event:",
      flood["Start Date"].max())

print("\nEvents by year:")
print(
    flood["Start Date"]
    .dt.year
    .value_counts()
    .sort_index()
)

print("\nEvents without valid dates:")
print(
    flood.loc[
        flood["Start Date"].isna(),
        ["EventID", "Start Date"]
    ].head(10)
)

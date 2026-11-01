import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

# Locate files by their names
event_files = list(DATA_DIR.glob("*floodevents*"))
rain_files = list(DATA_DIR.glob("*precipitation*"))
metadata_files = list(DATA_DIR.glob("*metadata*"))

print("Event files:", event_files)
print("Rainfall files:", rain_files)
print("Metadata files:", metadata_files)

if not event_files or not rain_files or not metadata_files:
    raise FileNotFoundError(
        "Could not locate all three CSV files. "
        "Check the filenames and data/raw folder."
    )

events = pd.read_csv(event_files[0], low_memory=False)
rainfall = pd.read_csv(rain_files[0], low_memory=False)
metadata = pd.read_csv(metadata_files[0], low_memory=False)

# Basic dataset information
for name, df in [
    ("FLOOD EVENTS", events),
    ("RAINFALL", rainfall),
    ("GAUGE METADATA", metadata),
]:
    print(f"\n{'=' * 20} {name} {'=' * 20}")
    print("Shape:", df.shape)
    print("Duplicate rows:", df.duplicated().sum())
    print("Missing values:")
    print(df.isna().sum().sort_values(ascending=False).head(15))

# Check the classification target
if "Flood Type" in events.columns:
    print("\n=== FLOOD TYPE DISTRIBUTION ===")
    print(events["Flood Type"].value_counts(dropna=False))

# Check EventID relationships
print("\n=== EVENT ID CHECK ===")
print("Unique event IDs:", events["EventID"].nunique())
print("Duplicate event IDs:", events["EventID"].duplicated().sum())
print("Rainfall unique event IDs:", rainfall["EventID"].nunique())

print(
    "Events without rainfall:",
    (~events["EventID"].isin(rainfall["EventID"])).sum()
)
print(
    "Rainfall records without events:",
    (~rainfall["EventID"].isin(events["EventID"])).sum()
)

# Check the metadata station key
if "GaugeID" in metadata.columns:
    print("\n=== GAUGE METADATA CHECK ===")
    print("Unique GaugeIDs:", metadata["GaugeID"].nunique())
    print("Duplicate GaugeIDs:", metadata["GaugeID"].duplicated().sum())

print("\nInspection completed.")

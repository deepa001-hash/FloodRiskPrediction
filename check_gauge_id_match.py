
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

events = pd.read_csv(
    DATA_DIR / "floodevents_indofloods.csv",
    dtype={"EventID": "string"}
)

metadata = pd.read_csv(
    DATA_DIR / "metadata_indofloods.csv",
    dtype={"GaugeID": "string"}
)

# Extract IDs using the current pattern
events["ExtractedGaugeID"] = events["EventID"].str.extract(
    r"gauge-(\d+)-", expand=False
)

# Normalize whitespace only; preserve original values for inspection
event_ids = events["ExtractedGaugeID"].dropna().str.strip()
meta_ids = metadata["GaugeID"].dropna().str.strip()

print("=== EVENT ID EXAMPLES ===")
print(events[["EventID", "ExtractedGaugeID"]].head(15).to_string(index=False))

print("\n=== METADATA GAUGE ID EXAMPLES ===")
print(metadata[["GaugeID", "Station"]].head(20).to_string(index=False))

print("\n=== ID FORMATS ===")
print("Extracted ID dtype:", events["ExtractedGaugeID"].dtype)
print("Metadata ID dtype:", metadata["GaugeID"].dtype)

print("\n=== ID COUNTS ===")
print("Unique extracted IDs:", event_ids.nunique())
print("Unique metadata IDs:", meta_ids.nunique())

print("\n=== SAMPLE UNMATCHED IDS ===")
print("Extracted IDs:", event_ids.head(20).tolist())
print("Metadata IDs:", meta_ids.head(20).tolist())

print("\n=== EXACT MATCH TEST ===")
print("Matching IDs:", len(set(event_ids) & set(meta_ids)))

print("\n=== METADATA IDENTIFIER CHECK ===")
for col in ["GaugeID", "Station"]:
    if col in metadata.columns:
        print(f"\n{col}:")
        print("Unique values:", metadata[col].nunique())
        print("Missing values:", metadata[col].isna().sum())

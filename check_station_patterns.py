
import pandas as pd
from pathlib import Path

file_path = Path(__file__).resolve().parent / "flood_ml_dataset.csv"
df = pd.read_csv(file_path)

# Count flood events by state
print("\nFlood events by State:")
print(df["State"].value_counts().head(15))

# Compare flood types by state
print("\nFlood Type distribution by State:")
print(pd.crosstab(df["State"], df["Flood Type"]).head(15))

# Compare flood types by river
print("\nFlood events by River:")
print(df["River Name/ Tributory/ SubTributory"]
      .value_counts().head(15))


import pandas as pd
from pathlib import Path

DATA_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\raw"
)

OUTPUT_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction\data\processed"
)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

flood = pd.read_csv(DATA_DIR / "floodevents_indofloods.csv")
rain = pd.read_csv(
    DATA_DIR / "precipitation_variables_indofloods.csv"
)

# Keep only the label and event date from flood records
flood["Start Date"] = pd.to_datetime(
    flood["Start Date"], errors="coerce"
)

df = flood[["EventID", "Start Date", "Flood Type"]].merge(
    rain,
    on="EventID",
    how="inner",
    validate="one_to_one"
)

# Use only rainfall features as model inputs
features = [f"T{i}d" for i in range(1, 11)]

# Chronological split
train = df[df["Start Date"] <= "2015-12-31"].copy()
test = df[df["Start Date"] >= "2016-01-01"].copy()

print("Training period: through 2015")
print("Testing period: 2016 onward")
print("Training rows:", len(train))
print("Testing rows:", len(test))

print("\nTraining target distribution:")
print(train["Flood Type"].value_counts())

print("\nTesting target distribution:")
print(test["Flood Type"].value_counts())

print("\nMissing feature values in training:",
      train[features].isna().sum().sum())
print("Missing feature values in testing:",
      test[features].isna().sum().sum())

# Save the prepared datasets
train.to_csv(OUTPUT_DIR / "train_flood_data.csv", index=False)
test.to_csv(OUTPUT_DIR / "test_flood_data.csv", index=False)

print("\nSaved prepared datasets to:", OUTPUT_DIR)

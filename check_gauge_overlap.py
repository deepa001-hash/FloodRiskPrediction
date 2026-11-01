
import pandas as pd
from pathlib import Path
import re

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train_flood_data.csv")
test = pd.read_csv(DATA_DIR / "test_flood_data.csv")

def get_gauge_id(event_id):
    return re.sub(r"-\d+$", "", str(event_id))

train_gauges = set(train["EventID"].map(get_gauge_id))
test_gauges = set(test["EventID"].map(get_gauge_id))

overlap = train_gauges & test_gauges

print("Unique training gauges:", len(train_gauges))
print("Unique testing gauges:", len(test_gauges))
print("Gauges appearing in both:", len(overlap))
print("Gauges only in test:", len(test_gauges - train_gauges))

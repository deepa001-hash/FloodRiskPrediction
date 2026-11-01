
import pandas as pd
import re
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report
)

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train_flood_data.csv")
test = pd.read_csv(DATA_DIR / "test_flood_data.csv")

def get_gauge_id(event_id):
    return re.sub(r"-\d+$", "", str(event_id))

train["GaugeID"] = train["EventID"].map(get_gauge_id)
test["GaugeID"] = test["EventID"].map(get_gauge_id)

seen_gauges = set(train["GaugeID"])

# Split later-period events into familiar and unseen gauges
groups = {
    "Familiar gauges": test[test["GaugeID"].isin(seen_gauges)],
    "Unseen gauges": test[~test["GaugeID"].isin(seen_gauges)]
}

features = [f"T{i}d" for i in range(1, 11)]
X_train = train[features]
y_train = train["Flood Type"]

# Train the Random Forest only on the earlier training period
model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    min_samples_leaf=5
)
model.fit(X_train, y_train)

baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)

print("TRAINING PERIOD: Through 2015")
print("Training events:", len(train))

for group_name, group in groups.items():
    print("\n" + "=" * 50)
    print(group_name)
    print("Events:", len(group))
    print("Unique gauges:", group["GaugeID"].nunique())

    if group.empty:
        print("No events available for this group.")
        continue

    X_test = group[features]
    y_test = group["Flood Type"]

    predictions = model.predict(X_test)
    baseline_predictions = baseline.predict(X_test)

    print("\nRandom Forest")
    print("Accuracy:", round(
        accuracy_score(y_test, predictions), 4
    ))
    print("Balanced accuracy:", round(
        balanced_accuracy_score(y_test, predictions), 4
    ))
    print(classification_report(
        y_test, predictions, zero_division=0
    ))

    print("Majority-class baseline")
    print("Accuracy:", round(
        accuracy_score(y_test, baseline_predictions), 4
    ))
    print("Balanced accuracy:", round(
        balanced_accuracy_score(y_test, baseline_predictions), 4
    ))

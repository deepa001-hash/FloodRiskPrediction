
import pandas as pd
import re
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
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

# Keep only test events from gauges never seen in training
seen_gauges = set(train["GaugeID"])
unseen_test = test[~test["GaugeID"].isin(seen_gauges)].copy()

features = [f"T{i}d" for i in range(1, 11)]

X_train = train[features]
y_train = train["Flood Type"]

X_test = unseen_test[features]
y_test = unseen_test["Flood Type"]

print("Training events:", len(train))
print("Unseen-gauge test events:", len(unseen_test))
print("Unseen gauges:", unseen_test["GaugeID"].nunique())

if len(unseen_test) == 0:
    print("No unseen-gauge events available.")
else:
    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        min_samples_leaf=5
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("\nUNSEEN-GAUGE RESULTS")
    print("Accuracy:", round(
        accuracy_score(y_test, predictions), 4
    ))
    print("Balanced accuracy:", round(
        balanced_accuracy_score(y_test, predictions), 4
    ))

    print("\nClassification report:")
    print(classification_report(
        y_test, predictions, zero_division=0
    ))

    print("Confusion matrix:")
    print(confusion_matrix(
        y_test, predictions, labels=["Flood", "Severe Flood"]
    ))


import pandas as pd
from pathlib import Path
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

features = [f"T{i}d" for i in range(1, 11)]

X_train = train[features]
y_train = train["Flood Type"]

X_test = test[features]
y_test = test["Flood Type"]

model = DummyClassifier(strategy="most_frequent")
model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("BASELINE: Always predict the majority class")
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, predictions), 4
))

print("\nClassification report:")
print(classification_report(
    y_test, predictions, zero_division=0
))

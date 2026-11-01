
import pandas as pd
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

features = [f"T{i}d" for i in range(1, 11)]

X_train = train[features]
y_train = train["Flood Type"]

X_test = test[features]
y_test = test["Flood Type"]

model = RandomForestClassifier(
    n_estimators=200,
    class_weight="balanced",
    random_state=42,
    min_samples_leaf=5
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("MODEL: Random Forest")
print("Training events:", len(train))
print("Testing events:", len(test))

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
print(confusion_matrix(y_test, predictions))

print("\nRainfall feature importance:")
importance = pd.Series(
    model.feature_importances_,
    index=features
).sort_values(ascending=False)

print(importance.round(4))

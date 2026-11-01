
import pandas as pd
from pathlib import Path

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    balanced_accuracy_score
)

BASE_DIR = Path(
    r"C:\Users\Deepa\PycharmProjects\FloodRiskPrediction"
)
DATA_DIR = BASE_DIR / "data" / "processed"

train = pd.read_csv(DATA_DIR / "train_flood_data.csv")
test = pd.read_csv(DATA_DIR / "test_flood_data.csv")

features = [f"T{i}d" for i in range(1, 11)]
target = "Flood Type"

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# Scale features and train a baseline classifier
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=2000, random_state=42)
)

model.fit(X_train, y_train)

# Evaluate only on later events
predictions = model.predict(X_test)

print("MODEL: Logistic Regression")
print("Training events:", len(X_train))
print("Testing events:", len(X_test))

print("\nAccuracy:", round(
    accuracy_score(y_test, predictions), 4
))

print("Balanced accuracy:", round(
    balanced_accuracy_score(y_test, predictions), 4
))

print("\nClassification report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

print("Confusion matrix:")
print(confusion_matrix(
    y_test,
    predictions,
    labels=["Flood", "Severe Flood"]
))

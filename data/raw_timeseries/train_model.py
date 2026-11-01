
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT / "data" / "processed"
    / "historical_severity_model_data.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(DATA_PATH)
df["Start Date"] = pd.to_datetime(
    df["Start Date"], errors="coerce"
)

df = df.dropna(subset=["Start Date", "Flood Type"])
df = df.sort_values("Start Date")

# Features and target
features = [f"T{i}d" for i in range(1, 11)]
X = df[features]
y = df["Flood Type"]

# Chronological split: train through 2015, test from 2016
train_mask = df["Start Date"] < "2016-01-01"
test_mask = df["Start Date"] >= "2016-01-01"

X_train, X_test = X.loc[train_mask], X.loc[test_mask]
y_train, y_test = y.loc[train_mask], y.loc[test_mask]

if len(X_train) == 0 or len(X_test) == 0:
    raise ValueError("Training or test set is empty.")

print("TRAINING ROWS:", len(X_train))
print("TEST ROWS:", len(X_test))
print("Training period:", df.loc[train_mask, "Start Date"].min(),
      "to", df.loc[train_mask, "Start Date"].max())
print("Test period:", df.loc[test_mask, "Start Date"].min(),
      "to", df.loc[test_mask, "Start Date"].max())

# Baseline model
baseline = DummyClassifier(strategy="most_frequent")
baseline.fit(X_train, y_train)
baseline_pred = baseline.predict(X_test)

# Random Forest model
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    min_samples_leaf=3,
    n_jobs=-1
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)

# Evaluation
results = []

for name, actual_predictions in [
    ("Baseline", baseline_pred),
    ("Random Forest", predictions)
]:
    accuracy = accuracy_score(y_test, actual_predictions)
    balanced = balanced_accuracy_score(y_test, actual_predictions)

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Balanced Accuracy": balanced
    })

    print(f"\n--- {name} ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Balanced accuracy: {balanced:.4f}")
    print("\nClassification report:")
    print(classification_report(
        y_test,
        actual_predictions,
        zero_division=0
    ))
    print("Confusion matrix (label order: Flood, Severe Flood):")
    print(confusion_matrix(
        y_test,
        actual_predictions,
        labels=["Flood", "Severe Flood"]
    ))

# Save results and model
results_df = pd.DataFrame(results)
results_df.to_csv(
    RESULTS_DIR / "model_evaluation.csv", index=False
)

joblib.dump(
    {"model": model, "features": features},
    MODEL_DIR / "flood_severity_model.joblib"
)

print("\nResults saved to:", RESULTS_DIR / "model_evaluation.csv")
print("Model saved to:", MODEL_DIR / "flood_severity_model.joblib")
print("\nIMPORTANT: This is historical severity classification,")
print("not a validated future flood early-warning model.")

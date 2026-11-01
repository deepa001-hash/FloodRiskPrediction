
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    recall_score,
    precision_score,
)

# ==================================================
# 1. PROJECT PATHS AND SETTINGS
# ==================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "flood_ml_dataset.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "flood_severity_model.joblib"
THRESHOLD_PATH = MODEL_DIR / "warning_threshold.joblib"

# IMPORTANT: Must match dashboard.py exactly.
FEATURES = [f"T{i}d" for i in range(1, 11)]
LABELS = ["Flood", "Severe Flood"]

TRAIN_END = pd.Timestamp("2013-01-01")
VALIDATION_END = pd.Timestamp("2016-01-01")

# ==================================================
# 2. LOAD AND CHECK DATA
# ==================================================
if not DATA_PATH.is_file():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

required_columns = ["Start Date", "Flood Type"] + FEATURES
missing_columns = [
    column for column in required_columns
    if column not in df.columns
]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

df["Start Date"] = pd.to_datetime(
    df["Start Date"], errors="coerce"
)
df["Flood Type"] = df["Flood Type"].astype("string").str.strip()

df = df.dropna(subset=["Start Date", "Flood Type"]).copy()
df = df[df["Flood Type"].isin(LABELS)].copy()
df = df.sort_values("Start Date").reset_index(drop=True)

if df.empty:
    raise ValueError("No usable rows remain after data cleaning.")

X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
X = X.replace([np.inf, -np.inf], np.nan)
y = df["Flood Type"].astype(str)

print("=" * 65)
print("FLOOD SEVERITY MODEL EVALUATION")
print("=" * 65)
print("Dataset shape:", df.shape)
print("Date range:", df["Start Date"].min(), "to", df["Start Date"].max())
print("\nClass distribution:")
print(y.value_counts())
print("\nMissing rainfall values by feature:")
print(X.isna().sum())

# ==================================================
# 3. CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
# Train: before 2013
# Validation: 2013-2015
# Test: 2016 onward
# ==================================================
train_mask = df["Start Date"] < TRAIN_END
val_mask = (
    (df["Start Date"] >= TRAIN_END)
    & (df["Start Date"] < VALIDATION_END)
)
test_mask = df["Start Date"] >= VALIDATION_END

X_train, y_train = X.loc[train_mask], y.loc[train_mask]
X_val, y_val = X.loc[val_mask], y.loc[val_mask]
X_test, y_test = X.loc[test_mask], y.loc[test_mask]

for name, labels in [
    ("Train", y_train),
    ("Validation", y_val),
    ("Test", y_test),
]:
    print(f"\n{name} events: {len(labels)}")
    print(labels.value_counts())

if min(len(y_train), len(y_val), len(y_test)) == 0:
    raise ValueError(
        "Train, validation, or test split is empty. "
        "Check the dataset dates."
    )

if set(y_train) != set(LABELS):
    raise ValueError(
        "Training data must contain both classes. "
        "Check the date split and class distribution."
    )

if set(y_val) != set(LABELS):
    raise ValueError(
        "Validation data must contain both classes to tune "
        "the threshold reliably. Check the date split."
    )

if set(y_test) != set(LABELS):
    print(
        "\nWARNING: Test data does not contain both classes. "
        "Some evaluation metrics may be incomplete."
    )

# ==================================================
# 4. TRAIN MODEL USING DASHBOARD'S 10 FEATURES
# ==================================================
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("classifier", RandomForestClassifier(
        n_estimators=300,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )),
])

model.fit(X_train, y_train)

severe_index = list(model.classes_).index("Severe Flood")
val_probs = model.predict_proba(X_val)[:, severe_index]
test_probs = model.predict_proba(X_test)[:, severe_index]

# ==================================================
# 5. SELECT THRESHOLD USING VALIDATION DATA ONLY
# ==================================================
thresholds = np.arange(0.20, 0.81, 0.02)
threshold_results = []

for threshold in thresholds:
    val_pred = np.where(
        val_probs >= threshold,
        "Severe Flood",
        "Flood",
    )

    threshold_results.append({
        "threshold": float(threshold),
        "accuracy": accuracy_score(y_val, val_pred),
        "balanced_accuracy": balanced_accuracy_score(y_val, val_pred),
        "severe_precision": precision_score(
            y_val, val_pred,
            pos_label="Severe Flood",
            zero_division=0,
        ),
        "severe_recall": recall_score(
            y_val, val_pred,
            pos_label="Severe Flood",
            zero_division=0,
        ),
    })

threshold_table = pd.DataFrame(threshold_results)

threshold_table = threshold_table.sort_values(
    ["balanced_accuracy", "severe_recall"],
    ascending=[False, False],
).reset_index(drop=True)

best_threshold = float(threshold_table.loc[0, "threshold"])

print("\nSelected validation threshold:", round(best_threshold, 3))
print("\nTop validation thresholds:")
print(threshold_table.head(10).round(3).to_string(index=False))

# ==================================================
# 6. EVALUATE TEST DATA
# Test data is not used to select the threshold.
# ==================================================
evaluation_rows = []

for name, threshold in [
    ("Default threshold", 0.50),
    ("Validation-selected threshold", best_threshold),
]:
    test_pred = np.where(
        test_probs >= threshold,
        "Severe Flood",
        "Flood",
    )

    accuracy = accuracy_score(y_test, test_pred)
    balanced_accuracy = balanced_accuracy_score(y_test, test_pred)
    severe_precision = precision_score(
        y_test, test_pred,
        pos_label="Severe Flood",
        zero_division=0,
    )
    severe_recall = recall_score(
        y_test, test_pred,
        pos_label="Severe Flood",
        zero_division=0,
    )

    evaluation_rows.append({
        "evaluation": name,
        "threshold": float(threshold),
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy,
        "severe_precision": severe_precision,
        "severe_recall": severe_recall,
    })

    print("\n" + "=" * 65)
    print(name)
    print("Threshold:", round(threshold, 3))
    print("=" * 65)
    print(f"Accuracy:           {accuracy:.4f}")
    print(f"Balanced accuracy:  {balanced_accuracy:.4f}")
    print(f"Severe precision:   {severe_precision:.4f}")
    print(f"Severe recall:      {severe_recall:.4f}")

    print("\nClassification report:")
    print(classification_report(
        y_test,
        test_pred,
        labels=LABELS,
        zero_division=0,
    ))

    print("Confusion matrix (actual rows, predicted columns):")
    print(confusion_matrix(
        y_test,
        test_pred,
        labels=LABELS,
    ))

# ==================================================
# 7. SAVE EVALUATION REPORTS
# ==================================================
MODEL_DIR.mkdir(parents=True, exist_ok=True)

threshold_table.to_csv(
    BASE_DIR / "validation_threshold_results.csv",
    index=False,
)

pd.DataFrame(evaluation_rows).to_csv(
    BASE_DIR / "test_evaluation_results.csv",
    index=False,
)

# ==================================================
# 8. SAVE MODEL AND THRESHOLD
# ==================================================
joblib.dump(model, MODEL_PATH)
joblib.dump(best_threshold, THRESHOLD_PATH)

print("\n" + "=" * 65)
print("FILES SAVED")
print("=" * 65)
print("Model:", MODEL_PATH)
print("Threshold:", THRESHOLD_PATH)
print("Validation results:", BASE_DIR / "validation_threshold_results.csv")
print("Test results:", BASE_DIR / "test_evaluation_results.csv")

print("\nEvaluation finished.")
print(
    "This is a flood-severity classifier for recorded events, "
    "not a validated flood-occurrence forecasting system."
)

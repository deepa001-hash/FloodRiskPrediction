
import pandas as pd
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)

# 1. Load dataset
file_path = Path("flood_ml_dataset.csv")
if not file_path.exists():
    raise FileNotFoundError(f"Dataset not found: {file_path.resolve()}")

df = pd.read_csv(file_path)

# 2. Parse dates and sort chronologically
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
df = df.dropna(subset=["Start Date", "Flood Type"])
df = df.sort_values("Start Date").reset_index(drop=True)

# 3. Use rainfall-only features
rainfall_features = [
    f"T{i}d" for i in range(1, 11)
] + ["Max_Rainfall_10d", "Mean_Rainfall_10d"]

X = df[rainfall_features].apply(pd.to_numeric, errors="coerce")
y = df["Flood Type"].astype(str).str.strip()

# 4. Chronological train/test split
split_date = pd.Timestamp("2016-01-01")
train_mask = df["Start Date"] < split_date
test_mask = df["Start Date"] >= split_date

X_train, X_test = X.loc[train_mask], X.loc[test_mask]
y_train, y_test = y.loc[train_mask], y.loc[test_mask]

if X_train.empty or X_test.empty:
    raise ValueError(
        "Train or test set is empty. Check the Start Date values and split date."
    )

print("Train events:", len(X_train))
print("Test events:", len(X_test))
print("Train target distribution:")
print(y_train.value_counts())
print("\nTest target distribution:")
print(y_test.value_counts())

# 5. Define models
models = {
    "Majority baseline": DummyClassifier(strategy="most_frequent"),
    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ]),
    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])
}

# 6. Train and evaluate
results = []

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    balanced_accuracy = balanced_accuracy_score(y_test, predictions)

    results.append({
        "Model": name,
        "Accuracy": round(accuracy, 4),
        "Balanced Accuracy": round(balanced_accuracy, 4)
    })

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)
    print("Accuracy:", round(accuracy, 4))
    print("Balanced accuracy:", round(balanced_accuracy, 4))
    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix (label order: Flood, Severe Flood):")
    print(confusion_matrix(
        y_test,
        predictions,
        labels=["Flood", "Severe Flood"]
    ))

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)
print(pd.DataFrame(results).to_string(index=False))

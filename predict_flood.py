
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# ==================================================
# 1. LOAD SAVED MODEL
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "flood_severity_model.joblib"
THRESHOLD_PATH = MODEL_DIR / "warning_threshold.joblib"

FEATURES = [f"T{i}d" for i in range(1, 11)]

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Model not found. Run early_warning_experiment.py first."
    )

if not THRESHOLD_PATH.exists():
    raise FileNotFoundError(
        "Warning threshold not found. Train the model first."
    )

model = joblib.load(MODEL_PATH)
threshold = float(joblib.load(THRESHOLD_PATH))

if not 0 < threshold < 1:
    raise ValueError("Invalid warning threshold.")

if "Severe Flood" not in model.classes_:
    raise ValueError("The saved model does not contain Severe Flood class.")

# ==================================================
# 2. COLLECT RAINFALL INPUTS
# ==================================================

print("\n" + "=" * 50)
print("       EARLY FLOOD SEVERITY PREDICTION")
print("=" * 50)

print("\nEnter rainfall values in the same units")
print("and time-window format as the training dataset.")

rainfall_values = []

for feature in FEATURES:

    while True:
        try:
            value = float(input(f"Enter {feature}: "))

            if not np.isfinite(value) or value < 0:
                print("Enter a finite, non-negative value.")
                continue

            rainfall_values.append(value)
            break

        except ValueError:
            print("Invalid input. Please enter a number.")

# ==================================================
# 3. VALIDATE CUMULATIVE RAINFALL
# ==================================================

# The dataset analysis found that T1d through T10d
# are cumulative and non-decreasing.
# Reject inconsistent inputs rather than silently
# modifying the user's values.

for i in range(1, len(rainfall_values)):
    if rainfall_values[i] < rainfall_values[i - 1]:
        raise ValueError(
            f"Invalid cumulative rainfall: {FEATURES[i]} "
            f"cannot be lower than {FEATURES[i - 1]}. "
            "Please check your inputs."
        )

# ==================================================
# 4. CREATE MODEL INPUT
# ==================================================

X_input = pd.DataFrame(
    [rainfall_values],
    columns=FEATURES
)

# ==================================================
# 5. MAKE PREDICTION
# ==================================================

probabilities = model.predict_proba(X_input)[0]

severe_index = list(model.classes_).index("Severe Flood")
flood_index = list(model.classes_).index("Flood")

severe_probability = float(probabilities[severe_index])
flood_probability = float(probabilities[flood_index])

if severe_probability >= threshold:
    prediction = "Severe Flood"
else:
    prediction = "Flood"

# ==================================================
# 6. DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 50)
print("                 RESULT")
print("=" * 50)

print("Predicted severity:", prediction)
print(f"Flood probability: {flood_probability:.2%}")
print(f"Severe Flood probability: {severe_probability:.2%}")
print(f"Decision threshold: {threshold:.2f}")

if prediction == "Severe Flood":
    print("\nWARNING: Model indicates higher severe-flood risk.")
    print("Follow official local authority advisories.")
else:
    print("\nModel classifies this event as Flood.")
    print("Continue monitoring official river and rainfall data.")

print("\n" + "=" * 50)
print("IMPORTANT LIMITATIONS")
print("=" * 50)
print("This model classifies the severity of recorded flood events.")
print("It does not predict flood occurrence or guarantee lead time.")
print("It is experimental and is not an official warning system.")
print("Do not use it as the sole basis for evacuation decisions.")


import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from live_monitoring import render_live_monitoring


# ==================================================
# 1. PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "flood_severity_model.joblib"
THRESHOLD_PATH = BASE_DIR / "models" / "warning_threshold.joblib"

FEATURES = [f"T{i}d" for i in range(1, 11)]

RAIN_FALL_FILE = BASE_DIR / "rainfall_inputs.json"


# ==================================================
# 2. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Flood Early Warning Dashboard",
    page_icon="🌧️",
    layout="wide",
)

st.title("🌧️ Flood Early Warning Dashboard")

district = st.selectbox(
    "Select District",
    [
        "Pune",
        "Mumbai",
        "Thane",
        "Nashik",
        "Nagpur",
        "Kolhapur",
        "Satara",
        "Sangli",
        "Raigad",
        "Ratnagiri",
    ],
)

st.caption(
    "Experimental flood-severity classification | Maharashtra"
)

st.warning(
    "This experimental model classifies the severity of recorded "
    "flood events. It does not predict whether a flood will occur "
    "and is not an official warning system. Always follow official "
    "IMD and local authority guidance."
)


# ==================================================
# 3. CHECK MODEL FILES
# ==================================================

if not MODEL_PATH.is_file():
    st.error(f"Model file not found: {MODEL_PATH}")
    st.stop()

if not THRESHOLD_PATH.is_file():
    st.error(f"Threshold file not found: {THRESHOLD_PATH}")
    st.stop()


# ==================================================
# 4. LOAD MODEL AND THRESHOLD
# ==================================================

def find_prediction_model(saved_object):
    """Find a fitted prediction model in a saved object."""

    if hasattr(saved_object, "predict_proba"):
        return saved_object

    if isinstance(saved_object, dict):

        preferred_keys = [
            "model",
            "pipeline",
            "classifier",
            "best_model",
            "estimator",
        ]

        for key in preferred_keys:
            if key in saved_object:
                try:
                    return find_prediction_model(saved_object[key])
                except ValueError:
                    pass

        for value in saved_object.values():
            try:
                return find_prediction_model(value)
            except ValueError:
                pass

    raise ValueError(
        "No model supporting predict_proba() was found."
    )


@st.cache_resource
def load_saved_files():

    saved_object = joblib.load(MODEL_PATH)
    model = find_prediction_model(saved_object)

    threshold_object = joblib.load(THRESHOLD_PATH)

    if isinstance(threshold_object, dict):
        threshold = threshold_object.get(
            "threshold",
            threshold_object.get("best_threshold"),
        )
    else:
        threshold = threshold_object

    if threshold is None:
        raise ValueError(
            "The threshold file does not contain a recognizable threshold."
        )

    threshold = float(threshold)

    if not 0 <= threshold <= 1:
        raise ValueError(
            "The decision threshold must be between 0 and 1."
        )

    if not hasattr(model, "classes_"):
        raise ValueError(
            "The loaded model does not expose its trained classes."
        )

    if "Severe Flood" not in list(model.classes_):
        raise ValueError(
            f"Expected 'Severe Flood' class, but found: {list(model.classes_)}"
        )

    return model, threshold


try:
    model, threshold = load_saved_files()

except Exception as error:
    st.error(f"Could not load the saved model: {error}")
    st.info(
        "Check how the model and threshold are saved in "
        "early_warning_experiment.py."
    )
    st.stop()


# ==================================================
# 5. RAINFALL INPUTS
# ==================================================

st.divider()
st.header("📊 Flood Severity Prediction")

st.subheader("Enter Rainfall Measurements")

if RAIN_FALL_FILE.exists():
    try:
        with open(RAIN_FALL_FILE, "r", encoding="utf-8") as file:
            saved_rainfall = json.load(file)
    except (json.JSONDecodeError, OSError):
        saved_rainfall = {}
else:
    saved_rainfall = {}

st.write(
    "Enter T1d through T10d using the same units and "
    "time-window definitions as the training dataset."
)

with st.form("rainfall_form"):

    input_columns = st.columns(5)
    rainfall_values = []

    for index, feature in enumerate(FEATURES):

        with input_columns[index % 5]:

            rainfall_value = st.number_input(
                feature,
                min_value=0.0,
                value=float(saved_rainfall.get(feature, 0.0)),
                step=1.0,
                format="%.2f",
                key=f"input_{feature}",
            )

            rainfall_values.append(rainfall_value)

    submitted = st.form_submit_button(
        "Analyze Flood Severity"
    )


# ==================================================
# 6. SAVE RAINFALL INPUTS
# ==================================================

if submitted:

    saved_rainfall = {
        feature: float(value)
        for feature, value in zip(FEATURES, rainfall_values)
    }

    with open(RAIN_FALL_FILE, "w", encoding="utf-8") as file:
        json.dump(saved_rainfall, file, indent=4)


# ==================================================
# 7. FLOOD SEVERITY PREDICTION
# ==================================================

if submitted:

    X_input = pd.DataFrame(
        [rainfall_values],
        columns=FEATURES,
    )

    try:
        probabilities = model.predict_proba(X_input)[0]
        classes = list(model.classes_)

        severe_index = classes.index("Severe Flood")
        severe_score = float(probabilities[severe_index])

        prediction = (
            "Severe Flood"
            if severe_score >= threshold
            else "Flood"
        )

    except Exception as error:

        st.error(f"Prediction failed: {error}")

        st.info(
            "The saved model may expect a different input structure. "
            "Check the model training code."
        )

        st.stop()

    # Display prediction results

    st.divider()
    st.subheader("Prediction Results")

    result_col, score_col, threshold_col = st.columns(3)

    result_col.metric(
        "Predicted Class",
        prediction,
    )

    score_col.metric(
        "Severe-Flood Model Score",
        f"{severe_score:.1%}",
    )

    threshold_col.metric(
        "Decision Threshold",
        f"{threshold:.0%}",
    )

    st.progress(
        min(max(severe_score, 0.0), 1.0)
    )

    if prediction == "Severe Flood":

        st.error("🔴 MODEL RESULT: SEVERE FLOOD")

        st.error(
            "The model classified these inputs as Severe Flood. "
            "Check official warnings and follow local authority guidance."
        )

    else:

        st.success("🟢 MODEL RESULT: FLOOD")

        st.info(
            "The model classified these inputs as Flood rather than "
            "Severe Flood. This does not mean conditions are safe."
        )

    # Preparedness guidance

    st.subheader("Preparedness Guidance")

    st.markdown(
        """
        - Monitor official IMD forecasts and local authority updates.
        - Never walk or drive through floodwater.
        - Keep emergency contacts, medicines, and essential documents ready.
        - Identify a safe route to higher ground.
        - Follow evacuation instructions issued by local authorities.
        """
    )

    # Show rainfall inputs

    with st.expander(
        "View entered rainfall values and chart",
        expanded=True,
    ):

        rainfall_table = pd.DataFrame(
            {
                "Time Window": FEATURES,
                "Rainfall Input": rainfall_values,
            }
        )

        st.dataframe(
            rainfall_table,
            use_container_width=True,
        )

        st.subheader("Rainfall Across Time Windows")

        chart_data = rainfall_table.set_index("Time Window")

        st.bar_chart(chart_data)


# ==================================================
# 8. LIVE WEATHER AND RIVER MONITORING
# ==================================================

st.divider()

render_live_monitoring()


# ==================================================
# 9. FOOTER
# ==================================================

st.divider()

st.caption(
    "Research prototype | Not an official flood forecasting "
    "or warning service"
)

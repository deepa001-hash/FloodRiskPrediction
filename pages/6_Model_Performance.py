
import streamlit as st
import pandas as pd

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Model Performance",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Model Performance & Evaluation")

st.write(
    "Evaluation of the experimental Random Forest model "
    "for classifying recorded flood-event severity."
)

st.warning(
    "This model classifies Flood vs Severe Flood among recorded "
    "flood events. It does not predict whether a flood will occur. "
    "Its scores are experimental and are not validated operational "
    "warning probabilities."
)

# ==================================================
# 2. TEST SET PERFORMANCE
# ==================================================

st.divider()
st.header("📊 Test Set Performance")

st.caption(
    "Chronological test set: 605 records from 2016 onward. "
    "Results below use the default decision threshold of 0.50."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Accuracy", "59.34%")
col2.metric("Balanced Accuracy", "58.90%")
col3.metric("Severe Flood Precision", "61.65%")
col4.metric("Severe Flood Recall", "43.20%")

# ==================================================
# 3. CLASSIFICATION REPORT
# ==================================================

st.divider()
st.header("📋 Classification Report")

report = pd.DataFrame({
    "Class": ["Flood", "Severe Flood"],
    "Precision": [0.58, 0.62],
    "Recall": [0.75, 0.43],
    "F1-score": [0.65, 0.51],
    "Support": [311, 294],
})

st.dataframe(
    report.style.format({
        "Precision": "{:.2f}",
        "Recall": "{:.2f}",
        "F1-score": "{:.2f}",
    }),
    use_container_width=True,
    hide_index=True,
)

st.caption("Rounded class-level results from the test classification report.")

# ==================================================
# 4. CONFUSION MATRIX - THRESHOLD 0.50
# ==================================================

st.divider()
st.header("🔍 Confusion Matrix — Threshold 0.50")

st.write(
    "Rows represent actual classes. Columns represent predicted classes."
)

matrix_050 = pd.DataFrame(
    [[232, 79], [167, 127]],
    index=["Actual Flood", "Actual Severe Flood"],
    columns=["Predicted Flood", "Predicted Severe Flood"],
)

st.table(matrix_050)

st.caption(
    "At threshold 0.50, 127 of 294 Severe Flood test records "
    "were correctly classified."
)

# ==================================================
# 5. THRESHOLD COMPARISON
# ==================================================

st.divider()
st.header("⚖️ Decision Threshold Comparison")

st.write(
    "The validation-selected threshold was 0.36. "
    "A lower threshold identifies more records as Severe Flood, "
    "but can also increase false alarms."
)

threshold_comparison = pd.DataFrame({
    "Metric": [
        "Test Accuracy",
        "Test Balanced Accuracy",
        "Severe Flood Precision",
        "Severe Flood Recall",
    ],
    "Threshold 0.50": [
        "59.34%",
        "58.90%",
        "61.65%",
        "43.20%",
    ],
    "Threshold 0.36": [
        "53.55%",
        "54.03%",
        "51.60%",
        "71.09%",
    ],
})

# Use a static table to ensure all three columns are visible.
st.table(threshold_comparison)

# ==================================================
# 6. SEVERE FLOOD RECALL COMPARISON
# ==================================================

st.subheader("Severe Flood Recall Comparison")

recall_chart = pd.DataFrame(
    {
        "Threshold": ["0.50", "0.36"],
        "Severe Flood Recall": [0.4320, 0.7109],
    }
).set_index("Threshold")

st.bar_chart(recall_chart)

# ==================================================
# 7. CONFUSION MATRIX - THRESHOLD 0.36
# ==================================================

st.divider()
st.header("🔍 Confusion Matrix — Threshold 0.36")

matrix_036 = pd.DataFrame(
    [[115, 196], [85, 209]],
    index=["Actual Flood", "Actual Severe Flood"],
    columns=["Predicted Flood", "Predicted Severe Flood"],
)

st.table(matrix_036)

st.caption(
    "At threshold 0.36, 209 of 294 Severe Flood test records "
    "were correctly classified, while more Flood records "
    "were incorrectly classified as Severe Flood."
)

# ==================================================
# 8. MODEL CONFIGURATION
# ==================================================

st.divider()
st.header("⚙️ Model Configuration")

details = pd.DataFrame({
    "Parameter": [
        "Algorithm",
        "Number of trees",
        "Class weighting",
        "Random state",
        "Input features",
        "Training period",
        "Validation period",
        "Test period",
        "Selected threshold",
    ],
    "Value": [
        "Random Forest Classifier",
        "300",
        "Balanced",
        "42",
        "T1d to T10d",
        "Before 2013",
        "2013–2015",
        "2016 onward",
        "0.36",
    ],
})

st.dataframe(details, use_container_width=True, hide_index=True)

# ==================================================
# 9. PERFORMANCE INTERPRETATION
# ==================================================

st.divider()
st.header("🧠 Performance Interpretation")

st.markdown("""
**At threshold 0.50**
- The model correctly identifies more ordinary Flood records.
- Severe Flood recall is 43.20%.

**At threshold 0.36**
- Severe Flood recall increases to 71.09%.
- Severe Flood precision decreases to 51.60%.
- More ordinary Flood records are incorrectly classified as Severe Flood.

**Important:** Neither threshold has been established as suitable
for real-world emergency warnings.
""")

# ==================================================
# 10. MODEL LIMITATIONS
# ==================================================

st.divider()
st.header("⚠️ Model Limitations")

st.markdown("""
1. The available dataset contains recorded flood events,
   without confirmed non-flood observations.
2. The model distinguishes Flood from Severe Flood;
   it does not predict flood occurrence.
3. The evaluation results are experimental.
4. The model scores are not calibrated real-world probabilities.
5. Further geographic and temporal validation is required.
6. Official weather and river-gauge observations are needed
   before operational warning use.
""")

# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "Model Performance & Evaluation | "
    "Experimental research prototype | "
    "Not an operational flood forecasting system"
)

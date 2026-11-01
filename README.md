# Early Flood Prediction, Warning & Prevention

An experimental Streamlit application for classifying the severity of
recorded flood events using rainfall measurements (T1d--T10d).

> **Important:** This project is an experimental flood-severity
> classification prototype. It does **not** predict whether a flood will
> occur, does not establish a reliable warning lead time, and is not an
> official warning system. Do not use it as the sole basis for
> evacuation or other safety decisions. Follow official IMD and
> local-authority guidance.

## Project overview

The application accepts ten rainfall measurements, T1d through T10d, and
uses a trained machine-learning pipeline to classify an input as:

-   `Flood`
-   `Severe Flood`

The Streamlit dashboard and command-line prediction script use the saved
model and decision threshold.

## Main features

-   Interactive Streamlit dashboard
-   Command-line prediction through `predict_flood.py`
-   Random Forest classification pipeline
-   Saved model and warning threshold
-   Test-set evaluation report
-   Input validation for rainfall measurements

## Technology

-   Python
-   Streamlit
-   pandas
-   NumPy
-   scikit-learn
-   joblib

## Project structure

The following is the expected deployment structure. Keep the model files
and evaluation report in the repository if the dashboard loads them at
runtime.

``` text
FloodRiskPrediction/
├── dashboard.py
├── predict_flood.py
├── early_warning_experiment.py
├── prepare_ml_dataset.py
├── requirements.txt
├── .gitignore
├── test_evaluation_results.csv
├── models/
│   ├── flood_severity_model.joblib
│   └── warning_threshold.joblib
└── data/                       # Optional: source/dataset files
```

Your actual folder may contain additional files. Do not upload private
credentials, local environment folders, or unnecessary temporary files.

## Setup

Python 3.14 was used in the development environment. For deployment,
select a Python version supported by the pinned package versions in
`requirements.txt`.

1.  Clone or download this repository.
2.  Open the project folder in a terminal.
3.  Create and activate a virtual environment if needed.
4.  Install dependencies:

``` bash
python -m pip install -r requirements.txt
```

## Run the dashboard

From the project root, run:

``` bash
python -m streamlit run dashboard.py
```

Do not run the dashboard with `python dashboard.py`. Streamlit apps
should be started with the Streamlit command.

## Run command-line prediction

``` bash
python predict_flood.py
```

Enter T1d through T10d when prompted. Use the same units and time-window
definitions as the training dataset.

## Model and evaluation

The experiment trains a Random Forest classifier using T1d--T10d
rainfall features. The pipeline includes median imputation and class
balancing. The data was split chronologically:

-   Training: dates before 2013
-   Validation: 2013--2015
-   Test: 2016 onward

The validation-selected decision threshold was **0.36**.

Reported test results:

  -----------------------------------------------------------------------
  Threshold         Accuracy       Balanced   Severe Flood   Severe Flood
                                   accuracy      precision         recall
  ----------- -------------- -------------- -------------- --------------
  0.50                0.5934         0.5890         0.6165         0.4320

  0.36                0.5355         0.5403         0.5160         0.7109
  -----------------------------------------------------------------------

At threshold 0.36, the model identifies a larger share of Severe Flood
cases in the test set, but also produces more false alarms. These
results are modest and should not be interpreted as evidence of
operational forecasting performance.

## Dataset scope and limitations

The current modelling dataset contains **4,548 recorded flood-event
rows**:

-   `Flood`: 2,919 rows
-   `Severe Flood`: 1,629 rows
-   155 unique gauges
-   Event dates spanning 1965-07-21 to 2020-09-24

The dataset contains recorded flood events and does not provide
confirmed non-flood observations. Therefore, the model learns to
distinguish the two recorded-event severity classes; it cannot estimate
the probability that a flood will occur on a future date or at a
location.

The target label is closely tied to whether the recorded peak flood
level reaches the danger level. Peak flood level and danger level are
not used as model inputs because they are not suitable advance-warning
predictors.

Additional limitations:

-   Model scores are not calibrated real-world flood probabilities.
-   The current test metrics are limited and may not generalize to
    unseen gauges, locations, or future conditions.
-   The district selector in the dashboard is informational and does not
    change the model prediction.
-   The rainfall inputs must match the training dataset's units and
    time-window definitions.
-   A real flood-occurrence warning system would require non-flood
    examples, forecast-time inputs, explicit lead-time targets, and
    stronger temporal and geographic validation.

## Responsible use

This software is for educational and experimental use only. It is not an
official alert service and must not replace weather bulletins,
river-gauge monitoring, emergency services, or instructions from public
authorities.

## Future improvements

-   Add verified non-flood observations.
-   Define prediction horizons and lead-time labels.
-   Incorporate rainfall forecasts, river levels, discharge, and
    catchment characteristics available at prediction time.
-   Evaluate using gauge-held-out and location-held-out testing.
-   Calibrate model probabilities and assess false-alarm rates with
    domain experts.
-   Connect to authoritative data and alert sources only after rigorous
    validation.

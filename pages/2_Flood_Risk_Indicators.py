
import streamlit as st
import pandas as pd
from datetime import datetime

from live_monitoring import (
    LOCATIONS,
    get_weather,
    get_river_data,
)

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="24-Hour Flood Risk Outlook",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 24-Hour Early Flood Risk Outlook")

st.write(
    "Experimental forecast-based monitoring using rainfall "
    "forecasts and modelled river-discharge information."
)

st.warning(
    "This is an experimental screening prototype, not a validated "
    "flood prediction model or official warning system. "
    "Always follow IMD and local authority instructions."
)

# ==================================================
# 2. LOCATION SELECTION
# ==================================================

district = st.selectbox(
    "Select Monitoring Location",
    list(LOCATIONS.keys()),
)

latitude, longitude = LOCATIONS[district]

st.caption(
    f"Location: {district}, Maharashtra | "
    f"Coordinates: {latitude}, {longitude}"
)

if st.button("🔄 Refresh Forecast Data"):
    get_weather.clear()
    get_river_data.clear()
    st.rerun()

# ==================================================
# 3. FETCH DATA
# ==================================================

weather = None
river = None

try:
    weather = get_weather(latitude, longitude)
except Exception as error:
    st.error(f"Weather API error: {error}")

try:
    river = get_river_data(latitude, longitude)
except Exception as error:
    st.error(f"River API error: {error}")

# ==================================================
# 4. CALCULATE 24-HOUR RAINFALL
# ==================================================

forecast_rainfall = None
rainfall_df = pd.DataFrame()
current = {}

if weather:

    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    times = hourly.get("time", [])
    rainfall = hourly.get("precipitation", [])

    rainfall_df = pd.DataFrame({
        "Time": times,
        "Rainfall (mm)": rainfall,
    })

    if not rainfall_df.empty:

        rainfall_df["Time"] = pd.to_datetime(
            rainfall_df["Time"]
        )

        rainfall_df["Rainfall (mm)"] = pd.to_numeric(
            rainfall_df["Rainfall (mm)"],
            errors="coerce",
        )

        api_time = pd.to_datetime(
            current.get("time"),
            errors="coerce",
        )

        if pd.notna(api_time):

            next_24_hours = api_time + pd.Timedelta(hours=24)

            forecast_df = rainfall_df[
                (rainfall_df["Time"] >= api_time)
                & (rainfall_df["Time"] < next_24_hours)
            ].dropna(subset=["Rainfall (mm)"])

            if not forecast_df.empty:
                forecast_rainfall = forecast_df[
                    "Rainfall (mm)"
                ].sum()

# ==================================================
# 5. CALCULATE MODELLED DISCHARGE TREND
# ==================================================

discharge_change = None
latest_discharge = None
previous_discharge = None
river_df = pd.DataFrame()

if river:

    daily = river.get("daily", {})

    river_df = pd.DataFrame({
        "Date": daily.get("time", []),
        "Discharge (m³/s)": daily.get(
            "river_discharge", []
        ),
    })

    if not river_df.empty:

        river_df["Date"] = pd.to_datetime(
            river_df["Date"],
            errors="coerce",
        )

        river_df["Discharge (m³/s)"] = pd.to_numeric(
            river_df["Discharge (m³/s)"],
            errors="coerce",
        )

        river_df = river_df.dropna(
            subset=["Date", "Discharge (m³/s)"]
        ).sort_values("Date")

        if not river_df.empty:

            api_time = pd.to_datetime(
                current.get("time"),
                errors="coerce",
            ) if current else pd.NaT

            if pd.notna(api_time):
                today = api_time.normalize()
            else:
                today = pd.Timestamp.now().normalize()

            past_values = river_df[
                river_df["Date"] < today
            ]

            today_values = river_df[
                river_df["Date"] >= today
            ]

            if not past_values.empty and not today_values.empty:

                previous_discharge = past_values.iloc[-1][
                    "Discharge (m³/s)"
                ]

                latest_discharge = today_values.iloc[0][
                    "Discharge (m³/s)"
                ]

                if previous_discharge > 0:

                    discharge_change = (
                        (latest_discharge - previous_discharge)
                        / previous_discharge
                    ) * 100

# ==================================================
# 6. 24-HOUR RISK SCREENING
# ==================================================

st.divider()
st.header("🚨 24-Hour Early Flood Risk Assessment")

risk_signals = []
risk_level = "Insufficient Data"
risk_reasons = []

# Rainfall screening rules.
# These are illustrative, not locally validated thresholds.

if forecast_rainfall is not None:

    if forecast_rainfall >= 50:
        risk_signals.append(2)
        risk_reasons.append(
            f"High forecast rainfall: {forecast_rainfall:.1f} mm."
        )

    elif forecast_rainfall >= 20:
        risk_signals.append(1)
        risk_reasons.append(
            f"Elevated forecast rainfall: {forecast_rainfall:.1f} mm."
        )

    else:
        risk_signals.append(0)
        risk_reasons.append(
            f"Forecast rainfall: {forecast_rainfall:.1f} mm."
        )

# Modelled discharge trend screening rules.

if discharge_change is not None:

    if discharge_change >= 50:
        risk_signals.append(2)
        risk_reasons.append(
            f"Strong increase in modelled discharge: "
            f"{discharge_change:+.1f}%."
        )

    elif discharge_change >= 25:
        risk_signals.append(1)
        risk_reasons.append(
            f"Increase in modelled discharge: "
            f"{discharge_change:+.1f}%."
        )

    else:
        risk_signals.append(0)
        risk_reasons.append(
            f"Modelled discharge change: "
            f"{discharge_change:+.1f}%."
        )

# Assign the strongest available screening signal.

if risk_signals:

    highest_signal = max(risk_signals)

    if highest_signal == 2:
        risk_level = "HIGH"

    elif highest_signal == 1:
        risk_level = "MODERATE"

    else:
        risk_level = "LOW"

    if risk_level == "HIGH":
        st.error("🔴 HIGH SCREENING LEVEL")

        st.write(
            "One or more forecast indicators have crossed "
            "the experimental high screening thresholds. "
            "Check official weather and local authority updates."
        )

    elif risk_level == "MODERATE":
        st.warning("🟠 MODERATE SCREENING LEVEL")

        st.write(
            "One or more forecast indicators suggest increased "
            "conditions requiring closer monitoring."
        )

    else:
        st.success("🟢 LOW SCREENING LEVEL")

        st.write(
            "The available indicators are below the experimental "
            "screening thresholds. This does not guarantee safety."
        )

    st.subheader("Why was this level assigned?")

    for reason in risk_reasons:
        st.write(f"• {reason}")

else:

    st.warning(
        "Risk assessment unavailable because forecast data "
        "could not be retrieved."
    )

# ==================================================
# 7. FORECAST SUMMARY
# ==================================================

st.divider()
st.header("📊 Forecast Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Location",
    district,
)

col2.metric(
    "24-Hour Forecast Rainfall",
    (
        f"{forecast_rainfall:.1f} mm"
        if forecast_rainfall is not None
        else "Unavailable"
    ),
)

col3.metric(
    "Risk Screening",
    risk_level,
)

col4, col5 = st.columns(2)

if latest_discharge is not None:

    col4.metric(
        "Modelled Discharge",
        f"{latest_discharge:.2f} m³/s",
    )

else:
    col4.metric(
        "Modelled Discharge",
        "Unavailable",
    )

if discharge_change is not None:

    col5.metric(
        "Discharge Change",
        f"{discharge_change:+.1f}%",
    )

else:
    col5.metric(
        "Discharge Change",
        "Unavailable",
    )

# ==================================================
# 8. RAINFALL TREND
# ==================================================

st.divider()
st.header("🌧️ Rainfall Forecast Trend")

if not rainfall_df.empty:

    st.line_chart(
        rainfall_df.set_index("Time")["Rainfall (mm)"]
    )

else:

    st.info("Rainfall trend is unavailable.")

# ==================================================
# 9. RIVER DISCHARGE TREND
# ==================================================

st.divider()
st.header("🌊 Modelled River Discharge Trend")

if not river_df.empty:

    st.line_chart(
        river_df.set_index("Date")["Discharge (m³/s)"]
    )

    st.dataframe(
        river_df,
        use_container_width=True,
    )

else:

    st.info("River discharge trend is unavailable.")

# ==================================================
# 10. PREPAREDNESS GUIDANCE
# ==================================================

st.divider()
st.header("🛡️ Flood Preparedness Guidance")

if risk_level == "HIGH":

    st.markdown(
        """
        - Monitor official IMD rainfall and weather warnings.
        - Follow district disaster-management instructions.
        - Avoid riverbanks, low-lying areas and flooded roads.
        - Keep emergency medicines and important documents ready.
        - Follow official evacuation instructions if issued.
        """
    )

elif risk_level == "MODERATE":

    st.markdown(
        """
        - Continue monitoring rainfall and river conditions.
        - Check official weather and local authority updates.
        - Avoid unnecessary travel through low-lying areas.
        - Keep emergency contacts and essential supplies ready.
        """
    )

elif risk_level == "LOW":

    st.markdown(
        """
        - Continue routine monitoring.
        - Follow official weather updates.
        - Remember that low screening status does not guarantee
          that flooding will not occur.
        """
    )

else:

    st.write(
        "Check official weather forecasts and local authority "
        "updates because sufficient data is not available."
    )

# ==================================================
# 11. METHODOLOGY AND LIMITATIONS
# ==================================================

st.divider()
st.header("ℹ️ Methodology and Limitations")

st.markdown(
    """
    **Data sources**
    - Rainfall forecast: Open-Meteo Weather API.
    - River discharge: Open-Meteo Flood API (GloFAS).

    **Experimental screening thresholds**
    - Rainfall below 20 mm: Low rainfall signal.
    - Rainfall from 20 to below 50 mm: Moderate rainfall signal.
    - Rainfall of 50 mm or more: High rainfall signal.
    - Modelled discharge increase of 25% or more: Moderate signal.
    - Modelled discharge increase of 50% or more: High signal.

    **Important limitations**
    - Thresholds are illustrative and not locally validated.
    - River discharge comparisons use daily modelled estimates,
      not hourly river-gauge measurements.
    - The screening category is not a calibrated flood probability.
    - This feature does not establish that a flood will occur
      within 24 hours.
    - The existing machine-learning model classifies recorded
      flood-event severity; it is not a 24-hour flood-occurrence model.
    """
)

st.caption(
    f"Last page refresh: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | "
    "Experimental research prototype | Not an official warning system."
)

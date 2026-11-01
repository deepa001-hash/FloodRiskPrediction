
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
    page_title="Flood Alerts",
    page_icon="🚨",
    layout="wide",
)

st.title("🚨 Flood Alerts & Notifications")

st.write(
    "Monitor changing rainfall and modelled river discharge "
    "conditions and identify situations requiring attention."
)

st.warning(
    "These are experimental monitoring alerts, not official flood "
    "warnings. The thresholds below are screening rules, not "
    "locally validated danger levels. Follow IMD and local authority "
    "instructions."
)

# ==================================================
# 2. LOCATION
# ==================================================

district = st.selectbox(
    "Select Monitoring Location",
    list(LOCATIONS.keys()),
)

latitude, longitude = LOCATIONS[district]

if st.button("Refresh Alert Data"):
    get_weather.clear()
    get_river_data.clear()

# ==================================================
# 3. FETCH DATA
# ==================================================

weather = None
river = None

try:
    weather = get_weather(latitude, longitude)
except Exception as error:
    st.error(f"Weather data unavailable: {error}")

try:
    river = get_river_data(latitude, longitude)
except Exception as error:
    st.error(f"River data unavailable: {error}")

# ==================================================
# 4. INITIALIZE ALERT HISTORY
# ==================================================

if "flood_alert_history" not in st.session_state:
    st.session_state.flood_alert_history = []

alerts = []

# ==================================================
# 5. RAINFALL ALERT CHECKS
# ==================================================

st.divider()
st.header("🌧️ Rainfall Alerts")

if weather:

    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    current_rain = float(current.get("rain") or 0)
    precipitation = float(current.get("precipitation") or 0)

    rainfall_df = pd.DataFrame({
        "Time": hourly.get("time", []),
        "Rainfall": hourly.get("precipitation", []),
    })

    past_total = None
    forecast_total = None

    if not rainfall_df.empty:

        rainfall_df["Time"] = pd.to_datetime(
            rainfall_df["Time"]
        )

        now = pd.Timestamp.now(
            tz=rainfall_df["Time"].dt.tz
        ) if rainfall_df["Time"].dt.tz is not None else pd.Timestamp.now()

        past = rainfall_df[
            (rainfall_df["Time"] <= now)
            & (rainfall_df["Time"] > now - pd.Timedelta(hours=24))
        ]

        future = rainfall_df[
            (rainfall_df["Time"] > now)
            & (rainfall_df["Time"] <= now + pd.Timedelta(hours=24))
        ]

        past_total = past["Rainfall"].sum()
        forecast_total = future["Rainfall"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Rain", f"{current_rain:.1f} mm")
    col2.metric("Current Precipitation", f"{precipitation:.1f} mm")

    if forecast_total is not None:
        col3.metric(
            "Next 24h Forecast Rain",
            f"{forecast_total:.1f} mm",
        )

    if forecast_total is not None and past_total is not None:

        if forecast_total > past_total:
            alerts.append({
                "type": "Rainfall",
                "level": "Attention",
                "message": (
                    "Forecast rainfall is higher than the previous "
                    "24-hour total."
                ),
            })

        if forecast_total >= 20:
            alerts.append({
                "type": "Rainfall",
                "level": "High Attention",
                "message": (
                    "The experimental 20 mm screening threshold "
                    "for forecast rainfall has been reached."
                ),
            })

    if current_rain > 0:
        st.info("Rain is currently being reported by the weather API.")

else:
    st.warning("Rainfall alert checks could not be completed.")

# ==================================================
# 6. RIVER DISCHARGE ALERT CHECKS
# ==================================================

st.divider()
st.header("🌊 River Discharge Alerts")

if river:

    daily = river.get("daily", {})

    river_df = pd.DataFrame({
        "Date": daily.get("time", []),
        "Discharge": daily.get("river_discharge", []),
    })

    if not river_df.empty:

        river_df["Date"] = pd.to_datetime(river_df["Date"])

        river_df["Discharge"] = pd.to_numeric(
            river_df["Discharge"],
            errors="coerce",
        )

        river_df = river_df.dropna(
            subset=["Discharge"]
        )

        if len(river_df) >= 2:

            first_value = float(
                river_df["Discharge"].iloc[0]
            )

            latest_value = float(
                river_df["Discharge"].iloc[-1]
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "First Available Estimate",
                f"{first_value:.2f} m³/s",
            )

            col2.metric(
                "Last Available Estimate",
                f"{latest_value:.2f} m³/s",
            )

            if first_value > 0:

                change = (
                    (latest_value - first_value)
                    / first_value
                ) * 100

                st.metric(
                    "Change Across Displayed Period",
                    f"{change:+.1f}%",
                )

                if change >= 25:
                    alerts.append({
                        "type": "River Discharge",
                        "level": "High Attention",
                        "message": (
                            "Modelled river discharge increased "
                            "by at least 25% across the displayed period."
                        ),
                    })

                elif change > 0:
                    alerts.append({
                        "type": "River Discharge",
                        "level": "Attention",
                        "message": (
                            "Modelled river discharge increased "
                            "across the displayed period."
                        ),
                    })

                else:
                    st.info(
                        "No increase was observed across the "
                        "displayed discharge period."
                    )

            st.subheader("Discharge Trend")

            st.line_chart(
                river_df.set_index("Date")["Discharge"]
            )

        else:
            st.warning(
                "Not enough river discharge records for comparison."
            )

else:
    st.warning("River discharge alert checks could not be completed.")

# ==================================================
# 7. ALERT SUMMARY
# ==================================================

st.divider()
st.header("📢 Current Alert Summary")

if weather is None or river is None:

    st.warning(
        "Incomplete monitoring data. No overall alert assessment "
        "can be made."
    )

elif not alerts:

    st.success(
        "No experimental screening conditions were triggered "
        "by the available data."
    )

else:

    for alert in alerts:

        if alert["level"] == "High Attention":
            st.error(
                f'🔴 {alert["level"]} — {alert["type"]}: '
                f'{alert["message"]}'
            )
        else:
            st.warning(
                f'🟠 {alert["level"]} — {alert["type"]}: '
                f'{alert["message"]}'
            )

# ==================================================
# 8. PREPAREDNESS GUIDANCE
# ==================================================

st.divider()
st.header("🛡️ Flood Preparedness Guidance")

st.markdown(
    """
    - Monitor official IMD rainfall forecasts.
    - Follow local disaster-management announcements.
    - Avoid crossing flooded roads and bridges.
    - Keep emergency medicines and documents ready.
    - Identify safe routes to higher ground.
    - Follow official evacuation instructions.
    """
)

# ==================================================
# 9. ALERT HISTORY
# ==================================================

st.divider()
st.header("📜 Alert History")

if st.button("Save Current Alert Snapshot"):

    st.session_state.flood_alert_history.append({
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Location": district,
        "Alerts": len(alerts),
        "Details": "; ".join(
            alert["message"] for alert in alerts
        ) if alerts else "No screening conditions triggered",
    })

    st.success("Current alert snapshot saved.")

if st.session_state.flood_alert_history:

    history_df = pd.DataFrame(
        st.session_state.flood_alert_history
    )

    st.dataframe(
        history_df,
        use_container_width=True,
    )

    csv_data = history_df.to_csv(index=False)

    st.download_button(
        "Download Alert History",
        data=csv_data,
        file_name="flood_alert_history.csv",
        mime="text/csv",
    )

else:
    st.info("No alert snapshots saved yet.")

# ==================================================
# 10. FOOTER
# ==================================================

st.divider()

st.caption(
    "Flood Alerts | Experimental research prototype | "
    "Not an official flood warning or emergency notification service."
)


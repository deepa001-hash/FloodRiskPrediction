
import streamlit as st
import pandas as pd
import requests

# -----------------------------------
# LOCATION COORDINATES
# -----------------------------------

LOCATIONS = {
    "Pune": (18.5204, 73.8567),
    "Mumbai": (19.0760, 72.8777),
    "Kolhapur": (16.7050, 74.2433),
    "Sangli": (16.8524, 74.5815),
    "Satara": (17.6805, 74.0183),
    "Nashik": (19.9975, 73.7898),
    "Nagpur": (21.1458, 79.0882),
    "Solapur": (17.6599, 75.9064),
}

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"


# -----------------------------------
# FETCH WEATHER DATA
# -----------------------------------

@st.cache_data(ttl=900)
def get_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "wind_speed_10m"
        ),
        "hourly": "precipitation",
        "forecast_days": 2,
        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=20
    )
    response.raise_for_status()
    return response.json()


# -----------------------------------
# FETCH RIVER DISCHARGE DATA
# -----------------------------------

@st.cache_data(ttl=3600)
def get_river_data(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "river_discharge",
        "forecast_days": 7,
        "past_days": 7,
        "timezone": "auto"
    }

    response = requests.get(
        FLOOD_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


# -----------------------------------
# MAIN MONITORING DASHBOARD
# -----------------------------------

def render_live_monitoring():

    st.title("🌧️ Live Flood Monitoring")

    st.write(
        "Weather, rainfall forecasts and modelled river "
        "discharge monitoring for selected Maharashtra locations."
    )

    st.info(
        "This is an experimental monitoring tool. "
        "River discharge is modelled data, not a live river-gauge "
        "measurement or an official flood warning."
    )

    # LOCATION SELECTION

    district = st.selectbox(
        "Select Monitoring Location",
        list(LOCATIONS.keys())
    )

    latitude, longitude = LOCATIONS[district]

    st.caption(
        f"Location: {district}, Maharashtra | "
        f"Coordinates: {latitude}, {longitude}"
    )

    if st.button("🔄 Refresh Monitoring Data"):
        get_weather.clear()
        get_river_data.clear()

    # -----------------------------------
    # WEATHER SECTION
    # -----------------------------------

    st.divider()
    st.header("☁️ Current Weather & Rainfall")

    try:
        weather = get_weather(latitude, longitude)
        current = weather["current"]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Temperature",
            f'{current["temperature_2m"]} °C'
        )

        col2.metric(
            "Humidity",
            f'{current["relative_humidity_2m"]} %'
        )

        col3.metric(
            "Precipitation",
            f'{current["precipitation"]} mm'
        )

        col4.metric(
            "Wind Speed",
            f'{current["wind_speed_10m"]} km/h'
        )

        st.caption(
            f'Weather data timestamp: '
            f'{current.get("time", "Not available")}'
        )

        # HOURLY RAINFALL

        st.subheader("🌧️ Hourly Rainfall Forecast")

        hourly = weather.get("hourly", {})

        rainfall_df = pd.DataFrame({
            "Time": hourly.get("time", []),
            "Rainfall (mm)": hourly.get("precipitation", [])
        })

        if not rainfall_df.empty:

            rainfall_df["Time"] = pd.to_datetime(
                rainfall_df["Time"]
            )

            st.line_chart(
                rainfall_df.set_index("Time")["Rainfall (mm)"]
            )

            # -----------------------------------
            # 24-HOUR RAINFALL OUTLOOK
            # -----------------------------------

            st.divider()
            st.header("⏳ 24-Hour Flood Risk Outlook")

            current_time = pd.to_datetime(current["time"])

            next_24_hours = (
                current_time + pd.Timedelta(hours=24)
            )

            forecast_24h = rainfall_df[
                (rainfall_df["Time"] >= current_time) &
                (rainfall_df["Time"] < next_24_hours)
            ]

            forecast_24h = forecast_24h.dropna(
                subset=["Rainfall (mm)"]
            )

            if not forecast_24h.empty:

                total_rainfall = forecast_24h[
                    "Rainfall (mm)"
                ].sum()

                st.metric(
                    "Forecast Rainfall — Next 24 Hours",
                    f"{total_rainfall:.1f} mm"
                )

                if total_rainfall >= 20:

                    st.warning(
                        "⚠️ Elevated Rainfall Screening: "
                        f"{total_rainfall:.1f} mm forecast "
                        "over the next 24 hours."
                    )

                else:

                    st.success(
                        "Rainfall is below the experimental "
                        "screening threshold. Forecast rainfall: "
                        f"{total_rainfall:.1f} mm."
                    )

                st.caption(
                    "Experimental screening threshold: 20 mm "
                    "of rainfall in 24 hours. This is not a "
                    "validated local flood-danger threshold."
                )

            else:
                st.warning(
                    "No hourly rainfall values available "
                    "for the next 24 hours."
                )

        else:
            st.warning("Hourly rainfall data is unavailable.")

    except requests.RequestException as error:
        st.error(f"Unable to fetch weather data: {error}")

    except (KeyError, TypeError, ValueError) as error:
        st.error(f"Unexpected weather data format: {error}")

    # -----------------------------------
    # RIVER DISCHARGE SECTION
    # -----------------------------------

    st.divider()
    st.header("🌊 River Discharge Monitoring")

    st.write(
        "The following section displays modelled river "
        "discharge estimates for the selected coordinates."
    )

    try:
        river = get_river_data(latitude, longitude)

        daily = river.get("daily", {})

        dates = daily.get("time", [])
        discharge = daily.get("river_discharge", [])

        river_df = pd.DataFrame({
            "Date": dates,
            "River Discharge (m³/s)": discharge
        })

        if not river_df.empty:

            river_df["Date"] = pd.to_datetime(
                river_df["Date"]
            )

            river_df = river_df.dropna(
                subset=["River Discharge (m³/s)"]
            )

            if not river_df.empty:

                st.subheader("River Discharge Trend")

                st.line_chart(
                    river_df.set_index("Date")[
                        "River Discharge (m³/s)"
                    ]
                )

                st.subheader("Discharge Records")

                st.dataframe(
                    river_df,
                    use_container_width=True
                )

                st.metric(
                    "Latest Available Discharge",
                    f'{river_df["River Discharge (m³/s)"].iloc[-1]:.2f} m³/s'
                )

                st.warning(
                    "These are modelled discharge estimates. "
                    "They are not measured river levels and "
                    "cannot independently establish flood danger."
                )

            else:
                st.warning(
                    "No valid river discharge values were returned."
                )

        else:
            st.warning(
                "River discharge data is unavailable for this location."
            )

    except requests.RequestException as error:
        st.error(f"Unable to fetch river data: {error}")

    except (KeyError, TypeError, ValueError) as error:
        st.error(f"Unexpected river data format: {error}")

    # -----------------------------------
    # DATA SOURCES
    # -----------------------------------

    st.divider()
    st.subheader("ℹ️ Data Sources")

    st.markdown(
        """
        - Weather and rainfall: Open-Meteo Weather API
        - River discharge: Open-Meteo Flood API (GloFAS)
        - Weather data cache: 15 minutes
        - River data cache: 1 hour
        """
    )

    st.caption(
        "Experimental monitoring interface. "
        "It does not provide a validated 24-hour flood prediction "
        "or an official flood alert. Always follow IMD and "
        "local authority instructions."
    )

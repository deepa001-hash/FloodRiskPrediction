
import streamlit as st
import pandas as pd

from live_monitoring import (
    LOCATIONS,
    get_weather,
    get_river_data,
)

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Interactive Flood Map",
    page_icon="🗺️",
    layout="wide",
)

st.title("🗺️ Interactive Maharashtra Flood Map")

st.write(
    "Explore monitoring locations across Maharashtra "
    "and view weather, rainfall and modelled river discharge."
)

st.info(
    "Map markers show configured monitoring coordinates, "
    "not confirmed flood locations. River discharge is modelled "
    "data, not an actual river-gauge measurement."
)

# ==================================================
# 2. LOCATION DATA
# ==================================================

map_data = pd.DataFrame([
    {
        "Location": name,
        "Latitude": coordinates[0],
        "Longitude": coordinates[1],
    }
    for name, coordinates in LOCATIONS.items()
])

# ==================================================
# 3. LOCATION SELECTION
# ==================================================

st.header("📍 Select Monitoring Location")

district = st.selectbox(
    "Choose a Maharashtra location",
    list(LOCATIONS.keys()),
)

latitude, longitude = LOCATIONS[district]

st.caption(
    f"Selected location: {district}, Maharashtra | "
    f"Latitude: {latitude} | Longitude: {longitude}"
)

# ==================================================
# 4. INTERACTIVE MAP
# ==================================================

st.divider()
st.header("🌍 Maharashtra Monitoring Locations")

st.write(
    "Use the map to explore the configured monitoring "
    "locations. Select a location using the dropdown above."
)

st.map(
    map_data,
    latitude="Latitude",
    longitude="Longitude",
    color="#FF4B4B",
    size=100,
    zoom=5,
)

st.caption(
    "Map markers represent approximate city monitoring "
    "coordinates, not river gauges or flood boundaries."
)

# ==================================================
# 5. FETCH SELECTED LOCATION WEATHER
# ==================================================

st.divider()
st.header(f"🌧️ Weather Information — {district}")

if st.button("Refresh Selected Location Data"):
    get_weather.clear()
    get_river_data.clear()

try:

    weather = get_weather(latitude, longitude)

    current = weather.get("current", {})

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Temperature",
        f'{current.get("temperature_2m", "N/A")} °C',
    )

    col2.metric(
        "Humidity",
        f'{current.get("relative_humidity_2m", "N/A")}%',
    )

    col3.metric(
        "Rainfall",
        f'{current.get("rain", "N/A")} mm',
    )

    col4.metric(
        "Wind Speed",
        f'{current.get("wind_speed_10m", "N/A")} km/h',
    )

    st.caption(
        f'Data timestamp: {current.get("time", "Not available")}'
    )

    hourly = weather.get("hourly", {})

    rainfall_df = pd.DataFrame({
        "Time": hourly.get("time", []),
        "Rainfall (mm)": hourly.get("precipitation", []),
    })

    if not rainfall_df.empty:

        rainfall_df["Time"] = pd.to_datetime(
            rainfall_df["Time"]
        )

        st.subheader("Hourly Rainfall Trend")

        st.line_chart(
            rainfall_df.set_index("Time")["Rainfall (mm)"]
        )

except Exception as error:

    st.error(
        f"Could not retrieve weather information: {error}"
    )

# ==================================================
# 6. RIVER DISCHARGE INFORMATION
# ==================================================

st.divider()
st.header(f"🌊 River Discharge — {district}")

try:

    river = get_river_data(latitude, longitude)

    daily = river.get("daily", {})

    river_df = pd.DataFrame({
        "Date": daily.get("time", []),
        "River Discharge (m³/s)": daily.get(
            "river_discharge", []
        ),
    })

    if not river_df.empty:

        river_df["Date"] = pd.to_datetime(
            river_df["Date"]
        )

        river_df["River Discharge (m³/s)"] = pd.to_numeric(
            river_df["River Discharge (m³/s)"],
            errors="coerce",
        )

        river_df = river_df.dropna(
            subset=["River Discharge (m³/s)"]
        )

        if not river_df.empty:

            st.subheader("Modelled River Discharge Trend")

            st.line_chart(
                river_df.set_index("Date")[
                    "River Discharge (m³/s)"
                ]
            )

            st.dataframe(
                river_df,
                use_container_width=True,
            )

        else:
            st.warning("No valid discharge values are available.")

    else:
        st.warning("River discharge information is unavailable.")

except Exception as error:

    st.error(
        f"Could not retrieve river discharge information: {error}"
    )

# ==================================================
# 7. MONITORING LOCATIONS TABLE
# ==================================================

st.divider()
st.header("📋 Available Monitoring Locations")

st.dataframe(
    map_data.rename(
        columns={
            "Location": "District / City",
            "Latitude": "Latitude",
            "Longitude": "Longitude",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

# ==================================================
# 8. FOOTER
# ==================================================

st.divider()

st.caption(
    "Interactive Flood Map | Experimental research prototype | "
    "Not an official flood map or warning service."
)

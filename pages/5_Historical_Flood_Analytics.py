
from pathlib import Path

import pandas as pd
import streamlit as st

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Historical Flood Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Historical Flood Analytics")

st.write(
    "Explore historical flood events, severity distribution, "
    "state-wise records and flood measurements."
)

# ==================================================
# 2. LOAD DATASET
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "flood_ml_dataset.csv"


@st.cache_data
def load_dataset(path):
    return pd.read_csv(path)


if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Place flood_ml_dataset.csv in the main project folder, "
        "alongside dashboard.py."
    )
    st.stop()

try:
    df = load_dataset(str(DATA_PATH))
except Exception as error:
    st.error(f"Could not load dataset: {error}")
    st.stop()

# ==================================================
# 3. CLEAN DATA
# ==================================================

required_columns = [
    "Start Date",
    "Flood Type",
    "State",
    "Peak Flood Level (m)",
    "Peak Discharge Q (cumec)",
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()

df["Start Date"] = pd.to_datetime(
    df["Start Date"],
    errors="coerce",
)

df["Year"] = df["Start Date"].dt.year

df["Peak Flood Level (m)"] = pd.to_numeric(
    df["Peak Flood Level (m)"],
    errors="coerce",
)

df["Peak Discharge Q (cumec)"] = pd.to_numeric(
    df["Peak Discharge Q (cumec)"],
    errors="coerce",
)

df["State"] = (
    df["State"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

df["Flood Type"] = (
    df["Flood Type"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)

# ==================================================
# 4. DATASET OVERVIEW
# ==================================================

st.divider()
st.header("📌 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Records", f"{len(df):,}")
col2.metric(
    "Recorded Flood Events",
    f"{df['EventID'].nunique():,}"
    if "EventID" in df.columns
    else f"{len(df):,}",
)
col3.metric(
    "States Represented",
    f"{df.loc[df['State'] != 'Unknown', 'State'].nunique():,}",
)
col4.metric(
    "Historical Years",
    f"{df['Year'].nunique():,}",
)

if df["Year"].notna().any():
    st.caption(
        f"Available date range: "
        f"{int(df['Year'].min())}–{int(df['Year'].max())}"
    )

# ==================================================
# 5. FILTERS
# ==================================================

st.divider()
st.header("🔎 Filter Historical Records")

valid_years = sorted(
    df["Year"].dropna().astype(int).unique().tolist()
)

if valid_years:

    year_range = st.slider(
        "Select year range",
        min_value=min(valid_years),
        max_value=max(valid_years),
        value=(min(valid_years), max(valid_years)),
    )

    filtered_df = df[
        df["Year"].between(
            year_range[0],
            year_range[1],
        )
    ].copy()

else:
    filtered_df = df.copy()

states = sorted(
    filtered_df.loc[
        filtered_df["State"] != "Unknown",
        "State",
    ].unique().tolist()
)

selected_states = st.multiselect(
    "Select states",
    options=states,
    default=states,
)

if selected_states:
    filtered_df = filtered_df[
        filtered_df["State"].isin(selected_states)
    ]
else:
    filtered_df = filtered_df.iloc[0:0]

flood_types = sorted(
    filtered_df["Flood Type"].unique().tolist()
)

selected_types = st.multiselect(
    "Select flood categories",
    options=flood_types,
    default=flood_types,
)

filtered_df = filtered_df[
    filtered_df["Flood Type"].isin(selected_types)
]

st.write(f"**Records after filtering:** {len(filtered_df):,}")

# ==================================================
# 6. FLOOD SEVERITY DISTRIBUTION
# ==================================================

st.divider()
st.header("🌊 Flood Severity Distribution")

if not filtered_df.empty:

    severity_counts = (
        filtered_df["Flood Type"]
        .value_counts()
        .rename_axis("Flood Type")
        .reset_index(name="Number of Events")
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Flood Category")

        st.bar_chart(
            severity_counts.set_index("Flood Type")
        )

    with col2:
        st.subheader("Category Summary")

        st.dataframe(
            severity_counts,
            use_container_width=True,
            hide_index=True,
        )

else:
    st.info("No records match the selected filters.")

# ==================================================
# 7. YEAR-WISE FLOOD EVENTS
# ==================================================

st.divider()
st.header("📅 Year-wise Flood Events")

yearly = (
    filtered_df.dropna(subset=["Year"])
    .groupby(["Year", "Flood Type"])
    .size()
    .unstack(fill_value=0)
)

if not yearly.empty:

    yearly.index = yearly.index.astype(int)

    st.line_chart(yearly)

    yearly_table = yearly.reset_index()

    st.dataframe(
        yearly_table,
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info("Year-wise data is unavailable.")

# ==================================================
# 8. STATE-WISE FLOOD ANALYSIS
# ==================================================

st.divider()
st.header("📍 State-wise Flood Analysis")

state_summary = (
    filtered_df.groupby("State")
    .size()
    .reset_index(name="Number of Events")
    .sort_values("Number of Events", ascending=False)
)

if not state_summary.empty:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Flood Events by State")

        st.bar_chart(
            state_summary.set_index("State")
        )

    with col2:
        st.subheader("State Records")

        st.dataframe(
            state_summary,
            use_container_width=True,
            hide_index=True,
        )

else:
    st.info("State-wise records are unavailable.")

# ==================================================
# 9. FLOOD LEVEL ANALYSIS
# ==================================================

st.divider()
st.header("📈 Peak Flood Level Analysis")

level_data = filtered_df.dropna(
    subset=["Peak Flood Level (m)", "Year"]
)

if not level_data.empty:

    level_trend = (
        level_data.groupby("Year")["Peak Flood Level (m)"]
        .mean()
        .rename("Average Peak Flood Level (m)")
    )

    st.line_chart(level_trend)

    col1, col2 = st.columns(2)

    col1.metric(
        "Average Peak Level",
        f"{level_data['Peak Flood Level (m)'].mean():.2f} m",
    )

    col2.metric(
        "Maximum Recorded Peak Level",
        f"{level_data['Peak Flood Level (m)'].max():.2f} m",
    )

else:
    st.info("Peak flood level measurements are unavailable.")

# ==================================================
# 10. DISCHARGE ANALYSIS
# ==================================================

st.divider()
st.header("💧 Peak River Discharge Analysis")

discharge_data = filtered_df.dropna(
    subset=["Peak Discharge Q (cumec)", "Year"]
)

if not discharge_data.empty:

    discharge_trend = (
        discharge_data.groupby("Year")["Peak Discharge Q (cumec)"]
        .mean()
        .rename("Average Peak Discharge (cumec)")
    )

    st.line_chart(discharge_trend)

    col1, col2 = st.columns(2)

    col1.metric(
        "Average Peak Discharge",
        f"{discharge_data['Peak Discharge Q (cumec)'].mean():,.2f}",
    )

    col2.metric(
        "Maximum Peak Discharge",
        f"{discharge_data['Peak Discharge Q (cumec)'].max():,.2f}",
    )

else:
    st.info("Peak discharge measurements are unavailable.")

# ==================================================
# 11. HISTORICAL DATA TABLE
# ==================================================

st.divider()
st.header("📋 Historical Flood Records")

display_columns = [
    col for col in [
        "EventID",
        "Start Date",
        "State",
        "Station",
        "River Name/ Tributory/ SubTributory",
        "Flood Type",
        "Peak Flood Level (m)",
        "Peak Discharge Q (cumec)",
        "Event Duration (days)",
    ]
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    hide_index=True,
)

# ==================================================
# 12. DOWNLOAD REPORT
# ==================================================

st.divider()
st.header("⬇️ Download Historical Analysis")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Flood Records",
    data=csv_data,
    file_name="historical_flood_analysis.csv",
    mime="text/csv",
)

# ==================================================
# 13. LIMITATIONS
# ==================================================

st.divider()

st.info(
    "Historical analysis describes recorded events in the supplied "
    "dataset. It does not establish future flood probability or "
    "causation. Results depend on dataset coverage and quality."
)

st.caption(
    "Historical Flood Analytics | Research prototype"
)

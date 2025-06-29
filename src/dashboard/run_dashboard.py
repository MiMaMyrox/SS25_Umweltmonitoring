import requests
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from backend._format_df import format_df
from backend import hourly_df, daily_df, monthly_df, yearly_df


if "initialized" not in st.session_state:
    requests.get("http://collector:8000/update-db")
    st.session_state.initialized = True

st.title("🌍 Umweltmonitoring Dashboard")

@st.cache_data
def load_data() -> pd.DataFrame:
    df = requests.get("http://collector:8000/get-db").json()["data"]
    df = format_df(pd.DataFrame(df))
    df['createdat'] = pd.to_datetime(df['createdat'], format="ISO8601", utc=True)
    df = df.replace([np.nan, np.inf, -np.inf], None)
    response = requests.get("http://model:9000/predict")
    forecast = pd.DataFrame(response.json())[["ds","yhat","yhat_lower","yhat_upper"]]
    forecast["ds"] = pd.to_datetime(forecast["ds"], format="ISO8601", utc=True)

    df = pd.merge_asof(
        df,
        forecast,
        left_on="createdat",
        right_on="ds",
        direction="backward"
    ).drop(columns=["ds"])

    df = format_df(df)
    return df

df = load_data()

aggregation = st.selectbox("Aggregation", ["Stündlich","Täglich", "Monatlich"])

sensor = st.selectbox("Messgröße wählen", ["temperatur","rel_luftfeuchte","luftdruck","pm10","pm25"])


if aggregation == "Stündlich":
    agg_df = hourly_df(df)

    # Convert to date only for selection
    min_date = agg_df["zeit"].dt.date.min()
    max_date = agg_df["zeit"].dt.date.max()

    # Let user select a single day
    selected_date = st.date_input(
        "Tag auswählen",
        value=min_date,
        min_value=min_date,
        max_value=max_date
    )

    # Define datetime range for selected day
    start_dt = pd.to_datetime(selected_date)
    end_dt = start_dt + pd.Timedelta(days=1)

    # Filter for selected day
    agg_df = agg_df[(agg_df["zeit"] >= start_dt) & (agg_df["zeit"] < end_dt)]


if aggregation == "Täglich":
    agg_df = daily_df(df)
    min_date, max_date = agg_df["zeit"].min(), agg_df["zeit"].max()
    start_date, end_date = st.date_input(
        "Zeitraum auswählen",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )
    agg_df = agg_df[(agg_df["zeit"].dt.date >= start_date) & (agg_df["zeit"].dt.date <= end_date)]

if aggregation == "Monatlich":
    agg_df = monthly_df(df)
    month_options = agg_df["zeit"].dt.to_period("M").astype(str).tolist()

    # Allow selecting start and end month
    start_month = st.selectbox("Startmonat", month_options, index=0)
    end_month = st.selectbox("Endmonat", month_options, index=len(month_options) - 1)

    # Convert back to timestamps
    start_date = pd.to_datetime(start_month)
    end_date = pd.to_datetime(end_month) + pd.offsets.MonthEnd(0)

    # Filter data
    agg_df = agg_df[(agg_df["zeit"] >= start_date) & (agg_df["zeit"] <= end_date)]


if sensor == "temperatur":
    plot_df = agg_df.set_index("zeit")[[sensor, "yhat", "yhat_lower", "yhat_upper"]]
else:
    plot_df = agg_df.set_index("zeit")[[sensor]]

st.line_chart(plot_df)

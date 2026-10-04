"""Airline Passenger Satisfaction — interactive Streamlit dashboard.

Run locally with:  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).parent
RAW_DATA_PATH = BASE_DIR / "Data.csv"
CLEAN_DATA_PATH = BASE_DIR / "Data_Cleaned.csv"

SATISFIED_COLOR = "#2a78d6"
DISSATISFIED_COLOR = "#eb6834"
SATISFACTION_COLORS = {"Satisfied": SATISFIED_COLOR, "Neutral or Dissatisfied": DISSATISFIED_COLOR}
CATEGORY_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]

CATEGORY_ORDERS = {
    "gender": ["Female", "Male"],
    "customer_type": ["Loyal Customer", "Disloyal Customer"],
    "type_of_travel": ["Business Travel", "Personal Travel"],
    "class": ["Economy", "Economy Plus", "Business"],
    "satisfaction": ["Satisfied", "Neutral or Dissatisfied"],
    "age_group": ["Child (<18)", "Young Adult (18-29)", "Adult (30-44)", "Middle-Aged (45-59)", "Senior (60+)"],
    "distance_group": ["Short-haul (<800 mi)", "Medium-haul (800-2000 mi)", "Long-haul (>2000 mi)"],
    "delay_group": ["On time", "1-15 min", "16-60 min", "> 60 min"],
}

st.set_page_config(page_title="Airline Passenger Satisfaction", page_icon="✈️", layout="wide")


# ---------------------------------------------------------------- data loading
@st.cache_data
def load_data():
    """Load the raw and cleaned datasets produced by the notebook."""
    raw = pd.read_csv(RAW_DATA_PATH)
    clean = pd.read_csv(CLEAN_DATA_PATH)
    for column, order in CATEGORY_ORDERS.items():
        clean[column] = pd.Categorical(clean[column], categories=order)
    return raw, clean


raw_df, clean_df = load_data()
SERVICE_COLUMNS = list(clean_df.loc[:, "inflight_wifi_service":"cleanliness"].columns)


def pretty_name(column):
    """snake_case -> Title Case label."""
    return column.replace("_", " ").title()


def satisfaction_rate_by(df, column):
    """Satisfaction rate (%) and number of passengers for every group of a column."""
    table = (df.groupby(column, observed=True)["is_satisfied"]
               .agg(satisfaction_rate="mean", passengers="count").reset_index())
    table["satisfaction_rate"] = (table["satisfaction_rate"] * 100).round(1)
    return table


def stacked_satisfaction_bar(df, column):
    """100 % stacked bar of satisfied vs dissatisfied passengers per group."""
    shares = (pd.crosstab(df[column], df["satisfaction"], normalize="index") * 100).round(1)
    long = shares.reset_index().melt(id_vars=column, var_name="satisfaction", value_name="percent")
    fig = px.bar(long, x=column, y="percent", color="satisfaction", text="percent",
                 color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                 labels={column: pretty_name(column), "percent": "% of passengers", "satisfaction": ""})
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="inside", marker_line_color="white",
                      marker_line_width=2)
    fig.update_layout(title=f"Satisfaction by {pretty_name(column)}", barmode="stack",
                      legend=dict(orientation="h", y=1.12), margin=dict(t=80))
    return fig


# ---------------------------------------------------------------- sidebar filters
st.sidebar.title("✈️ Filters")
st.sidebar.caption("All charts update with these filters.")


def multiselect_filter(label, column):
    """Sidebar multiselect pre-filled with every category of the column."""
    options = CATEGORY_ORDERS[column]
    return st.sidebar.multiselect(label, options, default=options)


selected_class = multiselect_filter("Class", "class")
selected_travel = multiselect_filter("Type of travel", "type_of_travel")
selected_customer = multiselect_filter("Customer type", "customer_type")
selected_gender = multiselect_filter("Gender", "gender")
age_range = st.sidebar.slider("Age", int(clean_df["age"].min()), int(clean_df["age"].max()),
                              (int(clean_df["age"].min()), int(clean_df["age"].max())))

filtered_df = clean_df[
    clean_df["class"].isin(selected_class)
    & clean_df["type_of_travel"].isin(selected_travel)
    & clean_df["customer_type"].isin(selected_customer)
    & clean_df["gender"].isin(selected_gender)
    & clean_df["age"].between(*age_range)
]
st.sidebar.markdown(f"**{len(filtered_df):,}** of {len(clean_df):,} passengers selected")

# ---------------------------------------------------------------- header
st.title("✈️ Airline Passenger Satisfaction Dashboard")
st.markdown("What makes airline passengers satisfied — and what makes them unhappy? "
            "An analysis of **25,976** passenger survey responses.")

if filtered_df.empty:
    st.warning("No passengers match the selected filters. Please widen your selection.")
    st.stop()

# KPI row
kpi_columns = st.columns(5)
kpi_columns[0].metric("Passengers", f"{len(filtered_df):,}")
kpi_columns[1].metric("Satisfied", f"{filtered_df['is_satisfied'].mean():.1%}",
                      f"{(filtered_df['is_satisfied'].mean() - clean_df['is_satisfied'].mean()) * 100:+.1f} pts vs all")
kpi_columns[2].metric("Avg. service rating", f"{filtered_df['average_service_rating'].mean():.2f} / 5")
kpi_columns[3].metric("On-time arrivals", f"{(filtered_df['arrival_delay'] == 0).mean():.1%}")
kpi_columns[4].metric("Median flight distance", f"{filtered_df['flight_distance'].median():,.0f} mi")

tab_overview, tab_cleaning, tab_segments, tab_services, tab_delays, tab_insights, tab_data = st.tabs(
    ["📋 Overview", "🧹 Data Cleaning", "👥 Passenger Segments", "⭐ Services", "⏱️ Delays & Distance",
     "💡 Insights", "🔎 Data Explorer"])

# ---------------------------------------------------------------- overview
with tab_overview:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("The domain")
        st.markdown(
            "Airlines compete on customer experience. This survey describes **who** each passenger is, "
            "**how** they travelled and **how they rated 14 services** (1–5), together with their overall "
            "satisfaction.")
        st.subheader("Research questions")
        st.markdown(
            "1. What share of passengers are satisfied?\n"
            "2. Which passenger segments are more / less satisfied?\n"
            "3. Which services matter most?\n"
            "4. Do delays reduce satisfaction?\n"
            "5. Does flight distance matter, and does it depend on class?\n"
            "6. Which travel type × class combination is happiest / unhappiest?")
    with right:
        counts = filtered_df["satisfaction"].value_counts().reindex(CATEGORY_ORDERS["satisfaction"])
        fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.55, sort=False,
                               marker=dict(colors=[SATISFIED_COLOR, DISSATISFIED_COLOR],
                                           line=dict(color="white", width=2))))
        fig.update_layout(title="Overall satisfaction", legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig, width="stretch")

    st.subheader("Columns in the dataset")
    column_descriptions = pd.DataFrame({
        "Column": ["id", "Gender", "Customer Type", "Age", "Type of Travel", "Class", "Flight Distance",
                   "14 service ratings", "Departure / Arrival Delay in Minutes", "satisfaction"],
        "Meaning": ["Unique passenger id", "Female / Male", "Loyal or disloyal customer", "Age in years",
                    "Business or personal travel", "Business, Eco, Eco Plus", "Flight distance in miles",
                    "Wifi, time convenience, online booking, gate location, food & drink, online boarding, "
                    "seat comfort, entertainment, on-board service, leg room, baggage, check-in, inflight "
                    "service, cleanliness — rated 1–5, 0 = not applicable",
                    "Delay in minutes", "Target: satisfied / neutral or dissatisfied"],
    })
    st.dataframe(column_descriptions, hide_index=True, width="stretch")

# ---------------------------------------------------------------- data cleaning
with tab_cleaning:
    st.subheader("Problems found in the raw data")
    raw_service_columns = list(raw_df.loc[:, "Inflight wifi service":"Cleanliness"].columns)
    zero_ratings = int((raw_df[raw_service_columns] == 0).sum().sum())
    issue_columns = st.columns(4)
    issue_columns[0].metric("Missing arrival delays", int(raw_df["Arrival Delay in Minutes"].isna().sum()))
    issue_columns[1].metric("'0 = N/A' ratings", f"{zero_ratings:,}")
    issue_columns[2].metric("Useless index columns", 1)
    issue_columns[3].metric("Inconsistent label groups", 4)

    cleaning_log = pd.DataFrame({
        "Problem": ["83 missing arrival delays", "Arrival delay stored as float",
                    "Rating 0 = 'Not Applicable'", "Inconsistent labels (e.g. 'disloyal Customer', 'Eco')",
                    "Extreme delays / distances", "Useless 'Unnamed: 0' column",
                    "Column names with spaces and slashes", "No segment columns"],
        "Action": ["Filled with the passenger's departure delay (correlation 0.96)", "Converted to integer",
                   "Replaced by NaN so they don't drag averages down", "Standardised capitalisation, Eco → Economy",
                   "Verified as genuine and kept; grouped into bins", "Dropped",
                   "Converted to snake_case", "Added age / distance / delay groups and average rating"],
    })
    st.dataframe(cleaning_log, hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        zero_by_service = (raw_df[raw_service_columns] == 0).sum().sort_values()
        zero_by_service = zero_by_service[zero_by_service > 0]
        fig = px.bar(x=zero_by_service.values, y=zero_by_service.index, orientation="h",
                     labels={"x": "Number of 0 ratings", "y": ""}, text=zero_by_service.values,
                     color_discrete_sequence=[DISSATISFIED_COLOR])
        fig.update_layout(title="'0 = Not Applicable' ratings per service (raw data)")
        st.plotly_chart(fig, width="stretch")
    with right:
        sample = raw_df.dropna().sample(3000, random_state=1)
        fig = px.scatter(sample, x="Departure Delay in Minutes", y="Arrival Delay in Minutes", opacity=0.4,
                         color_discrete_sequence=[SATISFIED_COLOR])
        fig.update_layout(title="Departure vs arrival delay — why we fill one with the other")
        st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- passenger segments
with tab_segments:
    segment_column = st.selectbox("Compare satisfaction by", ["class", "type_of_travel", "customer_type",
                                                              "gender", "age_group"], format_func=pretty_name)
    left, right = st.columns([3, 2])
    with left:
        st.plotly_chart(stacked_satisfaction_bar(filtered_df, segment_column), width="stretch")
    with right:
        st.markdown("**Satisfaction rate per group**")
        st.dataframe(satisfaction_rate_by(filtered_df, segment_column), hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        heat = filtered_df.pivot_table(index="type_of_travel", columns="class", values="is_satisfied",
                                       aggfunc="mean", observed=True) * 100
        fig = px.imshow(heat.round(1), text_auto=True, color_continuous_scale="Blues", zmin=0, zmax=100,
                        labels=dict(color="Satisfied %", x="", y=""), aspect="auto")
        fig.update_layout(title="Satisfaction rate (%) — travel type × class")
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.histogram(filtered_df, x="age", color="satisfaction", barmode="overlay", nbins=40,
                           opacity=0.65, color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                           labels={"age": "Age", "satisfaction": ""})
        fig.update_layout(title="Age distribution by satisfaction", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- services
with tab_services:
    service_means = filtered_df.groupby("satisfaction", observed=True)[SERVICE_COLUMNS].mean().T
    service_means = service_means.reindex(columns=CATEGORY_ORDERS["satisfaction"])
    service_means["gap"] = service_means["Satisfied"] - service_means["Neutral or Dissatisfied"]
    service_means = service_means.sort_values("gap")
    service_labels = [pretty_name(c) for c in service_means.index]

    left, right = st.columns(2)
    with left:
        overall = filtered_df[SERVICE_COLUMNS].mean().sort_values()
        fig = px.bar(x=overall.values.round(2), y=[pretty_name(c) for c in overall.index], orientation="h",
                     text=overall.values.round(2), labels={"x": "Average rating (1-5)", "y": ""},
                     color_discrete_sequence=[SATISFIED_COLOR])
        fig.update_layout(title="Average rating per service", xaxis_range=[0, 5], height=520)
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = go.Figure()
        for group, color in SATISFACTION_COLORS.items():
            fig.add_trace(go.Scatter(x=service_means[group], y=service_labels, mode="markers", name=group,
                                     marker=dict(color=color, size=12, line=dict(color="white", width=2))))
        for label, row in zip(service_labels, service_means.itertuples()):
            fig.add_shape(type="line", x0=row[2], x1=row[1], y0=label, y1=label,
                          line=dict(color="#c3c2b7", width=2), layer="below")
        fig.update_layout(title="Rating gap: satisfied vs dissatisfied", xaxis_title="Average rating (1-5)",
                          height=520, legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig, width="stretch")

    chosen_service = st.selectbox("How does satisfaction change with the rating of…", service_means.index[::-1],
                                  format_func=pretty_name)
    rate = satisfaction_rate_by(filtered_df, chosen_service)
    fig = px.line(rate, x=chosen_service, y="satisfaction_rate", markers=True,
                  labels={chosen_service: "Rating given", "satisfaction_rate": "Satisfied (%)"},
                  color_discrete_sequence=[SATISFIED_COLOR], hover_data=["passengers"])
    fig.update_traces(marker_size=10, line_width=3)
    fig.update_layout(title=f"Satisfaction rate by {pretty_name(chosen_service)} rating", yaxis_range=[0, 100], xaxis_dtick=1)
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- delays and distance
with tab_delays:
    left, right = st.columns(2)
    with left:
        delay_rate = satisfaction_rate_by(filtered_df, "delay_group")
        fig = px.bar(delay_rate, x="delay_group", y="satisfaction_rate", text="satisfaction_rate",
                     hover_data=["passengers"], color_discrete_sequence=[SATISFIED_COLOR],
                     labels={"delay_group": "Arrival delay", "satisfaction_rate": "Satisfied (%)"})
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(title="Satisfaction rate by arrival delay", yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.box(filtered_df, x="class", y="flight_distance", color="satisfaction",
                     color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                     labels={"class": "", "flight_distance": "Flight distance (miles)", "satisfaction": ""})
        fig.update_layout(title="Flight distance by class and satisfaction", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, width="stretch")

    heat = filtered_df.pivot_table(index="distance_group", columns="class", values="is_satisfied",
                                   aggfunc="mean", observed=True) * 100
    fig = px.imshow(heat.round(1), text_auto=True, color_continuous_scale="Blues", zmin=0, zmax=100,
                    labels=dict(color="Satisfied %", x="", y=""), aspect="auto")
    fig.update_layout(title="Satisfaction rate (%) by distance and class — distance matters mostly through class")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- insights
with tab_insights:
    st.subheader("Key insights")
    insight_columns = st.columns(3)
    insight_columns[0].info("**Only 43.9 %** of passengers are satisfied — the majority are neutral or dissatisfied.")
    insight_columns[1].info("**Business class: 69.5 %** satisfied vs **Economy: 19.4 %**.")
    insight_columns[2].info("**Personal travellers: ~10 %** satisfied, in every class.")
    insight_columns = st.columns(3)
    insight_columns[0].info("**Online boarding** is the #1 service driver (rating gap +1.44).")
    insight_columns[1].info("**Wifi** is the lowest-rated service, yet 99 % of those rating it 5 are satisfied.")
    insight_columns[2].info("Delays lower satisfaction from **47.9 %** (on time) to **35.2 %** (> 1 hour).")

    st.subheader("Recommendations")
    st.markdown(
        "1. **Fix the digital journey** — wifi, online boarding and online booking.\n"
        "2. **Upgrade the Economy experience** — seat comfort, entertainment, leg room.\n"
        "3. **Create an offer for leisure travellers** — they are the least satisfied group.\n"
        "4. **Win back disloyal customers** with targeted loyalty offers.\n"
        "5. **Reduce delays** and communicate proactively when they happen.")

# ---------------------------------------------------------------- data explorer
with tab_data:
    st.subheader("Cleaned data (filtered)")
    st.dataframe(filtered_df, width="stretch", height=450)
    st.download_button("⬇️ Download filtered data as CSV", filtered_df.to_csv(index=False).encode("utf-8"),
                       file_name="airline_satisfaction_filtered.csv", mime="text/csv")
    st.subheader("Summary statistics")
    st.dataframe(filtered_df.describe().T.round(2), width="stretch")

st.caption("Mid Project · Airline Passenger Satisfaction · Built with Python, Pandas, Plotly & Streamlit")

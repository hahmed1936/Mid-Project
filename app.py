"""Airline Passenger Satisfaction — interactive Streamlit dashboard.

Run locally with:  streamlit run app.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

BASE_DIR = Path(__file__).parent
RAW_DATA_PATH = BASE_DIR / "Data.csv"
CLEAN_DATA_PATH = BASE_DIR / "Data_Cleaned.csv"

# ---------------------------------------------------------------- colours
NAVY = "#0b1f3a"
SKY = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
PINK = "#e87ba4"
VIOLET = "#4a3aa7"
MUTED = "#5b636e"
SATISFACTION_COLORS = {"Satisfied": SKY, "Neutral or Dissatisfied": ORANGE}
CLASS_COLORS = {"Economy": ORANGE, "Economy Plus": YELLOW, "Business": SKY}
TRAVEL_COLORS = {"Business Travel": SKY, "Personal Travel": PINK}
CUSTOMER_COLORS = {"Loyal Customer": AQUA, "Disloyal Customer": VIOLET}
GENDER_COLORS = {"Female": PINK, "Male": SKY}
SEQUENTIAL_SCALE = ["#fde7dc", "#f6b89c", "#c9d8ee", "#6fa3e3", SKY, "#123f7a"]

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

# One consistent look for every Plotly chart
pio.templates["airline"] = go.layout.Template(layout=go.Layout(
    font=dict(family="Segoe UI, Arial, sans-serif", size=13, color="#1b1f24"),
    title=dict(font=dict(size=17, color=NAVY), x=0.01, xanchor="left"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=[SKY, ORANGE, AQUA, YELLOW, PINK, VIOLET],
    xaxis=dict(gridcolor="#e6ebf1", zeroline=False, linecolor="#d5dbe3"),
    yaxis=dict(gridcolor="#e6ebf1", zeroline=False, linecolor="#d5dbe3"),
    legend=dict(orientation="h", y=1.1, x=0, title_text=""),
    margin=dict(l=10, r=10, t=60, b=10),
    hoverlabel=dict(bgcolor="white", font_size=13),
))
pio.templates.default = "plotly_white+airline"

st.set_page_config(page_title="Airline Passenger Satisfaction", page_icon="✈️", layout="wide")

# ---------------------------------------------------------------- custom styling
st.markdown(f"""
<style>
    .block-container {{padding-top: 1.6rem; padding-bottom: 2rem;}}
    .hero {{
        background: linear-gradient(120deg, {NAVY} 0%, #15407a 55%, {SKY} 100%);
        border-radius: 18px; padding: 26px 32px; color: white; margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(11,31,58,0.18); position: relative; overflow: hidden;
    }}
    .hero h1 {{color: white; margin: 0; font-size: 2.1rem; font-weight: 800;}}
    .hero p {{color: #d6e4f7; margin: 6px 0 0 0; font-size: 1.05rem;}}
    .hero .plane {{position: absolute; right: 28px; top: 8px; font-size: 5.5rem; opacity: 0.25;
                   animation: fly 6s ease-in-out infinite;}}
    @keyframes fly {{0% {{transform: translate(0,0) rotate(-8deg);}} 50% {{transform: translate(-22px,10px) rotate(-2deg);}}
                     100% {{transform: translate(0,0) rotate(-8deg);}}}}
    .kpi {{
        background: white; border-radius: 16px; padding: 16px 18px; border: 1px solid #e6ebf1;
        box-shadow: 0 4px 14px rgba(11,31,58,0.07); transition: transform .2s, box-shadow .2s; height: 100%;
    }}
    .kpi:hover {{transform: translateY(-4px); box-shadow: 0 10px 24px rgba(11,31,58,0.14);}}
    .kpi .icon {{font-size: 1.6rem; width: 46px; height: 46px; border-radius: 50%; display: flex;
                 align-items: center; justify-content: center; margin-bottom: 8px;}}
    .kpi .value {{font-size: 1.75rem; font-weight: 800; color: {NAVY}; line-height: 1.1;}}
    .kpi .label {{font-size: 0.85rem; color: {MUTED}; margin-top: 2px;}}
    .kpi .delta-up {{color: #1a8f5c; font-size: 0.8rem; font-weight: 700;}}
    .kpi .delta-down {{color: #c94a1c; font-size: 0.8rem; font-weight: 700;}}
    .section-title {{font-size: 1.35rem; font-weight: 800; color: {NAVY}; margin: 18px 0 4px 0;}}
    .section-sub {{color: {MUTED}; margin-bottom: 10px;}}
    .insight {{
        border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; color: #1b1f24;
        background: #eef4fc; border: 1px solid #d6e4f7;
    }}
    .insight.warn {{background: #fdf0ea; border-color: #f6d3c3;}}
    .insight b.big {{font-size: 1.5rem; color: {NAVY}; display: block;}}
    .persona {{
        border-radius: 16px; padding: 18px; color: white; height: 100%;
        box-shadow: 0 6px 18px rgba(11,31,58,0.15);
    }}
    .persona .emoji {{font-size: 2.4rem;}}
    .persona .rate {{font-size: 2rem; font-weight: 800;}}
    .persona .name {{font-weight: 700; font-size: 1.05rem;}}
    .persona .desc {{font-size: 0.85rem; opacity: 0.92;}}
    [data-testid="stSidebar"] {{background: linear-gradient(180deg, {NAVY} 0%, #15407a 100%);}}
    [data-testid="stSidebar"] * {{color: #eaf1fb !important;}}
    [data-testid="stSidebar"] [data-baseweb="tag"] {{background-color: {SKY} !important;}}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{background-color: rgba(255,255,255,0.08);}}
</style>
""", unsafe_allow_html=True)


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
SHORT_SERVICE_NAMES = {
    "inflight_wifi_service": "Wifi", "departure_arrival_time_convenient": "Time convenience",
    "ease_of_online_booking": "Online booking", "gate_location": "Gate location", "food_and_drink": "Food & drink",
    "online_boarding": "Online boarding", "seat_comfort": "Seat comfort", "inflight_entertainment": "Entertainment",
    "on_board_service": "On-board service", "leg_room_service": "Leg room", "baggage_handling": "Baggage",
    "checkin_service": "Check-in", "inflight_service": "Inflight service", "cleanliness": "Cleanliness",
}
OVERALL_RATE = clean_df["is_satisfied"].mean() * 100


# ---------------------------------------------------------------- helpers
def pretty_name(column):
    """snake_case -> Title Case label."""
    return SHORT_SERVICE_NAMES.get(column, column.replace("_", " ").title())


def satisfaction_rate_by(df, columns):
    """Satisfaction rate (%) and number of passengers for every group of the given column(s)."""
    table = (df.groupby(columns, observed=True)["is_satisfied"]
               .agg(satisfaction_rate="mean", passengers="count").reset_index())
    table["satisfaction_rate"] = (table["satisfaction_rate"] * 100).round(1)
    return table


def as_text(df):
    """Copy with categorical columns as plain text plus a count column (needed by sunburst / treemap)."""
    out = df.assign(passengers=1)
    for column in CATEGORY_ORDERS:
        out[column] = out[column].astype(str)
    return out


def kpi_card(column, icon, value, label, color, delta=None):
    """Render a styled KPI card with an icon bubble and an optional delta vs. all passengers."""
    delta_html = ""
    if delta is not None:
        css = "delta-up" if delta >= 0 else "delta-down"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{css}">{arrow} {abs(delta):.1f} pts vs all passengers</div>'
    column.markdown(f"""
        <div class="kpi">
            <div class="icon" style="background:{color}22;">{icon}</div>
            <div class="value">{value}</div>
            <div class="label">{label}</div>
            {delta_html}
        </div>""", unsafe_allow_html=True)


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>',
                unsafe_allow_html=True)


def insight(text, warn=False):
    st.markdown(f'<div class="insight{" warn" if warn else ""}">{text}</div>', unsafe_allow_html=True)


def gauge(value, title, color):
    """Gauge chart showing a percentage, with the overall average as a threshold marker."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=value, number=dict(suffix="%", font=dict(size=40, color=NAVY)),
        delta=dict(reference=OVERALL_RATE, suffix=" pts", valueformat=".1f",
                   increasing=dict(color="#1a8f5c"), decreasing=dict(color="#c94a1c")),
        title=dict(text=title, font=dict(size=15, color=MUTED)),
        gauge=dict(axis=dict(range=[0, 100], ticksuffix="%"), bar=dict(color=color, thickness=0.75),
                   bgcolor="#eef2f7", borderwidth=0,
                   threshold=dict(line=dict(color=NAVY, width=3), thickness=0.85, value=OVERALL_RATE)),
    ))
    fig.update_layout(height=230, margin=dict(l=20, r=20, t=50, b=10))
    return fig


def stacked_satisfaction_bar(df, column, colors=None):
    """Horizontal 100 % stacked bar of satisfied vs dissatisfied passengers per group."""
    shares = (pd.crosstab(df[column], df["satisfaction"], normalize="index") * 100).round(1)
    long = shares.reset_index().melt(id_vars=column, var_name="satisfaction", value_name="percent")
    fig = px.bar(long, y=column, x="percent", color="satisfaction", text="percent", orientation="h",
                 color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                 labels={column: "", "percent": "% of passengers", "satisfaction": ""})
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="inside", insidetextfont=dict(color="white"),
                      marker_line_color="white", marker_line_width=2)
    fig.update_layout(title=f"Satisfaction by {pretty_name(column)}", barmode="stack", height=320,
                      xaxis_range=[0, 100])
    return fig


# ---------------------------------------------------------------- sidebar: navigation + filters
st.sidebar.markdown("## ✈️ Airline Insights")
page = st.sidebar.radio("Navigate", ["🏠 Overview", "👥 Customers", "⭐ Services", "🛫 Flights & Delays",
                                     "🧹 Data Quality", "💡 Insights & Actions", "🔎 Data Explorer"])
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Filters")


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
st.sidebar.progress(len(filtered_df) / len(clean_df))

# ---------------------------------------------------------------- header + KPIs (every page)
st.markdown("""
<div class="hero">
    <span class="plane">✈️</span>
    <h1>Airline Passenger Satisfaction</h1>
    <p>What makes passengers happy — and what drives them away? · 25,976 survey responses · 14 rated services</p>
</div>""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No passengers match the selected filters. Please widen your selection.")
    st.stop()

satisfied_rate = filtered_df["is_satisfied"].mean() * 100
kpi_columns = st.columns(5)
kpi_card(kpi_columns[0], "👥", f"{len(filtered_df):,}", "Passengers", SKY)
kpi_card(kpi_columns[1], "😊", f"{satisfied_rate:.1f}%", "Satisfied", AQUA, satisfied_rate - OVERALL_RATE)
kpi_card(kpi_columns[2], "⭐", f"{filtered_df['average_service_rating'].mean():.2f}", "Avg. service rating / 5",
         YELLOW)
kpi_card(kpi_columns[3], "⏱️", f"{(filtered_df['arrival_delay'] == 0).mean():.1%}", "On-time arrivals", VIOLET)
kpi_card(kpi_columns[4], "🛫", f"{filtered_df['flight_distance'].median():,.0f} mi", "Median flight distance",
         ORANGE)
st.write("")

# ================================================================ OVERVIEW
if page == "🏠 Overview":
    left, middle, right = st.columns([1.1, 1.3, 1.3])
    with left:
        counts = filtered_df["satisfaction"].value_counts().reindex(CATEGORY_ORDERS["satisfaction"])
        fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.62, sort=False,
                               marker=dict(colors=[SKY, ORANGE], line=dict(color="white", width=3)),
                               textinfo="percent", textfont=dict(size=15, color="white"), pull=[0.04, 0]))
        fig.add_annotation(text=f"<b>{satisfied_rate:.1f}%</b><br><span style='font-size:12px'>satisfied</span>",
                           showarrow=False, font=dict(size=24, color=NAVY))
        fig.update_layout(title="Overall satisfaction", height=380)
        st.plotly_chart(fig, width="stretch")
    with middle:
        fig = px.sunburst(as_text(filtered_df), path=["class", "type_of_travel", "satisfaction"],
                          values="passengers", color="satisfaction",
                          color_discrete_map={**SATISFACTION_COLORS, "(?)": "#c9d8ee"})
        fig.update_traces(insidetextorientation="radial", marker=dict(line=dict(color="white", width=1.5)),
                          hovertemplate="<b>%{label}</b><br>%{value:,} passengers<br>%{percentParent:.1%} of parent")
        fig.update_layout(title="Class → Travel → Satisfaction", height=380)
        st.plotly_chart(fig, width="stretch")
        st.caption("💡 Click a segment to zoom in, click the centre to zoom out")
    with right:
        fig = px.treemap(as_text(filtered_df), path=[px.Constant("All passengers"), "customer_type",
                                                                   "age_group"],
                         values="passengers", color="is_satisfied", color_continuous_scale=SEQUENTIAL_SCALE,
                         range_color=[0, 1])
        fig.update_traces(hovertemplate="<b>%{label}</b><br>%{value:,} passengers<br>Satisfied: %{color:.1%}",
                          texttemplate="<b>%{label}</b><br>%{value:,}", marker=dict(line=dict(color="white", width=2)))
        fig.update_layout(title="Passenger mix (colour = % satisfied)", height=380,
                          coloraxis_colorbar=dict(title="Satisfied", tickformat=".0%"))
        st.plotly_chart(fig, width="stretch")

    section("🎯 Satisfaction gauges by segment", "The dark marker shows the overall average (43.9 %)")
    gauge_columns = st.columns(4)
    segments = [("Business class", filtered_df["class"] == "Business", SKY),
                ("Economy class", filtered_df["class"] == "Economy", ORANGE),
                ("Business travel", filtered_df["type_of_travel"] == "Business Travel", AQUA),
                ("Personal travel", filtered_df["type_of_travel"] == "Personal Travel", PINK)]
    for column, (title, mask, color) in zip(gauge_columns, segments):
        subset = filtered_df[mask]
        if subset.empty:
            column.info(f"No {title.lower()} passengers in the selection")
        else:
            column.plotly_chart(gauge(subset["is_satisfied"].mean() * 100, title, color), width="stretch")

    section("🔀 The passenger journey", "How passengers flow from loyalty → travel purpose → class → satisfaction")
    stages = ["customer_type", "type_of_travel", "class", "satisfaction"]
    node_labels = [label for stage in stages for label in CATEGORY_ORDERS[stage]]
    node_index = {(stage, label): i for i, (stage, label) in
                  enumerate((stage, label) for stage in stages for label in CATEGORY_ORDERS[stage])}
    node_colors = [CUSTOMER_COLORS.get(l) or TRAVEL_COLORS.get(l) or CLASS_COLORS.get(l)
                   or SATISFACTION_COLORS.get(l) for l in node_labels]
    sources, targets, values, link_colors = [], [], [], []
    for a, b in zip(stages[:-1], stages[1:]):
        flows = filtered_df.groupby([a, b], observed=True).size().reset_index(name="n")
        for _, row in flows.iterrows():
            sources.append(node_index[(a, row[a])])
            targets.append(node_index[(b, row[b])])
            values.append(row["n"])
            link_colors.append("rgba(42,120,214,0.25)" if row[b] == "Satisfied" else
                               "rgba(235,104,52,0.25)" if row[b] == "Neutral or Dissatisfied" else
                               "rgba(150,165,185,0.25)")
    fig = go.Figure(go.Sankey(
        node=dict(label=node_labels, color=node_colors, pad=22, thickness=22, line=dict(color="white", width=1)),
        link=dict(source=sources, target=targets, value=values, color=link_colors,
                  hovertemplate="%{source.label} → %{target.label}<br>%{value:,} passengers<extra></extra>")))
    fig.update_layout(height=460, font=dict(size=13))
    st.plotly_chart(fig, width="stretch")

# ================================================================ CUSTOMERS
elif page == "👥 Customers":
    section("🧑‍🤝‍🧑 Customer personas", "Satisfaction rate of the four main passenger types")
    personas = [
        ("💼", "The Business Flyer", "Business travel · Business class",
         (filtered_df["type_of_travel"] == "Business Travel") & (filtered_df["class"] == "Business"), SKY),
        ("🧳", "The Budget Professional", "Business travel · Economy / Eco Plus",
         (filtered_df["type_of_travel"] == "Business Travel") & (filtered_df["class"] != "Business"), VIOLET),
        ("🏖️", "The Holiday Maker", "Personal travel · any class",
         filtered_df["type_of_travel"] == "Personal Travel", ORANGE),
        ("🔁", "The Switcher", "Disloyal customer · any trip",
         filtered_df["customer_type"] == "Disloyal Customer", "#7a5c00"),
    ]
    persona_columns = st.columns(4)
    for column, (emoji, name, desc, mask, color) in zip(persona_columns, personas):
        subset = filtered_df[mask]
        rate_text = f"{subset['is_satisfied'].mean():.0%}" if len(subset) else "—"
        column.markdown(f"""
            <div class="persona" style="background: linear-gradient(135deg, {color} 0%, {NAVY} 140%);">
                <div class="emoji">{emoji}</div>
                <div class="name">{name}</div>
                <div class="desc">{desc}</div>
                <div class="rate">{rate_text}</div>
                <div class="desc">satisfied · {len(subset):,} passengers</div>
            </div>""", unsafe_allow_html=True)

    st.write("")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(stacked_satisfaction_bar(filtered_df, "class"), width="stretch")
        st.plotly_chart(stacked_satisfaction_bar(filtered_df, "customer_type"), width="stretch")
    with right:
        st.plotly_chart(stacked_satisfaction_bar(filtered_df, "type_of_travel"), width="stretch")
        st.plotly_chart(stacked_satisfaction_bar(filtered_df, "gender"), width="stretch")

    section("🎂 Age", "How age shapes satisfaction")
    left, right = st.columns(2)
    with left:
        fig = px.histogram(filtered_df, x="age", color="satisfaction", nbins=40, barmode="overlay", opacity=0.7,
                           color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                           marginal="box", labels={"age": "Age"})
        fig.update_layout(title="Age distribution by satisfaction", height=420)
        st.plotly_chart(fig, width="stretch")
    with right:
        age_rate = satisfaction_rate_by(filtered_df, "age")
        age_rate["smoothed"] = age_rate["satisfaction_rate"].rolling(5, center=True, min_periods=1).mean()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=age_rate["age"], y=age_rate["passengers"], name="Passengers", yaxis="y2",
                             marker_color="#dfe7f2", hovertemplate="Age %{x}: %{y:,} passengers<extra></extra>"))
        fig.add_trace(go.Scatter(x=age_rate["age"], y=age_rate["smoothed"], name="Satisfied % (5-yr avg)",
                                 mode="lines", line=dict(color=SKY, width=4, shape="spline"), fill="tozeroy",
                                 fillcolor="rgba(42,120,214,0.12)",
                                 hovertemplate="Age %{x}: %{y:.1f}% satisfied<extra></extra>"))
        fig.update_layout(title="Satisfaction rate across ages", height=420,
                          yaxis=dict(title="Satisfied (%)", range=[0, 100], ticksuffix="%"),
                          yaxis2=dict(overlaying="y", side="right", showgrid=False, showticklabels=False),
                          xaxis_title="Age")
        st.plotly_chart(fig, width="stretch")

    section("🎞️ Animated view", "Press ▶ to watch satisfaction change across age groups for every class")
    animated = satisfaction_rate_by(filtered_df, ["age_group", "class", "type_of_travel"])
    fig = px.bar(animated, x="class", y="satisfaction_rate", color="type_of_travel", barmode="group",
                 animation_frame="age_group", text="satisfaction_rate", color_discrete_map=TRAVEL_COLORS,
                 category_orders=CATEGORY_ORDERS, range_y=[0, 100], hover_data=["passengers"],
                 labels={"satisfaction_rate": "Satisfied (%)", "class": "", "type_of_travel": ""})
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig.update_layout(height=470)
    st.plotly_chart(fig, width="stretch")

    section("🌡️ Customer heatmap", "Satisfaction rate (%) for every age group × class")
    heat = filtered_df.pivot_table(index="age_group", columns="class", values="is_satisfied", aggfunc="mean",
                                   observed=True) * 100
    fig = px.imshow(heat.round(1), text_auto=True, color_continuous_scale=SEQUENTIAL_SCALE, zmin=0, zmax=100,
                    aspect="auto", labels=dict(color="Satisfied %", x="", y=""))
    fig.update_layout(height=380)
    st.plotly_chart(fig, width="stretch")

# ================================================================ SERVICES
elif page == "⭐ Services":
    means = filtered_df.groupby("satisfaction", observed=True)[SERVICE_COLUMNS].mean().T
    means = means.reindex(columns=CATEGORY_ORDERS["satisfaction"])
    means["gap"] = means["Satisfied"] - means["Neutral or Dissatisfied"]

    left, right = st.columns([1.1, 1])
    with left:
        fig = go.Figure()
        labels = [pretty_name(c) for c in SERVICE_COLUMNS] + [pretty_name(SERVICE_COLUMNS[0])]
        for group, color, fill in [("Satisfied", SKY, "rgba(42,120,214,0.25)"),
                                   ("Neutral or Dissatisfied", ORANGE, "rgba(235,104,52,0.25)")]:
            values = list(means[group]) + [means[group].iloc[0]]
            fig.add_trace(go.Scatterpolar(r=values, theta=labels, fill="toself", name=group,
                                          line=dict(color=color, width=3), fillcolor=fill))
        fig.update_layout(title="Service fingerprint: satisfied vs dissatisfied", height=520,
                          polar=dict(radialaxis=dict(range=[1, 5], tickvals=[1, 2, 3, 4, 5]),
                                     bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, width="stretch")
    with right:
        ranked = means.sort_values("gap")
        fig = go.Figure(go.Bar(x=ranked["gap"], y=[pretty_name(c) for c in ranked.index], orientation="h",
                               marker=dict(color=ranked["gap"], colorscale=[[0, ORANGE], [0.3, "#c9d8ee"], [1, SKY]]),
                               text=[f"{g:+.2f}" for g in ranked["gap"]], textposition="outside",
                               hovertemplate="%{y}: gap %{x:+.2f}<extra></extra>"))
        fig.update_layout(title="Rating gap (satisfied − dissatisfied)", height=520,
                          xaxis=dict(title="Difference in average rating", range=[-0.4, 1.8]))
        st.plotly_chart(fig, width="stretch")

    section("📊 How passengers rated each service", "Share of each rating 1–5")
    distribution = (filtered_df[SERVICE_COLUMNS].apply(lambda c: c.value_counts(normalize=True)).T * 100)
    distribution = distribution.loc[filtered_df[SERVICE_COLUMNS].mean().sort_values().index]
    distribution.index = [pretty_name(c) for c in distribution.index]
    rating_colors = {1.0: "#c94a1c", 2.0: "#f19a72", 3.0: "#d5dbe3", 4.0: "#7fb0ea", 5.0: "#1e5fae"}
    fig = go.Figure()
    for rating in [1.0, 2.0, 3.0, 4.0, 5.0]:
        fig.add_trace(go.Bar(y=distribution.index, x=distribution[rating], name=f"{int(rating)} ★", orientation="h",
                             marker=dict(color=rating_colors[rating], line=dict(color="white", width=1)),
                             hovertemplate=f"%{{y}} · {int(rating)}★: %{{x:.1f}}%<extra></extra>"))
    fig.update_layout(barmode="stack", height=520, xaxis=dict(title="% of passengers", ticksuffix="%"),
                      title="Rating distribution per service (sorted by average rating)")
    st.plotly_chart(fig, width="stretch")

    section("🔍 Explore one service", "How the chance of being satisfied changes with each rating")
    chosen = st.selectbox("Choose a service", means.sort_values("gap", ascending=False).index,
                          format_func=pretty_name)
    left, right = st.columns([2, 1])
    with left:
        by_class = satisfaction_rate_by(filtered_df, [chosen, "class"])
        fig = px.line(by_class, x=chosen, y="satisfaction_rate", color="class", markers=True,
                      color_discrete_map=CLASS_COLORS, category_orders=CATEGORY_ORDERS, hover_data=["passengers"],
                      labels={chosen: "Rating given", "satisfaction_rate": "Satisfied (%)", "class": ""})
        fig.update_traces(line=dict(width=3.5), marker=dict(size=11, line=dict(color="white", width=2)))
        fig.update_layout(title=f"Satisfaction by {pretty_name(chosen)} rating, per class", height=420,
                          xaxis_dtick=1, yaxis_range=[0, 105])
        st.plotly_chart(fig, width="stretch")
    with right:
        top_rate = filtered_df.loc[filtered_df[chosen] == 5, "is_satisfied"].mean() * 100
        low_rate = filtered_df.loc[filtered_df[chosen] <= 2, "is_satisfied"].mean() * 100
        st.write("")
        insight(f"<b class='big'>{top_rate:.0f}%</b>satisfied among passengers who rated "
                f"<b>{pretty_name(chosen)}</b> 5 ★")
        insight(f"<b class='big'>{low_rate:.0f}%</b>satisfied among passengers who rated it 1–2 ★", warn=True)
        insight(f"<b class='big'>{filtered_df[chosen].mean():.2f} / 5</b>average rating of "
                f"{pretty_name(chosen)}")

    section("🧩 Which services move together?", "Spearman correlation between ratings and satisfaction")
    corr = filtered_df[SERVICE_COLUMNS + ["is_satisfied"]].corr(method="spearman")
    corr.index = corr.columns = [pretty_name(c) if c != "is_satisfied" else "SATISFIED" for c in corr.columns]
    fig = px.imshow(corr.round(2), text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
    fig.update_traces(textfont_size=10)
    fig.update_layout(height=620)
    st.plotly_chart(fig, width="stretch")

# ================================================================ FLIGHTS & DELAYS
elif page == "🛫 Flights & Delays":
    left, right = st.columns(2)
    with left:
        delay_rate = satisfaction_rate_by(filtered_df, "delay_group")
        fig = go.Figure(go.Funnel(y=delay_rate["delay_group"].astype(str), x=delay_rate["satisfaction_rate"],
                                  textinfo="value", texttemplate="%{x:.1f}% satisfied",
                                  marker=dict(color=[SKY, "#5b95df", "#e58a63", ORANGE]),
                                  hovertemplate="%{y}: %{x:.1f}% satisfied<extra></extra>"))
        fig.update_layout(title="Satisfaction shrinks as delays grow", height=400)
        st.plotly_chart(fig, width="stretch")
    with right:
        share = filtered_df["delay_group"].value_counts().reindex(CATEGORY_ORDERS["delay_group"])
        fig = go.Figure(go.Pie(labels=share.index, values=share.values, hole=0.55, sort=False,
                               marker=dict(colors=[AQUA, YELLOW, "#f19a72", "#c94a1c"],
                                           line=dict(color="white", width=3))))
        fig.update_layout(title="How late do passengers arrive?", height=400)
        st.plotly_chart(fig, width="stretch")

    section("📈 Delay curve", "Satisfaction rate for growing arrival delays")
    delay_bins = pd.cut(filtered_df["arrival_delay"], bins=[-1, 0, 5, 10, 20, 30, 45, 60, 90, 120, 180, 10000],
                        labels=["0", "1-5", "6-10", "11-20", "21-30", "31-45", "46-60", "61-90", "91-120",
                                "121-180", "180+"])
    curve = filtered_df.groupby(delay_bins, observed=True)["is_satisfied"].agg(["mean", "count"]).reset_index()
    fig = go.Figure(go.Scatter(x=curve["arrival_delay"].astype(str), y=curve["mean"] * 100, mode="lines+markers",
                               line=dict(color=ORANGE, width=4, shape="spline"), fill="tozeroy",
                               fillcolor="rgba(235,104,52,0.12)",
                               marker=dict(size=curve["count"] / curve["count"].max() * 30 + 8, color=ORANGE,
                                           line=dict(color="white", width=2)),
                               customdata=curve["count"],
                               hovertemplate="Delay %{x} min<br>%{y:.1f}% satisfied<br>%{customdata:,} passengers"
                                             "<extra></extra>"))
    fig.add_hline(y=OVERALL_RATE, line_dash="dash", line_color=NAVY, annotation_text="overall average")
    fig.update_layout(height=400, xaxis_title="Arrival delay (minutes) · bubble size = passengers",
                      yaxis=dict(title="Satisfied (%)", range=[0, 70], ticksuffix="%"))
    st.plotly_chart(fig, width="stretch")

    section("🌍 Flight distance", "Long flights look happier — but mainly because they are flown in Business class")
    left, right = st.columns(2)
    with left:
        fig = px.violin(filtered_df, x="class", y="flight_distance", color="satisfaction", box=True,
                        color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS,
                        labels={"class": "", "flight_distance": "Flight distance (miles)"})
        fig.update_layout(title="Flight distance by class and satisfaction", height=440, violinmode="group")
        st.plotly_chart(fig, width="stretch")
    with right:
        heat = filtered_df.pivot_table(index="distance_group", columns="class", values="is_satisfied",
                                       aggfunc="mean", observed=True) * 100
        fig = px.imshow(heat.round(1), text_auto=True, color_continuous_scale=SEQUENTIAL_SCALE, zmin=0, zmax=100,
                        aspect="auto", labels=dict(color="Satisfied %", x="", y=""))
        fig.update_traces(textfont_size=16)
        fig.update_layout(title="Satisfaction rate (%) by distance and class", height=440)
        st.plotly_chart(fig, width="stretch")

    section("🗺️ Age × distance density", "Where are satisfied and dissatisfied passengers concentrated?")
    fig = px.density_heatmap(filtered_df, x="age", y="flight_distance", z="is_satisfied", histfunc="avg",
                             nbinsx=30, nbinsy=25, color_continuous_scale=SEQUENTIAL_SCALE, range_color=[0, 1],
                             labels={"age": "Age", "flight_distance": "Flight distance (miles)",
                                     "is_satisfied": "Satisfied"})
    fig.update_layout(height=460, coloraxis_colorbar=dict(title="Satisfied", tickformat=".0%"))
    st.plotly_chart(fig, width="stretch")

# ================================================================ DATA QUALITY
elif page == "🧹 Data Quality":
    raw_service_columns = list(raw_df.loc[:, "Inflight wifi service":"Cleanliness"].columns)
    zero_ratings = int((raw_df[raw_service_columns] == 0).sum().sum())
    issue_columns = st.columns(4)
    kpi_card(issue_columns[0], "❓", int(raw_df["Arrival Delay in Minutes"].isna().sum()), "Missing arrival delays",
             ORANGE)
    kpi_card(issue_columns[1], "0️⃣", f"{zero_ratings:,}", "'0 = Not Applicable' ratings", YELLOW)
    kpi_card(issue_columns[2], "🏷️", 4, "Columns with inconsistent labels", PINK)
    kpi_card(issue_columns[3], "🗑️", 1, "Useless index column", VIOLET)
    st.write("")

    left, right = st.columns(2)
    with left:
        zero_by_service = (raw_df[raw_service_columns] == 0).sum().sort_values()
        zero_by_service = zero_by_service[zero_by_service > 0]
        fig = px.bar(x=zero_by_service.values, y=zero_by_service.index, orientation="h", text=zero_by_service.values,
                     labels={"x": "Number of 0 ratings", "y": ""}, color=zero_by_service.values,
                     color_continuous_scale=["#f6d3c3", ORANGE])
        fig.update_layout(title="'0 = Not Applicable' ratings per service (raw data)", height=420,
                          coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")
    with right:
        sample = raw_df.dropna().sample(3000, random_state=1)
        fig = px.scatter(sample, x="Departure Delay in Minutes", y="Arrival Delay in Minutes", opacity=0.45,
                         trendline=None, color_discrete_sequence=[SKY])
        fig.update_layout(title="Departure vs arrival delay (r = 0.96) — basis for filling missing values",
                          height=420)
        st.plotly_chart(fig, width="stretch")

    section("🔁 Before → after", "Every change made during cleaning")
    cleaning_log = pd.DataFrame({
        "Problem": ["83 missing arrival delays", "Arrival delay stored as float", "Rating 0 = 'Not Applicable'",
                    "Inconsistent labels ('disloyal Customer', 'Eco' …)", "Extreme delays / distances",
                    "Useless 'Unnamed: 0' column", "Column names with spaces and slashes", "No segment columns"],
        "Action": ["Filled with the passenger's departure delay", "Converted to integer",
                   "Replaced by NaN so they don't drag averages down", "Standardised capitalisation, Eco → Economy",
                   "Verified as genuine and kept; grouped into bins", "Dropped", "Converted to snake_case",
                   "Added age / distance / delay groups and average rating"],
        "Status": ["✅ Fixed"] * 8,
    })
    st.dataframe(cleaning_log, hide_index=True, width="stretch")

    label_examples = pd.DataFrame({
        "Column": ["Customer Type", "Type of Travel", "Class", "Class", "satisfaction", "satisfaction"],
        "Before": ["disloyal Customer", "Business travel", "Eco", "Eco Plus", "satisfied", "neutral or dissatisfied"],
        "After": ["Disloyal Customer", "Business Travel", "Economy", "Economy Plus", "Satisfied",
                  "Neutral or Dissatisfied"],
    })
    st.dataframe(label_examples, hide_index=True, width="stretch")

# ================================================================ INSIGHTS
elif page == "💡 Insights & Actions":
    section("💡 Key insights", "What the data tells us")
    insight_columns = st.columns(3)
    with insight_columns[0]:
        insight("<b class='big'>43.9%</b>of passengers are satisfied — the majority are neutral or dissatisfied.",
                warn=True)
        insight("<b class='big'>69.5% vs 19.4%</b>satisfied in Business class vs Economy.")
    with insight_columns[1]:
        insight("<b class='big'>~10%</b>of personal (leisure) travellers are satisfied — in every class.", warn=True)
        insight("<b class='big'>+1.44</b>rating gap for online boarding — the #1 service driver.")
    with insight_columns[2]:
        insight("<b class='big'>2.81 / 5</b>wifi is the lowest-rated service, yet 99% of those rating it 5 ★ are "
                "satisfied.", warn=True)
        insight("<b class='big'>47.9% → 35.2%</b>satisfaction from on-time to more than one hour late.")

    section("🏆 What drives satisfaction the most?", "Strength of association with satisfaction (Cramér's V)")
    drivers = pd.DataFrame({"Factor": ["Class", "Type of travel", "Age group", "Customer type", "Arrival delay",
                                       "Gender"],
                            "Strength": [0.50, 0.45, 0.25, 0.18, 0.10, 0.01]}).sort_values("Strength")
    fig = px.bar(drivers, x="Strength", y="Factor", orientation="h", text="Strength", color="Strength",
                 color_continuous_scale=["#c9d8ee", SKY, NAVY])
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(height=380, coloraxis_showscale=False, xaxis_range=[0, 0.6], yaxis_title="")
    st.plotly_chart(fig, width="stretch")

    section("🚀 Recommendations", "Ordered by expected impact")
    recommendations = [
        ("📶", "Fix the digital journey", "Wifi, online boarding and online booking are rated lowest yet are top drivers."),
        ("💺", "Upgrade the Economy experience", "Fewer than 1 in 5 Economy passengers are satisfied."),
        ("🏖️", "Win over leisure travellers", "Family services, flexible fares and better entertainment."),
        ("🤝", "Re-engage disloyal customers", "Only 25% satisfied — targeted loyalty offers."),
        ("⏱️", "Keep delays short", "Every extra delay band lowers satisfaction."),
    ]
    recommendation_columns = st.columns(5)
    for column, (icon, title, text) in zip(recommendation_columns, recommendations):
        column.markdown(f"""<div class="kpi"><div class="icon" style="background:{SKY}22;">{icon}</div>
                            <div style="font-weight:800;color:{NAVY};">{title}</div>
                            <div class="label">{text}</div></div>""", unsafe_allow_html=True)

# ================================================================ DATA EXPLORER
elif page == "🔎 Data Explorer":
    section("🔎 Build your own chart", "Pick any two variables")
    numeric_columns = ["age", "flight_distance", "departure_delay", "arrival_delay", "average_service_rating"]
    categorical_columns = ["class", "type_of_travel", "customer_type", "gender", "age_group", "distance_group",
                           "delay_group"]
    left, middle, right = st.columns(3)
    x_axis = left.selectbox("X axis", categorical_columns + numeric_columns, format_func=pretty_name)
    y_axis = middle.selectbox("Y axis", numeric_columns + SERVICE_COLUMNS, index=4, format_func=pretty_name)
    chart_type = right.radio("Chart type", ["Box", "Violin", "Scatter"], horizontal=True)
    sample = filtered_df.sample(min(len(filtered_df), 5000), random_state=0)
    if chart_type == "Box":
        fig = px.box(sample, x=x_axis, y=y_axis, color="satisfaction", color_discrete_map=SATISFACTION_COLORS,
                     category_orders=CATEGORY_ORDERS)
    elif chart_type == "Violin":
        fig = px.violin(sample, x=x_axis, y=y_axis, color="satisfaction", box=True,
                        color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS)
    else:
        fig = px.scatter(sample, x=x_axis, y=y_axis, color="satisfaction", opacity=0.5,
                         color_discrete_map=SATISFACTION_COLORS, category_orders=CATEGORY_ORDERS)
    fig.update_layout(height=480, xaxis_title=pretty_name(x_axis), yaxis_title=pretty_name(y_axis),
                      title=f"{pretty_name(y_axis)} by {pretty_name(x_axis)} (sample of {len(sample):,})")
    st.plotly_chart(fig, width="stretch")

    section("📋 Cleaned data", "Filtered by the sidebar")
    st.dataframe(filtered_df, width="stretch", height=420)
    st.download_button("⬇️ Download filtered data as CSV", filtered_df.to_csv(index=False).encode("utf-8"),
                       file_name="airline_satisfaction_filtered.csv", mime="text/csv")
    with st.expander("📐 Summary statistics"):
        st.dataframe(filtered_df.describe().T.round(2), width="stretch")

st.markdown(f"<div style='text-align:center;color:{MUTED};margin-top:30px;font-size:0.85rem;'>"
            "Mid Project · Airline Passenger Satisfaction · Python, Pandas, Plotly &amp; Streamlit</div>",
            unsafe_allow_html=True)

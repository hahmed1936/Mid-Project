"""Airline Passenger Satisfaction — interactive Streamlit dashboard.

Run locally with:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

BASE_DIR = Path(__file__).parent
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
    """Load the cleaned dataset produced by the notebook."""
    clean = pd.read_csv(CLEAN_DATA_PATH)
    for column, order in CATEGORY_ORDERS.items():
        clean[column] = pd.Categorical(clean[column], categories=order)
    return clean


clean_df = load_data()
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


def short_label(label):
    """Put the bracket part of a long group name on a second line, e.g. 'Short-haul<br>(<800 mi)'."""
    return str(label).replace(" (", "<br>(")


def satisfaction_rate_by(df, column):
    """Satisfaction rate (%) and number of passengers for every group of a column."""
    table = (df.groupby(column, observed=True)["is_satisfied"]
               .agg(satisfaction_rate="mean", passengers="count").reset_index())
    table["satisfaction_rate"] = (table["satisfaction_rate"] * 100).round(1)
    return table


def section(title, subtitle=""):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>',
                unsafe_allow_html=True)


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


def insight(text, warn=False):
    st.markdown(f'<div class="insight{" warn" if warn else ""}">{text}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- the only three chart types used in the dashboard
_chart_counter = [0]


def plot(container, fig):
    """Show a Plotly chart with a unique key (the same chart can appear in more than one tab)."""
    _chart_counter[0] += 1
    container.plotly_chart(fig, width="stretch", key=f"chart_{_chart_counter[0]}")


def donut_chart(df):
    """Chart type 1 — donut: share of satisfied vs dissatisfied passengers."""
    counts = df["satisfaction"].value_counts().reindex(CATEGORY_ORDERS["satisfaction"])
    rate = df["is_satisfied"].mean() * 100
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.62, sort=False,
                           marker=dict(colors=[SKY, ORANGE], line=dict(color="white", width=3)),
                           textinfo="percent", textfont=dict(size=16, color="white"),
                           hovertemplate="%{label}: %{value:,} passengers<extra></extra>"))
    fig.add_annotation(text=f"<b>{rate:.1f}%</b><br><span style='font-size:13px'>satisfied</span>",
                       showarrow=False, font=dict(size=26, color=NAVY))
    fig.update_layout(title="Satisfied vs not satisfied", height=380)
    return fig


def satisfaction_bar(df, column, title):
    """Chart type 2 — one bar per group = % of satisfied passengers. Blue = above average, orange = below."""
    table = satisfaction_rate_by(df, column)
    table = table[table["passengers"] > 0]
    colors = [SKY if r >= OVERALL_RATE else ORANGE for r in table["satisfaction_rate"]]
    fig = go.Figure(go.Bar(x=[short_label(v) for v in table[column]], y=table["satisfaction_rate"],
                           marker=dict(color=colors, line=dict(color="white", width=1.5)),
                           text=[f"<b>{r:.0f}%</b>" for r in table["satisfaction_rate"]], textposition="outside",
                           customdata=table["passengers"],
                           hovertemplate="%{x}<br>%{y:.1f}% satisfied<br>%{customdata:,} passengers<extra></extra>"))
    fig.add_hline(y=OVERALL_RATE, line_dash="dash", line_color=NAVY,
                  annotation_text=f"average {OVERALL_RATE:.0f}%", annotation_position="top left")
    fig.update_layout(title=title, height=360, yaxis=dict(title="% satisfied", range=[0, 105], ticksuffix="%"),
                      xaxis=dict(title="", tickangle=0), showlegend=False)
    return fig, table


def count_bar(labels, values, title, value_title, colors=None, horizontal=False, number_format="{:,.0f}"):
    """Chart type 3 — simple bars of a number per group (passengers, ratings ...)."""
    colors = colors or [SKY] * len(values)
    text = [f"<b>{number_format.format(v)}</b>" for v in values]
    bar = (go.Bar(y=labels, x=values, orientation="h", text=text, textposition="outside", marker_color=colors,
                  hovertemplate="%{y}: %{x}<extra></extra>") if horizontal else
           go.Bar(x=labels, y=values, text=text, textposition="outside", marker_color=colors,
                  hovertemplate="%{x}: %{y}<extra></extra>"))
    fig = go.Figure(bar)
    axis = dict(title=value_title, range=[0, max(values) * 1.18])
    fig.update_layout(title=title, height=max(360, 34 * len(labels)) if horizontal else 360, showlegend=False,
                      **({"xaxis": axis, "yaxis": dict(title="")} if horizontal else
                         {"yaxis": axis, "xaxis": dict(title="", tickangle=0)}))
    return fig


def show_satisfaction_bar(df, column, title, container=st):
    """Draw a satisfaction bar and, under it, one line saying how to read it and which group is highest/lowest."""
    fig, table = satisfaction_bar(df, column, title)
    plot(container, fig)
    if len(table) > 1:
        best = table.loc[table["satisfaction_rate"].idxmax()]
        worst = table.loc[table["satisfaction_rate"].idxmin()]
        container.caption(f"📖 Each bar = % of passengers in that group who are satisfied. "
                          f"**Highest:** {best[column]} ({best['satisfaction_rate']:.0f}%) · "
                          f"**Lowest:** {worst[column]} ({worst['satisfaction_rate']:.0f}%)")


# ---------------------------------------------------------------- sidebar filters
st.sidebar.markdown("## ✈️ Airline Insights")
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

# ---------------------------------------------------------------- header + KPIs (every tab)
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
st.info("📖 **How to read the bar charts:** each bar shows the % of satisfied passengers in a group. "
        "**Blue** = above the average (dashed line), **orange** = below it. Hover over any bar for details.")

tab_overview, tab_customers, tab_services, tab_flights = st.tabs(
    ["🏠 Overview", "👥 Customers", "⭐ Services", "🛫 Flights & Delays"])

# ================================================================ OVERVIEW
with tab_overview:
    left, middle, right = st.columns(3)
    with left:
        plot(st, donut_chart(filtered_df))
        st.caption(f"📖 Blue = satisfied, orange = neutral or dissatisfied. "
                   f"**{satisfied_rate:.0f}%** of the selected passengers are satisfied.")
    show_satisfaction_bar(filtered_df, "class", "Satisfaction by class", middle)
    show_satisfaction_bar(filtered_df, "type_of_travel", "Satisfaction by travel purpose", right)

    section("🔢 How many passengers?", "Number of passengers in each group")
    left, right = st.columns(2)
    class_counts = filtered_df["class"].value_counts().reindex(CATEGORY_ORDERS["class"]).dropna()
    plot(left, count_bar(list(class_counts.index), list(class_counts.values), "Passengers per class",
                         "Passengers"))
    travel_counts = filtered_df["type_of_travel"].value_counts().reindex(CATEGORY_ORDERS["type_of_travel"]).dropna()
    plot(right, count_bar(list(travel_counts.index), list(travel_counts.values),
                          "Passengers per travel purpose", "Passengers", colors=[SKY, PINK]))

# ================================================================ CUSTOMERS
with tab_customers:
    section("🧑‍🤝‍🧑 Customer types", "% satisfied in the four main passenger types")
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
    show_satisfaction_bar(filtered_df, "customer_type", "Satisfaction by loyalty", left)
    show_satisfaction_bar(filtered_df, "gender", "Satisfaction by gender", right)

    section("🎂 Age", "Which age groups are happiest?")
    left, right = st.columns(2)
    show_satisfaction_bar(filtered_df, "age_group", "Satisfaction by age group", left)
    age_counts = filtered_df["age_group"].value_counts().reindex(CATEGORY_ORDERS["age_group"]).dropna()
    plot(right, count_bar([short_label(v) for v in age_counts.index], list(age_counts.values),
                          "Passengers per age group", "Passengers"))

# ================================================================ SERVICES
with tab_services:
    averages = filtered_df[SERVICE_COLUMNS].mean().sort_values()
    overall_average = averages.mean()
    section("⭐ How good is each service?", "Average rating from 1 (bad) to 5 (excellent)")
    plot(st, count_bar([pretty_name(c) for c in averages.index], list(averages.values),
                       "Average rating of each service", "Average rating (1-5)",
                       colors=[ORANGE if v < overall_average else SKY for v in averages.values],
                       horizontal=True, number_format="{:.2f}"))
    st.caption(f"📖 Longer bar = better rated. **Orange** = below the average of all services "
               f"({overall_average:.2f}). Weakest: **{pretty_name(averages.index[0])}** "
               f"({averages.iloc[0]:.2f}) · Best: **{pretty_name(averages.index[-1])}** ({averages.iloc[-1]:.2f})")

    section("🔍 Which services make passengers happy?", "Pick a service: how many passengers are satisfied "
                                                       "for each rating they gave it?")
    gaps = (filtered_df[filtered_df["is_satisfied"] == 1][SERVICE_COLUMNS].mean()
            - filtered_df[filtered_df["is_satisfied"] == 0][SERVICE_COLUMNS].mean()).sort_values(ascending=False)
    chosen = st.selectbox("Service", list(gaps.index), format_func=pretty_name)
    left, right = st.columns([2, 1])
    with left:
        by_rating = filtered_df.dropna(subset=[chosen]).assign(rating=lambda d: d[chosen].astype(int).astype(str) + " ★")
        show_satisfaction_bar(by_rating, "rating", f"% satisfied for each {pretty_name(chosen)} rating")
    with right:
        st.write("")
        top_rate = filtered_df.loc[filtered_df[chosen] == 5, "is_satisfied"].mean() * 100
        low_rate = filtered_df.loc[filtered_df[chosen] <= 2, "is_satisfied"].mean() * 100
        insight(f"<b class='big'>{top_rate:.0f}%</b>are satisfied when they rate {pretty_name(chosen)} 5 ★")
        insight(f"<b class='big'>{low_rate:.0f}%</b>are satisfied when they rate it 1–2 ★", warn=True)
    st.caption("📖 The services at the top of the list make the biggest difference: passengers who rate them "
               "high are much more likely to be satisfied.")

# ================================================================ FLIGHTS & DELAYS
with tab_flights:
    section("⏱️ Delays", "Does arriving late make passengers less happy?")
    left, right = st.columns(2)
    show_satisfaction_bar(filtered_df, "delay_group", "Satisfaction by arrival delay", left)
    delay_counts = filtered_df["delay_group"].value_counts().reindex(CATEGORY_ORDERS["delay_group"]).dropna()
    plot(right, count_bar(list(delay_counts.index), list(delay_counts.values), "Passengers per delay group",
                          "Passengers", colors=[AQUA, YELLOW, ORANGE, "#c94a1c"][:len(delay_counts)]))

    section("🌍 Flight distance", "Long flights look happier overall — but inside each class distance changes little")
    show_satisfaction_bar(filtered_df, "distance_group", "Satisfaction by flight distance (all classes)")
    class_columns = st.columns(3)
    for column, travel_class in zip(class_columns, CATEGORY_ORDERS["class"]):
        subset = filtered_df[filtered_df["class"] == travel_class]
        if subset.empty:
            column.info(f"No {travel_class} passengers in the selection")
        else:
            show_satisfaction_bar(subset, "distance_group", f"{travel_class} class only", column)

st.markdown(f"<div style='text-align:center;color:{MUTED};margin-top:30px;font-size:0.85rem;'>"
            "Mid Project · Airline Passenger Satisfaction · Python, Pandas, Plotly &amp; Streamlit</div>",
            unsafe_allow_html=True)

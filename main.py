
import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    ColorBar,
    LinearColorMapper
)
from bokeh.palettes import RdBu11, Category10
from bokeh.transform import linear_cmap, dodge

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Malaysia Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

# Keep original dataset names
BIRTH_FILE = BASE_DIR / "birth_state (1).csv"
MARRIAGE_FILE = BASE_DIR / "marriages_state.csv"
INCOME_FILE = BASE_DIR / "hh_income_state.csv"


# =====================================================
# 2. LOAD DATA
# =====================================================

@st.cache_data
def load_data():

    births = pd.read_csv(BIRTH_FILE)
    marriages = pd.read_csv(MARRIAGE_FILE)
    income = pd.read_csv(INCOME_FILE)

    for df in [births, marriages, income]:
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year

    # Birth data
    births = births.rename(columns={
        "abs": "birth_abs",
        "rate": "birth_rate"
    })

    births["birth_abs"] = pd.to_numeric(
        births["birth_abs"], errors="coerce"
    )
    births["birth_rate"] = pd.to_numeric(
        births["birth_rate"], errors="coerce"
    )

    # Marriage data
    marriages["sex"] = (
        marriages["sex"].astype(str).str.lower().str.strip()
    )

    marriages["abs"] = pd.to_numeric(
        marriages["abs"], errors="coerce"
    )
    marriages["rate"] = pd.to_numeric(
        marriages["rate"], errors="coerce"
    )

    # Average female and male records
    marriages = (
        marriages
        .groupby(["state", "year"], as_index=False)
        .agg(
            marriage_abs=("abs", "mean"),
            marriage_rate=("rate", "mean")
        )
    )

    # Income data
    income["income_mean"] = pd.to_numeric(
        income["income_mean"], errors="coerce"
    )
    income["income_median"] = pd.to_numeric(
        income["income_median"], errors="coerce"
    )

    births = births[
        ["state", "year", "birth_abs", "birth_rate"]
    ]

    income = income[
        ["state", "year", "income_mean", "income_median"]
    ]

    return births, marriages, income


try:
    births, marriages, income = load_data()

except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()


# =====================================================
# 3. MERGE DATASETS
# =====================================================

birth_income = pd.merge(
    births, income,
    on=["state", "year"],
    how="inner"
)

birth_marriage = pd.merge(
    births, marriages,
    on=["state", "year"],
    how="inner"
)

marriage_income = pd.merge(
    marriages, income,
    on=["state", "year"],
    how="inner"
)


# =====================================================
# 4. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("📊 Dashboard Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Economic Prosperity vs. Demographic Growth",
        "Family Formation and Population Dynamics",
        "Socioeconomic Influence on Marriages"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("🔎 Data Filters")

all_states = sorted(
    set(births["state"].dropna())
    | set(marriages["state"].dropna())
    | set(income["state"].dropna())
)

selected_states = st.sidebar.multiselect(
    "Select States",
    options=all_states,
    default=all_states
)

min_year = max(
    2000,
    int(min(
        births["year"].min(),
        marriages["year"].min(),
        income["year"].min()
    ))
)

max_year = int(max(
    births["year"].max(),
    marriages["year"].max(),
    income["year"].max()
))

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

st.sidebar.caption(
    "Source: Department of Statistics Malaysia (DOSM)"
)


# =====================================================
# 5. FILTER FUNCTION
# =====================================================

def apply_filters(df):

    return df[
        df["state"].isin(selected_states)
        & df["year"].between(
            selected_years[0],
            selected_years[1]
        )
    ].copy()


bi = apply_filters(birth_income)
bm = apply_filters(birth_marriage)
mi = apply_filters(marriage_income)

birth_filtered = apply_filters(births)
marriage_filtered = apply_filters(marriages)
income_filtered = apply_filters(income)


# =====================================================
# 6. BOKEH CHART SETTINGS
# =====================================================

def chart_style(title, x_label, y_label):

    p = figure(
        title=title,
        height=400,
        sizing_mode="stretch_width",
        x_axis_label=x_label,
        y_axis_label=y_label,
        toolbar_location="above"
    )

    p.title.text_font_size = "15px"
    p.xaxis.axis_label_text_font_size = "12px"
    p.yaxis.axis_label_text_font_size = "12px"
    p.xaxis.major_label_orientation = 0.8

    return p


def show_chart(p):

    st.bokeh_chart(
        p,
        use_container_width=True
    )


def show_summary(data, columns):

    cols = st.columns(len(columns))

    for col, (label, value) in zip(cols, columns):

        col.metric(label, value)


def correlation_heatmap(data, columns, title):

    corr = data[columns].corr()

    x_values = []
    y_values = []
    values = []

    for row in columns:
        for col in columns:
            x_values.append(col)
            y_values.append(row)
            values.append(corr.loc[row, col])

    source = ColumnDataSource({
        "x": x_values,
        "y": y_values,
        "value": values
    })

    mapper = LinearColorMapper(
        palette=RdBu11,
        low=-1,
        high=1
    )

    p = figure(
        title=title,
        x_range=columns,
        y_range=list(reversed(columns)),
        height=420,
        sizing_mode="stretch_width",
        toolbar_location=None
    )

    p.rect(
        x="x",
        y="y",
        width=1,
        height=1,
        source=source,
        fill_color={
            "field": "value",
            "transform": mapper
        },
        line_color="white"
    )

    p.text(
        x="x",
        y="y",
        text="value",
        source=source,
        text_align="center",
        text_baseline="middle"
    )

    p.add_layout(
        ColorBar(color_mapper=mapper),
        "right"
    )

    p.xaxis.major_label_orientation = 0.8

    return p


# =====================================================
# PAGE 1
# ECONOMIC PROSPERITY VS DEMOGRAPHIC GROWTH
# =====================================================

if page == "Economic Prosperity vs. Demographic Growth":

    st.title(
        "Economic Prosperity vs. Demographic Growth"
    )

    st.write(
        "Explore the relationship between household income "
        "and live births across Malaysian states."
    )

    st.subheader("🎯 Visualization Objective")

    st.write(
        "To examine the relationship between household income "
        "and live births across Malaysian states, identifying "
        "possible socioeconomic patterns in demographic growth."
    )

    st.caption(
        f"Selected period: {selected_years[0]}–{selected_years[1]}"
    )

    if bi.empty:
        st.warning("No matching income and birth records.")
        st.stop()

    # Summary
    state_summary = (
        bi.groupby("state", as_index=False)
        .agg(
            births=("birth_abs", "sum"),
            income=("income_median", "mean")
        )
    )

    valid = bi.dropna(
        subset=["birth_abs", "income_median"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Live Births",
        f"{valid['birth_abs'].sum():,.0f}"
    )

    c2.metric(
        "Average Median Income",
        f"RM {valid['income_median'].mean():,.0f}"
    )

    c3.metric(
        "Highest Income State",
        state_summary.loc[
            state_summary["income"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Highest Birth State",
        state_summary.loc[
            state_summary["births"].idxmax(), "state"
        ]
    )

    st.divider()

    # Chart 1: Scatter
    st.subheader(
        "1. Scatter Plot: Household Income vs Live Births"
    )

    p = chart_style(
        "Income and Live Births",
        "Median Household Income (RM)",
        "Total Live Births"
    )

    source = ColumnDataSource(state_summary)

    p.scatter(
        x="income",
        y="births",
        source=source,
        size=12,
        color="#2878B5",
        alpha=0.75
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("State", "@state"),
                ("Income", "RM @income{0,0.00}"),
                ("Births", "@births{0,0}")
            ]
        )
    )

    show_chart(p)

    st.write(
        "Interpretation: This scatter plot examines the "
        "relationship between average median household income "
        "and total live births across selected states. "
        "The distribution helps identify possible positive "
        "or negative associations."
    )

    # Chart 2: Bar
    st.subheader(
        "2. Bar Chart: Median Household Income by State"
    )

    chart_data = state_summary.sort_values(
        "income", ascending=False
    )

    p = chart_style(
        "Average Median Household Income by State",
        "State",
        "Median Income (RM)"
    )

    p.vbar(
        x="state",
        top="income",
        width=0.65,
        source=ColumnDataSource(chart_data),
        color="#329D83"
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("State", "@state"),
                ("Income", "RM @income{0,0.00}")
            ]
        )
    )

    show_chart(p)

    st.write(
        "Interpretation: The bar chart compares average "
        "median household income among selected states "
        "during the chosen period."
    )

    # Chart 3: Heatmap
    st.subheader(
        "3. Correlation Heatmap: Income and Birth Indicators"
    )

    corr_data = bi[
        [
            "income_mean",
            "income_median",
            "birth_abs",
            "birth_rate"
        ]
    ].dropna()

    if len(corr_data) >= 2:

        show_chart(
            correlation_heatmap(
                corr_data,
                [
                    "income_mean",
                    "income_median",
                    "birth_abs",
                    "birth_rate"
                ],
                "Income and Birth Correlation"
            )
        )

        st.write(
            "Interpretation: The heatmap displays Pearson "
            "correlation coefficients between income and "
            "birth indicators. Values closer to 1 or -1 "
            "indicate stronger linear associations."
        )


# =====================================================
# PAGE 2
# FAMILY FORMATION AND POPULATION DYNAMICS
# =====================================================

elif page == "Family Formation and Population Dynamics":

    st.title(
        "Family Formation and Population Dynamics"
    )

    st.write(
        "Explore marriage patterns and live birth trends "
        "across Malaysian states."
    )

    st.subheader("🎯 Visualization Objective")

    st.write(
        "To analyze the relationship between marriage "
        "patterns and live births across Malaysian states "
        "over time, identifying demographic trends and "
        "regional differences."
    )

    if bm.empty:
        st.warning("No matching marriage and birth records.")
        st.stop()

    # Summary
    state_summary = (
        bm.groupby("state", as_index=False)
        .agg(
            births=("birth_abs", "sum"),
            marriages=("marriage_abs", "sum")
        )
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Live Births",
        f"{bm['birth_abs'].sum():,.0f}"
    )

    c2.metric(
        "Estimated Marriages",
        f"{bm['marriage_abs'].sum():,.0f}"
    )

    c3.metric(
        "Highest Marriage State",
        state_summary.loc[
            state_summary["marriages"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Highest Birth State",
        state_summary.loc[
            state_summary["births"].idxmax(), "state"
        ]
    )

    st.caption(
        "Marriage values are the average of female and male "
        "records, not their combined sum."
    )

    st.divider()

    # Chart 1: Time series
    st.subheader(
        "1. Time-Series Line Chart: Marriages vs Live Births"
    )

    yearly = (
        bm.groupby("year", as_index=False)
        .agg(
            births=("birth_abs", "sum"),
            marriages=("marriage_abs", "sum")
        )
    )

    p = chart_style(
        "Annual Marriage and Live Birth Trends",
        "Year",
        "Number of Records"
    )

    p.line(
        x="year",
        y="births",
        source=ColumnDataSource(yearly),
        color="#2878B5",
        line_width=3,
        legend_label="Live Births"
    )

    p.line(
        x="year",
        y="marriages",
        source=ColumnDataSource(yearly),
        color="#E07A3F",
        line_width=3,
        legend_label="Estimated Marriages"
    )

    p.legend.location = "top_left"

    p.add_tools(
        HoverTool(
            tooltips=[
                ("Year", "@year"),
                ("Births", "@births{0,0}"),
                ("Marriages", "@marriages{0,0}")
            ]
        )
    )

    show_chart(p)

    st.write(
        "Interpretation: The line chart tracks changes in "
        "marriages and live births over the selected years. "
        "It helps identify similar movements and differences "
        "in demographic trends."
    )

    # Chart 2: Heatmap
    st.subheader(
        "2. Correlation Heatmap: Marriage and Birth Indicators"
    )

    corr_data = bm[
        [
            "marriage_abs",
            "marriage_rate",
            "birth_abs",
            "birth_rate"
        ]
    ].dropna()

    if len(corr_data) >= 2:

        show_chart(
            correlation_heatmap(
                corr_data,
                [
                    "marriage_abs",
                    "marriage_rate",
                    "birth_abs",
                    "birth_rate"
                ],
                "Marriage and Birth Correlation"
            )
        )

        st.write(
            "Interpretation: The heatmap shows the strength "
            "and direction of linear associations between "
            "marriage and birth indicators."
        )

    # Chart 3: Grouped bar
    st.subheader(
        "3. Grouped Bar Chart: Marriages vs Live Births"
    )

    p = chart_style(
        "Marriage and Birth Comparison by State",
        "State",
        "Number of Records"
    )

    states = state_summary["state"].tolist()
    x = np.arange(len(states))
    width = 0.36

    p.vbar(
        x=dodge("state", -0.2, range=p.x_range),
        top="marriages",
        width=width,
        source=ColumnDataSource(state_summary),
        color="#E07A3F",
        legend_label="Estimated Marriages"
    )

    p.vbar(
        x=dodge("state", 0.2, range=p.x_range),
        top="births",
        width=width,
        source=ColumnDataSource(state_summary),
        color="#2878B5",
        legend_label="Live Births"
    )

    p.x_range.factors = states
    p.legend.location = "top_left"

    show_chart(p)

    st.write(
        "Interpretation: This grouped bar chart compares "
        "estimated marriage and live birth volumes across "
        "selected states during the chosen period."
    )


# =====================================================
# PAGE 3
# SOCIOECONOMIC INFLUENCE ON MARRIAGES
# =====================================================

elif page == "Socioeconomic Influence on Marriages":

    st.title(
        "Socioeconomic Influence on Marriages"
    )

    st.write(
        "Explore the relationship between household income "
        "and marriage patterns across Malaysian states."
    )

    st.subheader("🎯 Visualization Objective")

    st.write(
        "To investigate the relationship between household "
        "income levels and marriage patterns across Malaysian "
        "states, examining possible socioeconomic associations."
    )

    if mi.empty:
        st.warning("No matching marriage and income records.")
        st.stop()

    # Summary
    state_summary = (
        mi.groupby("state", as_index=False)
        .agg(
            income=("income_median", "mean"),
            marriages=("marriage_abs", "sum"),
            marriage_rate=("marriage_rate", "mean")
        )
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Household Income",
        f"RM {mi['income_mean'].mean():,.0f}"
    )

    c2.metric(
        "Estimated Marriages",
        f"{mi['marriage_abs'].sum():,.0f}"
    )

    c3.metric(
        "Highest Marriage State",
        state_summary.loc[
            state_summary["marriages"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Lowest Income State",
        state_summary.loc[
            state_summary["income"].idxmin(), "state"
        ]
    )

    st.divider()

    # Chart 1: Bubble chart
    st.subheader(
        "1. Bubble Chart: Household Income vs Marriages"
    )

    p = chart_style(
        "Income and Marriage Relationship",
        "Average Median Income (RM)",
        "Average Marriage Rate"
    )

    p.scatter(
        x="income",
        y="marriage_rate",
        size=20,
        source=ColumnDataSource(state_summary),
        color="#329D83",
        alpha=0.65
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("State", "@state"),
                ("Income", "RM @income{0,0.00}"),
                ("Marriage Rate", "@marriage_rate{0.00}"),
                ("Marriage Volume", "@marriages{0,0}")
            ]
        )
    )

    show_chart(p)

    st.write(
        "Interpretation: The bubble chart examines the "
        "relationship between household income and marriage "
        "rates. Each bubble represents a state, while the "
        "hover information displays estimated marriage volume."
    )

    # Chart 2: Box plot
    st.subheader(
        "2. Box Plot: Income Distribution by Marriage Volume"
    )

    box_data = state_summary.dropna(
        subset=["income", "marriages"]
    ).copy()

    if len(box_data) >= 3:

        box_data["Marriage Tier"] = pd.qcut(
            box_data["marriages"].rank(method="first"),
            q=3,
            labels=["Low", "Medium", "High"]
        )

        tiers = ["Low", "Medium", "High"]

        p = chart_style(
            "Income Distribution by Marriage Volume",
            "Marriage Volume Tier",
            "Median Household Income (RM)"
        )

        for tier in tiers:

            values = box_data.loc[
                box_data["Marriage Tier"] == tier,
                "income"
            ].dropna().values

            if len(values) == 0:
                continue

            q1, median, q3 = np.percentile(
                values, [25, 50, 75]
            )

            lower = values.min()
            upper = values.max()

            p.vbar(
                x=tier,
                width=0.5,
                bottom=q1,
                top=q3,
                fill_color="#329D83",
                line_color="black"
            )

            p.segment(
                x0=tier,
                y0=lower,
                x1=tier,
                y1=q1,
                line_color="black"
            )

            p.segment(
                x0=tier,
                y0=q3,
                x1=tier,
                y1=upper,
                line_color="black"
            )

            p.segment(
                x0=tier,
                y0=median,
                x1=tier,
                y1=median,
                line_color="black",
                line_width=3
            )

            p.scatter(
                x=[tier] * len(values),
                y=values,
                size=6,
                color="#2878B5",
                alpha=0.5
            )

        show_chart(p)

        st.write(
            "Interpretation: The box plot compares household "
            "income distributions among low, medium and high "
            "marriage-volume groups. It highlights the median, "
            "spread and differences in income across groups."
        )

    # Chart 3: Marriage rate
    st.subheader(
        "3. Bar Chart: Marriage Rate by State"
    )

    chart_data = state_summary.sort_values(
        "marriage_rate",
        ascending=False
    )

    p = chart_style(
        "Marriage Rate Distribution by State",
        "State",
        "Average Marriage Rate"
    )

    p.vbar(
        x="state",
        top="marriage_rate",
        width=0.65,
        source=ColumnDataSource(chart_data),
        color="#2878B5"
    )

    p.add_tools(
        HoverTool(
            tooltips=[
                ("State", "@state"),
                ("Marriage Rate", "@marriage_rate{0.00}")
            ]
        )
    )

    show_chart(p)

    st.write(
        "Interpretation: This bar chart compares average "
        "marriage rates among selected states during the "
        "selected period."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center">
        <b>Malaysia Socioeconomic & Demographic Dashboard</b>
        <br>
        Department of Statistics Malaysia (DOSM)
        <br>
        Scientific Visualization Project
    </div>
    """,
    unsafe_allow_html=True
)


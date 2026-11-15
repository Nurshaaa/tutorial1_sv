import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Malaysian Data Visualization",
    page_icon="📊",
    layout="wide"
)

st.title("Malaysian Demographic and Socioeconomic Dashboard")
st.caption("Data Source: Department of Statistics Malaysia (DOSM)")

BASE_DIR = Path(__file__).parent

BIRTH_FILE = BASE_DIR / "birth_state (1).csv"
MARRIAGE_FILE = BASE_DIR / "marriages_state.csv"
INCOME_FILE = BASE_DIR / "hh_income_state.csv"


# ==========================================
# DISTINCT CATEGORY COLOURS
# ==========================================
COLOR_PALETTE = [
    "#E6194B",  # Red
    "#4363D8",  # Blue
    "#FFE119",  # Yellow
    "#3CB44B",  # Green
    "#F58231",  # Orange
    "#911EB4",  # Purple
    "#42D4F4",  # Cyan
    "#F032E6",  # Magenta
    "#BFEF45",  # Lime
    "#FABED4",  # Pink
    "#469990",  # Teal
    "#9A6324",  # Brown
    "#800000",  # Maroon
    "#000075",  # Navy
    "#A9A9A9"   # Grey
]

INDICATOR_COLORS = {
    "Live Births": "#E6194B",
    "Marriages (Male/Female Average)": "#4363D8"
}

HEATMAP_COLORS = [
    [0.0, "#E6194B"],
    [0.33, "#FFE119"],
    [0.66, "#3CB44B"],
    [1.0, "#4363D8"]
]


# ==========================================
# LOAD AND PREPARE DATA
# ==========================================
@st.cache_data
def load_data():

    births = pd.read_csv(BIRTH_FILE)
    marriages = pd.read_csv(MARRIAGE_FILE)
    income = pd.read_csv(INCOME_FILE)

    def prepare_year(df):
        df = df.copy()

        if "year" not in df.columns:
            df["year"] = (
                df["date"]
                .astype(str)
                .str.extract(r"((?:19|20)\d{2})")[0]
            )

        df["year"] = pd.to_numeric(
            df["year"], errors="coerce"
        )

        df = df.dropna(subset=["year"])
        df["year"] = df["year"].astype(int)

        return df

    births = prepare_year(births)
    marriages = prepare_year(marriages)
    income = prepare_year(income)

    # Convert numeric columns
    for df, columns in [
        (births, ["abs", "rate"]),
        (marriages, ["abs", "rate"]),
        (income, ["income_mean", "income_median"])
    ]:
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(
                    df[col], errors="coerce"
                )

    # Birth data aggregation
    births = births.groupby(
        ["state", "year"], as_index=False
    ).agg(
        births_abs=("abs", "sum"),
        births_rate=("rate", "mean")
    )

    # Marriage data aggregation: average
    marriages = marriages.groupby(
        ["state", "year"], as_index=False
    ).agg(
        marriage_abs=("abs", "mean"),
        marriage_rate=("rate", "mean")
    )

    # Household income aggregation
    income = income.groupby(
        ["state", "year"], as_index=False
    ).agg(
        income_mean=("income_mean", "mean"),
        income_median=("income_median", "mean")
    )

    # Merge datasets
    data = births.merge(
        marriages,
        on=["state", "year"],
        how="outer"
    )

    data = data.merge(
        income,
        on=["state", "year"],
        how="outer"
    )

    return data


try:
    data = load_data()

except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.info(
        "Please ensure all three CSV files are in the same folder as main.py."
    )
    st.stop()


# ==========================================
# CREATE CONSISTENT STATE COLOUR MAPPING
# ==========================================
all_states = sorted(data["state"].dropna().unique())

STATE_COLORS = {
    state: COLOR_PALETTE[i % len(COLOR_PALETTE)]
    for i, state in enumerate(all_states)
}


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("Dashboard Menu")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Objective 1",
        "Objective 2",
        "Objective 3"
    ]
)


# ==========================================
# SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.subheader("Data Filters")

selected_states = st.sidebar.multiselect(
    "Select State",
    all_states,
    default=all_states
)

st.sidebar.subheader("Year Filter")

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=2017,
    max_value=2024,
    value=(2017, 2024),
    step=1
)

# Apply filters
filtered = data[
    (data["state"].isin(selected_states))
    & (data["year"].between(
        year_range[0],
        year_range[1]
    ))
    & (data["year"].between(2017, 2024))
].copy()

if not selected_states:
    st.warning("Please select at least one state.")
    st.stop()


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def show_metrics(df):

    col1, col2, col3, col4 = st.columns(4)

    births = df["births_abs"].sum()
    income = df["income_mean"].mean()
    marriages = df["marriage_abs"].sum()
    rate = df["births_rate"].mean()

    col1.metric(
        "Total Live Births",
        f"{births:,.0f}"
    )

    col2.metric(
        "Average Household Income",
        f"RM {income:,.2f}" if pd.notna(income) else "N/A"
    )

    col3.metric(
        "Marriage Volume",
        f"{marriages:,.0f}"
    )

    col4.metric(
        "Average Birth Rate",
        f"{rate:,.2f}" if pd.notna(rate) else "N/A"
    )


def show_heatmap(df, columns, title):

    corr = df[columns].dropna().corr()

    if corr.empty or corr.isna().all().all():
        st.info("Not enough data to calculate correlation.")
        return

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale=HEATMAP_COLORS,
        zmin=-1,
        zmax=1,
        title=title
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# HOME PAGE
# ==========================================
if page == "Home":

    st.header("Project Overview")

    st.write("""
    This dashboard explores the relationship between demographic
    and socioeconomic indicators across Malaysian states using
    data from the Department of Statistics Malaysia (DOSM).
    """)

    st.subheader("Research Objectives")

    st.markdown("""
    **Objective 1: Economic Prosperity vs. Demographic Growth**

    Examine the relationship between household income and live births.

    **Objective 2: Family Formation and Population Dynamics**

    Analyze marriage patterns and live births over time.

    **Objective 3: Socioeconomic Influence on Marriages**

    Investigate the relationship between household income and marriage patterns.
    """)

    st.subheader("Dataset Information")

    overview = pd.DataFrame({
        "Dataset": [
            "Birth State",
            "Marriages State",
            "Household Income State"
        ],
        "Filename": [
            "birth_state (1).csv",
            "marriages_state.csv",
            "hh_income_state.csv"
        ],
        "Main Indicators": [
            "Number of births and birth rate",
            "Number of marriages and marriage rate",
            "Mean and median household income"
        ]
    })

    st.dataframe(
        overview,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Dataset Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total States", data["state"].nunique())
    col2.metric("Selected Start Year", year_range[0])
    col3.metric("Selected End Year", year_range[1])


# ==========================================
# OBJECTIVE 1
# ==========================================
elif page == "Objective 1":

    st.header("Objective 1: Economic Prosperity vs. Demographic Growth")

    st.write("""
    **Objective:** To examine the relationship between household
    income and live births across Malaysian states.
    """)

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.markdown("---")

    # Visualization 1: Scatter Plot
    st.subheader("Visualization 1: Household Income vs. Live Births")

    df = filtered.dropna(
        subset=["income_median", "births_abs"]
    )

    if not df.empty:

        fig1 = px.scatter(
            df,
            x="income_median",
            y="births_abs",
            color="state",
            size="births_abs",
            hover_data=["year"],
            color_discrete_map=STATE_COLORS,
            title="Median Household Income vs. Live Births",
            labels={
                "income_median": "Median Household Income (RM)",
                "births_abs": "Number of Live Births",
                "state": "State"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("Insufficient data for scatter plot.")

    # Visualization 2: Bar Chart
    st.subheader("Visualization 2: Total Live Births by State")

    birth_state = filtered.groupby(
        "state", as_index=False
    )["births_abs"].sum().dropna()

    if not birth_state.empty:

        fig2 = px.bar(
            birth_state,
            x="state",
            y="births_abs",
            color="state",
            color_discrete_map=STATE_COLORS,
            title="Total Live Births by State",
            labels={
                "state": "State",
                "births_abs": "Total Live Births"
            }
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Insufficient data for bar chart.")

    # Visualization 3: Heatmap
    st.subheader("Visualization 3: Correlation Heatmap")

    show_heatmap(
        filtered,
        [
            "income_mean",
            "income_median",
            "births_abs",
            "births_rate"
        ],
        "Correlation Between Income and Birth Indicators"
    )

    st.subheader("Interpretation and Discussion")

    st.write("""
    The scatter plot compares household income with the number of
    live births across Malaysian states. The bar chart identifies
    states with higher and lower birth totals.

    The correlation heatmap summarizes the relationship between
    household income and birth indicators. These visualizations
    help identify demographic and socioeconomic patterns.
    Correlation does not necessarily imply causation.
    """)


# ==========================================
# OBJECTIVE 2
# ==========================================
elif page == "Objective 2":

    st.header("Objective 2: Family Formation and Population Dynamics")

    st.write("""
    **Objective:** To analyze the relationship between marriage
    patterns and live births across Malaysian states over time.
    """)

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.markdown("---")

    yearly = filtered.groupby(
        "year", as_index=False
    ).agg(
        births=("births_abs", "sum"),
        marriages=("marriage_abs", "sum")
    )

    yearly_long = yearly.melt(
        id_vars="year",
        var_name="Indicator",
        value_name="Value"
    )

    yearly_long["Indicator"] = yearly_long[
        "Indicator"
    ].replace({
        "births": "Live Births",
        "marriages": "Marriages (Male/Female Average)"
    })

    # Visualization 1: Line Chart
    st.subheader("Visualization 1: Marriage and Birth Trends")

    if not yearly_long.empty:

        fig1 = px.line(
            yearly_long,
            x="year",
            y="Value",
            color="Indicator",
            markers=True,
            color_discrete_map=INDICATOR_COLORS,
            title="Marriage and Live Birth Trends Over Time",
            labels={
                "year": "Year",
                "Value": "Recorded Value"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("Insufficient data for line chart.")

    # Visualization 2: Heatmap
    st.subheader("Visualization 2: Correlation Heatmap")

    show_heatmap(
        filtered,
        [
            "marriage_abs",
            "marriage_rate",
            "births_abs",
            "births_rate"
        ],
        "Correlation Between Marriage and Birth Indicators"
    )

    # Visualization 3: Grouped Bar Chart
    st.subheader("Visualization 3: Yearly Comparison")

    if not yearly_long.empty:

        fig3 = px.bar(
            yearly_long,
            x="year",
            y="Value",
            color="Indicator",
            barmode="group",
            color_discrete_map=INDICATOR_COLORS,
            title="Marriage and Live Birth Comparison by Year",
            labels={
                "year": "Year",
                "Value": "Recorded Value"
            }
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Insufficient data for grouped bar chart.")

    st.subheader("Interpretation and Discussion")

    st.write("""
    The line chart displays changes in marriage and live birth
    values over time. The heatmap summarizes correlations between
    marriage and birth indicators.

    The grouped bar chart compares their yearly values.
    Marriage values represent the average of male and female
    records for each state and year. These visualizations help
    identify patterns in family formation and population dynamics.
    """)


# ==========================================
# OBJECTIVE 3
# ==========================================
elif page == "Objective 3":

    st.header("Objective 3: Socioeconomic Influence on Marriages")

    st.write("""
    **Objective:** To investigate the relationship between
    household income levels and marriage patterns across
    Malaysian states.
    """)

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.markdown("---")

    # Visualization 1: Bubble Chart
    st.subheader("Visualization 1: Household Income vs. Marriage Patterns")

    df = filtered.dropna(
        subset=["income_mean", "marriage_abs"]
    )

    if not df.empty:

        fig1 = px.scatter(
            df,
            x="income_mean",
            y="marriage_abs",
            size="marriage_abs",
            color="state",
            hover_data=["year"],
            color_discrete_map=STATE_COLORS,
            title="Mean Household Income vs. Marriage Volume",
            labels={
                "income_mean": "Mean Household Income (RM)",
                "marriage_abs": "Marriage Volume (Male/Female Average)",
                "state": "State"
            }
        )

        st.plotly_chart(fig1, use_container_width=True)

    else:
        st.info("Insufficient data for bubble chart.")

    # Visualization 2: Box Plot
    st.subheader("Visualization 2: Household Income Distribution")

    box_data = filtered.dropna(
        subset=["income_mean"]
    )

    if not box_data.empty:

        fig2 = px.box(
            box_data,
            x="state",
            y="income_mean",
            color="state",
            points="outliers",
            color_discrete_map=STATE_COLORS,
            title="Household Income Distribution by State",
            labels={
                "state": "State",
                "income_mean": "Mean Household Income (RM)"
            }
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("Insufficient data for box plot.")

    # Visualization 3: Bar Chart
    st.subheader("Visualization 3: Marriage Rate by State")

    marriage_state = filtered.groupby(
        "state", as_index=False
    )["marriage_rate"].mean().dropna()

    if not marriage_state.empty:

        fig3 = px.bar(
            marriage_state,
            x="state",
            y="marriage_rate",
            color="state",
            color_discrete_map=STATE_COLORS,
            title="Average Marriage Rate by State",
            labels={
                "state": "State",
                "marriage_rate": "Average Marriage Rate"
            }
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("Insufficient data for marriage rate chart.")

    st.subheader("Interpretation and Discussion")

    st.write("""
    The bubble chart compares household income with marriage
    volume across states. The box plot shows the distribution
    of household income, while the bar chart compares average
    marriage rates between states.

    These visualizations help identify socioeconomic patterns
    related to marriage across Malaysian states. They do not
    establish a cause-and-effect relationship.
    """)


# ==========================================
# FOOTER
# ==========================================
st.markdown("---")

st.caption(
    "Scientific Visualization Project | "
    "Department of Statistics Malaysia (DOSM) / OpenDOSM"
)



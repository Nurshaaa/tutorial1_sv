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
st.caption("Data source: Department of Statistics Malaysia (DOSM)")

BASE_DIR = Path(__file__).parent

# Original dataset filenames
BIRTH_FILE = BASE_DIR / "birth_state (1).csv"
MARRIAGE_FILE = BASE_DIR / "marriages_state.csv"
INCOME_FILE = BASE_DIR / "hh_income_state.csv"


# ==========================================
# LOAD DATA
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
                df["date"].astype(str)
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

    # Convert numerical columns
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

    # Birth aggregation
    births = births.groupby(
        ["state", "year"], as_index=False
    ).agg(
        births_abs=("abs", "sum"),
        births_rate=("rate", "mean")
    )

    # Marriage aggregation: average male and female
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
# SIDEBAR FILTERS
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

st.sidebar.markdown("---")
st.sidebar.subheader("Data Filters")

states = sorted(data["state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State",
    states,
    default=states
)

years = sorted(data["year"].dropna().unique())

if len(years) > 1:
    year_range = st.sidebar.slider(
        "Select Year Range",
        int(min(years)),
        int(max(years)),
        (int(min(years)), int(max(years)))
    )
else:
    year_range = (int(years[0]), int(years[0]))

filtered = data[
    (data["state"].isin(selected_states))
    & (data["year"].between(*year_range))
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

    col1.metric("Total Live Births", f"{births:,.0f}")
    col2.metric(
        "Average Household Income",
        f"RM {income:,.2f}" if pd.notna(income) else "N/A"
    )
    col3.metric("Marriage Volume", f"{marriages:,.0f}")
    col4.metric(
        "Average Birth Rate",
        f"{rate:,.2f}" if pd.notna(rate) else "N/A"
    )


def show_heatmap(df, columns, title):

    corr = df[columns].corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=title
    )

    st.plotly_chart(fig, use_container_width=True)


# ==========================================
# HOME PAGE
# ==========================================
if page == "Home":

    st.header("Project Overview")

    st.write("""
    This dashboard explores the relationship between demographic
    and socioeconomic indicators across Malaysian states.

    Three datasets are used:
    - Annual Live Births by State
    - Annual Marriages by State
    - Household Income by State
    """)

    st.subheader("Research Objectives")

    st.markdown("""
    **Objective 1:** Economic Prosperity vs. Demographic Growth

    Examine the relationship between household income and live births.

    **Objective 2:** Family Formation and Population Dynamics

    Analyze marriage patterns and live births over time.

    **Objective 3:** Socioeconomic Influence on Marriages

    Investigate the relationship between household income and marriage patterns.
    """)

    st.subheader("Dataset Information")

    st.dataframe(
        pd.DataFrame({
            "Dataset": [
                "Birth State",
                "Marriages State",
                "Household Income State"
            ],
            "Filename": [
                "birth_state (1).csv",
                "marriages_state.csv",
                "hh_income_state.csv"
            ]
        }),
        use_container_width=True,
        hide_index=True
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Total States", data["state"].nunique())
    c2.metric("First Year", int(data["year"].min()))
    c3.metric("Last Year", int(data["year"].max()))


# ==========================================
# OBJECTIVE 1
# ==========================================
elif page == "Objective 1":

    st.header("Objective 1: Economic Prosperity vs. Demographic Growth")

    st.write(
        "To examine the relationship between household income "
        "and live births across Malaysian states."
    )

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.subheader("Visualization 1: Income vs. Live Births")

    df = filtered.dropna(
        subset=["income_median", "births_abs"]
    )

    fig1 = px.scatter(
        df,
        x="income_median",
        y="births_abs",
        color="state",
        size="births_abs",
        hover_data=["year"],
        title="Median Household Income vs. Live Births",
        labels={
            "income_median": "Median Household Income (RM)",
            "births_abs": "Number of Live Births"
        }
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Visualization 2: Births by State")

    birth_state = filtered.groupby(
        "state", as_index=False
    )["births_abs"].sum()

    fig2 = px.bar(
        birth_state,
        x="state",
        y="births_abs",
        color="births_abs",
        title="Total Live Births by State"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Visualization 3: Correlation Heatmap")

    show_heatmap(
        filtered,
        ["income_mean", "income_median", "births_abs", "births_rate"],
        "Income and Birth Indicators Correlation"
    )

    st.subheader("Interpretation")

    st.write("""
    The scatter plot compares household income and live births.
    The bar chart identifies states with higher and lower birth totals.
    The heatmap summarizes the correlation between income and birth indicators.
    Correlation does not necessarily imply causation.
    """)


# ==========================================
# OBJECTIVE 2
# ==========================================
elif page == "Objective 2":

    st.header("Objective 2: Family Formation and Population Dynamics")

    st.write(
        "To analyze the relationship between marriage patterns "
        "and live births across Malaysian states over time."
    )

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.subheader("Visualization 1: Trends Over Time")

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

    fig1 = px.line(
        yearly_long,
        x="year",
        y="Value",
        color="Indicator",
        markers=True,
        title="Marriage and Live Birth Trends"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Visualization 2: Correlation Heatmap")

    show_heatmap(
        filtered,
        ["marriage_abs", "marriage_rate", "births_abs", "births_rate"],
        "Marriage and Birth Indicators Correlation"
    )

    st.subheader("Visualization 3: Yearly Comparison")

    fig3 = px.bar(
        yearly_long,
        x="year",
        y="Value",
        color="Indicator",
        barmode="group",
        title="Marriage and Live Birth Comparison"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Interpretation")

    st.write("""
    The line chart shows changes in marriage and birth values over time.
    The heatmap summarizes relationships between marriage and birth indicators.
    The grouped bar chart compares their yearly values.
    Marriage figures represent the average of male and female records.
    """)


# ==========================================
# OBJECTIVE 3
# ==========================================
elif page == "Objective 3":

    st.header("Objective 3: Socioeconomic Influence on Marriages")

    st.write(
        "To investigate the relationship between household income "
        "and marriage patterns across Malaysian states."
    )

    if filtered.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    show_metrics(filtered)

    st.subheader("Visualization 1: Income vs. Marriages")

    df = filtered.dropna(
        subset=["income_mean", "marriage_abs"]
    )

    fig1 = px.scatter(
        df,
        x="income_mean",
        y="marriage_abs",
        size="marriage_abs",
        color="state",
        hover_data=["year"],
        title="Mean Household Income vs. Marriage Volume",
        labels={
            "income_mean": "Mean Household Income (RM)",
            "marriage_abs": "Marriage Volume (Male/Female Average)"
        }
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Visualization 2: Income Distribution")

    fig2 = px.box(
        filtered.dropna(subset=["income_mean"]),
        x="state",
        y="income_mean",
        color="state",
        title="Household Income Distribution by State"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Visualization 3: Marriage Rate by State")

    marriage_state = filtered.groupby(
        "state", as_index=False
    )["marriage_rate"].mean()

    fig3 = px.bar(
        marriage_state,
        x="state",
        y="marriage_rate",
        color="marriage_rate",
        title="Average Marriage Rate by State"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Interpretation")

    st.write("""
    The bubble chart compares household income with marriage volume.
    The box plot shows the distribution of household income across states.
    The bar chart compares average marriage rates between states.
    These patterns do not establish a cause-and-effect relationship.
    """)


# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("Scientific Visualization Project | DOSM / OpenDOSM")



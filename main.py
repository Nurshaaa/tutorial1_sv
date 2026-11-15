from streamlit_bokeh import streamlit_bokeh
import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    ColorBar,
    LinearColorMapper,
    FactorRange
)
from bokeh.palettes import RdBu11
from bokeh.transform import dodge


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Malaysia Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

# Original dataset filenames - DO NOT CHANGE
BIRTH_FILE = BASE_DIR / "birth_state (1).csv"
MARRIAGE_FILE = BASE_DIR / "marriages_state.csv"
INCOME_FILE = BASE_DIR / "hh_income_state.csv"


# =====================================================
# 2. LOAD DATASETS
# =====================================================

@st.cache_data
def load_data():

    births = pd.read_csv(BIRTH_FILE)
    marriages = pd.read_csv(MARRIAGE_FILE)
    income = pd.read_csv(INCOME_FILE)

    # Check required columns
    required_birth = {"state", "date", "abs", "rate"}
    required_marriage = {"state", "date", "sex", "abs", "rate"}
    required_income = {
        "state", "date", "income_mean", "income_median"
    }

    if not required_birth.issubset(births.columns):
        raise ValueError("Birth dataset is missing required columns.")

    if not required_marriage.issubset(marriages.columns):
        raise ValueError("Marriage dataset is missing required columns.")

    if not required_income.issubset(income.columns):
        raise ValueError("Income dataset is missing required columns.")

    # Convert date and year
    for df in [births, marriages, income]:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year

    # -------------------------------------------------
    # BIRTH DATA
    # -------------------------------------------------

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

    births = births.dropna(
        subset=["state", "year"]
    )

    # -------------------------------------------------
    # MARRIAGE DATA
    # -------------------------------------------------

    marriages["sex"] = (
        marriages["sex"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    marriages["abs"] = pd.to_numeric(
        marriages["abs"], errors="coerce"
    )

    marriages["rate"] = pd.to_numeric(
        marriages["rate"], errors="coerce"
    )

    marriages = marriages.dropna(
        subset=["state", "year"]
    )

    # User selected average for marriage dataset.
    # Average male and female records for each state/year.
    marriages = (
        marriages
        .groupby(["state", "year"], as_index=False)
        .agg(
            marriage_abs=("abs", "mean"),
            marriage_rate=("rate", "mean")
        )
    )

    # -------------------------------------------------
    # HOUSEHOLD INCOME DATA
    # -------------------------------------------------

    income["income_mean"] = pd.to_numeric(
        income["income_mean"], errors="coerce"
    )

    income["income_median"] = pd.to_numeric(
        income["income_median"], errors="coerce"
    )

    income = income.dropna(
        subset=["state", "year"]
    )

    # Select required columns
    births = births[
        ["state", "year", "birth_abs", "birth_rate"]
    ]

    marriages = marriages[
        ["state", "year", "marriage_abs", "marriage_rate"]
    ]

    income = income[
        ["state", "year", "income_mean", "income_median"]
    ]

    return births, marriages, income


# =====================================================
# 3. LOAD DATA WITH ERROR HANDLING
# =====================================================

try:

    births, marriages, income = load_data()

except Exception as e:

    st.error(f"Dataset loading error: {e}")

    st.info(
        "Please ensure that all three CSV files are "
        "uploaded in the same folder as main.py."
    )

    st.stop()


# =====================================================
# 4. MERGE DATASETS
# =====================================================

birth_income = pd.merge(
    births,
    income,
    on=["state", "year"],
    how="inner"
)

birth_marriage = pd.merge(
    births,
    marriages,
    on=["state", "year"],
    how="inner"
)

marriage_income = pd.merge(
    marriages,
    income,
    on=["state", "year"],
    how="inner"
)


# =====================================================
# 5. SIDEBAR NAVIGATION
# =====================================================

st.sidebar.title("📊 Malaysia Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Economic Prosperity vs. Demographic Growth",
        "Family Formation and Population Dynamics",
        "Socioeconomic Influence on Marriages"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("🔎 Dashboard Filters")

all_states = sorted(
    set(births["state"].dropna().unique())
    | set(marriages["state"].dropna().unique())
    | set(income["state"].dropna().unique())
)

selected_states = st.sidebar.multiselect(
    "Select State",
    options=all_states,
    default=all_states
)

# Filter year range based on available analytical data
available_years = sorted(
    set(birth_income["year"].dropna().astype(int))
    | set(birth_marriage["year"].dropna().astype(int))
    | set(marriage_income["year"].dropna().astype(int))
)

if not available_years:
    st.error("No matching years found in the datasets.")
    st.stop()

min_year = min(available_years)
max_year = max(available_years)

if min_year == max_year:
    selected_years = (min_year, max_year)
    st.sidebar.write(f"Year: {min_year}")
else:
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

st.sidebar.divider()

st.sidebar.caption(
    "Data Source: Department of Statistics Malaysia (DOSM)"
)


# =====================================================
# 6. FILTER FUNCTION
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


# =====================================================
# 7. HELPER FUNCTIONS
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

    def show_chart(p):
    streamlit_bokeh(
        p,
        use_container_width=True
    )


def show_correlation_heatmap(data, columns, title):

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
        toolbar_location="above"
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
        text_baseline="middle",
        text_color="black"
    )

    p.add_layout(
        ColorBar(color_mapper=mapper),
        "right"
    )

    p.xaxis.major_label_orientation = 0.8

    return p


def empty_data_message(data):

    if data.empty:

        st.warning(
            "No data available for the selected filters. "
            "Please select another state or year range."
        )

        st.stop()


# =====================================================
# 8. HOME PAGE
# =====================================================

if page == "Home":

    st.title(
        "Malaysia Socioeconomic & Demographic Dashboard"
    )

    st.markdown(
        """
        ### Interactive Scientific Visualization

        This dashboard explores the relationship between
        household income, marriage patterns and live births
        across Malaysian states.
        """
    )

    st.divider()

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Live Birth Records",
        f"{len(births):,}"
    )

    col2.metric(
        "Marriage Records",
        f"{len(marriages):,}"
    )

    col3.metric(
        "Household Income Records",
        f"{len(income):,}"
    )

    st.divider()

    st.subheader("Visualization Objectives")

    st.markdown(
        """
        **Objective 1: Economic Prosperity vs. Demographic Growth**

        To examine the relationship between household income
        and live births across Malaysian states, identifying
        possible socioeconomic patterns in demographic growth.

        ---

        **Objective 2: Family Formation and Population Dynamics**

        To analyze the relationship between marriage patterns
        and live births across Malaysian states over time,
        identifying demographic trends and regional differences.

        ---

        **Objective 3: Socioeconomic Influence on Marriages**

        To investigate the relationship between household
        income levels and marriage patterns across Malaysian
        states, examining possible socioeconomic associations.
        """
    )

    st.info(
        "Use the sidebar navigation to explore the three "
        "visualization pages. You can filter the dashboard "
        "by state and year."
    )


# =====================================================
# PAGE 1
# ECONOMIC PROSPERITY VS DEMOGRAPHIC GROWTH
# =====================================================

elif page == "Economic Prosperity vs. Demographic Growth":

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

    empty_data_message(bi)

    # -----------------------------------------------
    # SUMMARY BOXES
    # -----------------------------------------------

    summary = (
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
        summary.loc[
            summary["income"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Highest Birth State",
        summary.loc[
            summary["births"].idxmax(), "state"
        ]
    )

    st.caption(
        "Income is the unweighted average of available "
        "state-year median income records."
    )

    st.divider()

    # -----------------------------------------------
    # VISUALIZATION 1: SCATTER PLOT
    # -----------------------------------------------

    st.subheader(
        "1. Scatter Plot: Household Income vs. Live Births"
    )

    scatter_data = summary.dropna(
        subset=["income", "births"]
    )

    p = chart_style(
        "Household Income and Live Births",
        "Average Median Household Income (RM)",
        "Total Live Births"
    )

    source = ColumnDataSource(scatter_data)

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

    st.markdown(
        """
        **Interpretation:**

        The scatter plot examines the relationship between
        average median household income and total live births
        across selected states. The position of each point
        helps identify possible positive or negative
        associations between economic conditions and
        demographic distribution.
        """
    )

    # -----------------------------------------------
    # VISUALIZATION 2: BAR CHART
    # -----------------------------------------------

    st.subheader(
        "2. Bar Chart: Household Income by State"
    )

    chart_data = summary.dropna(
        subset=["income"]
    ).sort_values(
        "income", ascending=False
    )

    p = chart_style(
        "Average Median Household Income by State",
        "State",
        "Median Household Income (RM)"
    )

    p.x_range = FactorRange(
        *chart_data["state"].tolist()
    )

    source = ColumnDataSource(chart_data)

    p.vbar(
        x="state",
        top="income",
        width=0.65,
        source=source,
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

    st.markdown(
        """
        **Interpretation:**

        The bar chart compares average median household
        income among Malaysian states. Differences in bar
        heights highlight regional economic disparities
        and identify states with relatively higher or
        lower household income.
        """
    )

    # -----------------------------------------------
    # VISUALIZATION 3: CORRELATION HEATMAP
    # -----------------------------------------------

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
            show_correlation_heatmap(
                corr_data,
                [
                    "income_mean",
                    "income_median",
                    "birth_abs",
                    "birth_rate"
                ],
                "Income and Birth Correlation Matrix"
            )
        )

        st.markdown(
            """
            **Interpretation:**

            The heatmap displays Pearson correlation
            coefficients between household income and
            birth indicators. Positive values represent
            positive linear associations, while negative
            values indicate inverse associations.
            """
        )

    else:

        st.warning(
            "Insufficient complete records for correlation analysis."
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

    st.caption(
        f"Selected period: {selected_years[0]}–{selected_years[1]}"
    )

    empty_data_message(bm)

    # -----------------------------------------------
    # SUMMARY BOXES
    # -----------------------------------------------

    summary = (
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
        summary.loc[
            summary["marriages"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Highest Birth State",
        summary.loc[
            summary["births"].idxmax(), "state"
        ]
    )

    st.caption(
        "Marriage values are averages of female and male "
        "records for each state and year. They are not "
        "the sum of both records."
    )

    st.divider()

    # -----------------------------------------------
    # VISUALIZATION 1: LINE CHART
    # -----------------------------------------------

    st.subheader(
        "1. Time-Series Line Chart: Marriages vs. Live Births"
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

    p.scatter(
        x="year",
        y="births",
        source=ColumnDataSource(yearly),
        color="#2878B5",
        size=7
    )

    p.line(
        x="year",
        y="marriages",
        source=ColumnDataSource(yearly),
        color="#E07A3F",
        line_width=3,
        legend_label="Estimated Marriages"
    )

    p.scatter(
        x="year",
        y="marriages",
        source=ColumnDataSource(yearly),
        color="#E07A3F",
        size=7
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

    st.markdown(
        """
        **Interpretation:**

        The line chart tracks annual changes in estimated
        marriages and live births. It helps identify
        increasing or decreasing trends and compare
        demographic patterns over the selected period.
        """
    )

    # -----------------------------------------------
    # VISUALIZATION 2: CORRELATION HEATMAP
    # -----------------------------------------------

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
            show_correlation_heatmap(
                corr_data,
                [
                    "marriage_abs",
                    "marriage_rate",
                    "birth_abs",
                    "birth_rate"
                ],
                "Marriage and Birth Correlation Matrix"
            )
        )

        st.markdown(
            """
            **Interpretation:**

            The heatmap illustrates the strength and
            direction of linear associations between
            marriage and birth indicators. Stronger
            positive or negative values indicate
            stronger linear relationships.
            """
        )

    else:

        st.warning(
            "Insufficient complete records for correlation analysis."
        )

    # -----------------------------------------------
    # VISUALIZATION 3: GROUPED BAR CHART
    # -----------------------------------------------

    st.subheader(
        "3. Grouped Bar Chart: Marriages vs. Live Births"
    )

    chart_data = summary.dropna(
        subset=["births", "marriages"]
    )

    states = chart_data["state"].tolist()

    p = chart_style(
        "Marriage and Live Birth Comparison by State",
        "State",
        "Number of Records"
    )

    p.x_range = FactorRange(*states)

    source = ColumnDataSource(chart_data)

    p.vbar(
        x=dodge("state", -0.2, range=p.x_range),
        top="marriages",
        width=0.36,
        source=source,
        color="#E07A3F",
        legend_label="Estimated Marriages"
    )

    p.vbar(
        x=dodge("state", 0.2, range=p.x_range),
        top="births",
        width=0.36,
        source=source,
        color="#2878B5",
        legend_label="Live Births"
    )

    p.legend.location = "top_left"

    p.add_tools(
        HoverTool(
            tooltips=[
                ("State", "@state"),
                ("Marriages", "@marriages{0,0}"),
                ("Births", "@births{0,0}")
            ]
        )
    )

    show_chart(p)

    st.markdown(
        """
        **Interpretation:**

        The grouped bar chart compares estimated marriage
        and live birth volumes across selected states.
        It highlights regional differences in family
        formation and demographic activity.
        """
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

    st.caption(
        f"Selected period: {selected_years[0]}–{selected_years[1]}"
    )

    empty_data_message(mi)

    # -----------------------------------------------
    # SUMMARY BOXES
    # -----------------------------------------------

    summary = (
        mi.groupby("state", as_index=False)
        .agg(
            income=("income_median", "mean"),
            mean_income=("income_mean", "mean"),
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
        summary.loc[
            summary["marriages"].idxmax(), "state"
        ]
    )

    c4.metric(
        "Lowest Income State",
        summary.loc[
            summary["income"].idxmin(), "state"
        ]
    )

    st.divider()

    # -----------------------------------------------
    # VISUALIZATION 1: BUBBLE CHART
    # -----------------------------------------------

    st.subheader(
        "1. Bubble Chart: Household Income vs. Marriages"
    )

    bubble_data = summary.dropna(
        subset=["income", "marriage_rate", "marriages"]
    ).copy()

    if not bubble_data.empty:

        max_marriages = bubble_data["marriages"].max()

        if max_marriages > 0:

            bubble_data["bubble_size"] = (
                10 + 30 * bubble_data["marriages"]
                / max_marriages
            )

        else:

            bubble_data["bubble_size"] = 10

        p = chart_style(
            "Household Income and Marriage Patterns",
            "Average Median Household Income (RM)",
            "Average Marriage Rate"
        )

        source = ColumnDataSource(bubble_data)

        p.scatter(
            x="income",
            y="marriage_rate",
            size="bubble_size",
            source=source,
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

    st.markdown(
        """
        **Interpretation:**

        The bubble chart examines the relationship between
        household income and marriage rates across states.
        Bubble size represents estimated marriage volume,
        allowing comparison of income, marriage rates
        and marriage volume simultaneously.
        """
    )

    # -----------------------------------------------
    # VISUALIZATION 2: BOX PLOT
    # -----------------------------------------------

    st.subheader(
        "2. Box Plot: Income Distribution by Marriage Volume"
    )

    box_data = summary.dropna(
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

        p.x_range = FactorRange(*tiers)

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

            # Interquartile range
            p.vbar(
                x=tier,
                width=0.5,
                bottom=q1,
                top=q3,
                fill_color="#329D83",
                line_color="black"
            )

            # Lower and upper whiskers
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

            # Median line
            p.segment(
                x0=dodge("tier", -0.25, range=p.x_range),
                y0="median",
                x1=dodge("tier", 0.25, range=p.x_range),
                y1="median",
                source=ColumnDataSource({
                    "tier": [tier],
                    "median": [median]
                }),
                line_color="black",
                line_width=3
            )

            # Individual income points
            p.scatter(
                x=[tier] * len(values),
                y=values,
                size=7,
                color="#2878B5",
                alpha=0.6
            )

        show_chart(p)

        st.markdown(
            """
            **Interpretation:**

            The box plot compares median household income
            distributions among states grouped into low,
            medium and high marriage-volume tiers. It
            highlights differences in median income,
            variation and possible extreme observations.
            """
        )

    else:

        st.warning(
            "At least three states are needed for the box plot."
        )

    # -----------------------------------------------
    # VISUALIZATION 3: BAR CHART
    # -----------------------------------------------

    st.subheader(
        "3. Bar Chart: Marriage Rate by State"
    )

    chart_data = summary.dropna(
        subset=["marriage_rate"]
    ).sort_values(
        "marriage_rate",
        ascending=False
    )

    p = chart_style(
        "Average Marriage Rate by State",
        "State",
        "Average Marriage Rate"
    )

    p.x_range = FactorRange(
        *chart_data["state"].tolist()
    )

    source = ColumnDataSource(chart_data)

    p.vbar(
        x="state",
        top="marriage_rate",
        width=0.65,
        source=source,
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

    st.markdown(
        """
        **Interpretation:**

        The bar chart compares average marriage rates
        across Malaysian states. It identifies states
        with relatively higher and lower marriage rates
        during the selected period.
        """
    )


# =====================================================
# 9. FOOTER
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


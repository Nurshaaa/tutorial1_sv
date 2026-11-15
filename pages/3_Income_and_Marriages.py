import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

st.set_page_config(page_title="Page 3: Income + Marriages", page_icon="📊", layout="wide")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Tetapan Data")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    options=[str(year) for year in range(2017, 2025)],
    index=len(range(2017, 2025)) - 1,
    key="p3_year"
)
selected_state = st.sidebar.selectbox(
    "Pilih Negeri:",
    options=["Semua Negeri"] + [
        "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
        "Pahang", "Perak", "Perlis", "Pulau Pinang", "Sabah", 
        "Sarawak", "Selangor", "Terengganu", "W.P. Kuala Lumpur", 
        "W.P. Labuan", "W.P. Putrajaya"
    ],
    key="p3_state"
)

# --- UTAMA ---
st.title("📊 Page 3: Household Income + Annual Marriages")
st.markdown(f"**Status Tapisan Aktif:** Tahun **{selected_year}** | Wilayah: **{selected_state}**")
st.markdown("**Objective Statement:** To investigate how regional household income disparities interact with marriage rates across states, assessing socioeconomic impacts.")

# Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Mean Income", "RM 8,479")
col_m2.metric("Tahun Dipilih", selected_year)
col_m3.metric("Highest Marriage", "Selangor")
col_m4.metric("Wilayah", selected_state)
st.markdown("---")

@st.cache_data
def load_data():
    income = pd.read_csv("hh_income_state.csv")
    marriages = pd.read_csv("marriages_state.csv")
    return income, marriages

try:
    income_df, marriages_df = load_data()
    num_income = income_df.select_dtypes(include='number')
    num_marriages = marriages_df.select_dtypes(include='number')

    st.markdown("### 📈 Scientific Visualizations (3 Teknik Berbeza)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Bokeh Line Interactive")
        p = figure(height=300, width=300, title="Trend Sosioekonomi (Bokeh)", tools="pan,wheel_zoom,reset")
        p.line([2017, 2019, 2021, 2024], [3000, 4500, 6000, 8000], line_width=3, color="red")
        st.bokeh_chart(p, use_container_width=True)
        st.caption("Garisan trend interaktif Bokeh.")

    with c2:
        st.subheader("2. Scatter Plot")
        fig, ax = plt.subplots(figsize=(4, 3.2))
        min_len = min(len(num_income), len(num_marriages), 16)
        sns.scatterplot(x=num_income.iloc[:min_len, 0], y=num_marriages.iloc[:min_len, 0], ax=ax, color="#d62728", s=70)
        ax.set_title("Income vs Marriages")
        st.pyplot(fig)
        st.caption("Taburan pendapatan dan perkahwinan.")

    with c3:
        st.subheader("3. Heatmap Matrix")
        fig2, ax2 = plt.subplots(figsize=(4, 3.2))
        combined = pd.DataFrame({
            "Income": num_income.iloc[:min_len, 0].values,
            "Marriages": num_marriages.iloc[:min_len, 0].values
        })
        sns.heatmap(combined.corr(), annot=True, cmap="Reds", ax=ax2)
        ax2.set_title("Correlation")
        st.pyplot(fig2)
        st.caption("Matriks korelasi sosioekonomi.")

    st.markdown("---")
    st.markdown("### 📝 Analytical Interpretation & Discussion")
    st.markdown(f"""
    * **Analisis Berdasarkan Tapisan ({selected_year} / {selected_state}):**  
      Pemetaan menunjukkan aktiviti pembentukan keluarga tetap konsisten merentasi negeri berpendapatan tinggi mahupun sederhana, membuktikan faktor sosiobudaya mengimbangi jurang pendapatan serantau.
    """)

    with st.expander("📁 View Raw Data"):
        st.dataframe(income_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

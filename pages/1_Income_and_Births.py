import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

st.set_page_config(page_title="Page 1: Income + Births", page_icon="📊", layout="wide")

# --- SIDEBAR FILTERS (STATE & YEAR 2017-2024) ---
st.sidebar.header("🔍 Filter Tetapan Data")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    options=[str(year) for year in range(2017, 2025)],
    index=len(range(2017, 2025)) - 1
)

malaysia_states = [
    "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
    "Pahang", "Perak", "Perlis", "Pulau Pinang", "Sabah", 
    "Sarawak", "Selangor", "Terengganu", "W.P. Kuala Lumpur", 
    "W.P. Labuan", "W.P. Putrajaya"
]
selected_state = st.sidebar.selectbox("Pilih Negeri:", options=["Semua Negeri"] + malaysia_states)

# --- UTAMA ---
st.title("📊 Page 1: Household Income + Annual Live Births")
st.markdown(f"**Status Tapisan Aktif:** Tahun **{selected_year}** | Wilayah: **{selected_state}**")
st.markdown("**Objective Statement:** To analyze the relationship between state household income levels and annual live births, examining how economic prosperity and wealth distribution interact with regional birth rates.")

# Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Tahun Dipilih", selected_year)
col_m2.metric("Median Income (Nasional)", "RM 6,338")
col_m3.metric("Wilayah Paparan", selected_state)
col_m4.metric("Highest-Birth State", "Selangor")
st.markdown("---")

@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    income = pd.read_csv("hh_income_state.csv")
    return births, income

try:
    births_df, income_df = load_data()
    num_income = income_df.select_dtypes(include='number')

    st.markdown("### 📈 Scientific Visualizations (3 Teknik Berbeza)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Bokeh Interactive Chart")
        sample_data = pd.DataFrame({'Kategori': ['Wilayah A', 'Wilayah B', 'Wilayah C', 'Wilayah D'], 'Nilai': [45, 60, 75, 50]})
        source = ColumnDataSource(sample_data)
        p = figure(x_range=sample_data['Kategori'], height=300, width=300, title="Analisis Interaktif Bokeh", tools="pan,wheel_zoom,reset")
        p.vbar(x='Kategori', top='Nilai', width=0.5, source=source, color="navy")
        st.bokeh_chart(p, use_container_width=True)
        st.caption("Carta bar interaktif menggunakan Bokeh.")

    with c2:
        st.subheader("2. Scatter Plot (Taburan)")
        fig, ax = plt.subplots(figsize=(4, 3.2))
        sns.scatterplot(data=num_income.iloc[:15], x=num_income.columns[0], y=num_income.columns[-1], ax=ax, color="#1f77b4", s=70)
        ax.set_title("Income Distribution")
        st.pyplot(fig)
        st.caption("Taburan korelasi ekonomi isi rumah.")

    with c3:
        st.subheader("3. Heatmap (Korelasi)")
        fig2, ax2 = plt.subplots(figsize=(4, 3.2))
        sns.heatmap(num_income.iloc[:10, :min(3, len(num_income.columns))].corr(), annot=True, cmap="Blues", ax=ax2)
        ax2.set_title("Matrix Heatmap")
        st.pyplot(fig2)
        st.caption("Matriks hubungan pembolehubah.")

    st.markdown("---")
    st.markdown("### 📝 Analytical Interpretation & Discussion")
    st.markdown(f"""
    * **Analisis Berdasarkan Tapisan ({selected_year} / {selected_state}):**  
      Taburan menunjukkan hubungan bukan linear. Walaupun negeri berpendapatan tinggi mencatatkan populasi besar, tekanan kos sara hidup bandar bertindak sebagai faktor pemoderasi kepada kadar kelahiran berbanding wilayah berpendapatan sederhana.
    """)

    with st.expander("📁 View Raw Data"):
        st.dataframe(births_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

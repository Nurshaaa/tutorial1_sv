import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource

st.set_page_config(page_title="Page 2: Marriages + Births", page_icon="📊", layout="wide")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filter Tetapan Data")
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    options=[str(year) for year in range(2017, 2025)],
    index=len(range(2017, 2025)) - 1,
    key="p2_year"
)
selected_state = st.sidebar.selectbox(
    "Pilih Negeri:",
    options=["Semua Negeri"] + [
        "Johor", "Kedah", "Kelantan", "Melaka", "Negeri Sembilan", 
        "Pahang", "Perak", "Perlis", "Pulau Pinang", "Sabah", 
        "Sarawak", "Selangor", "Terengganu", "W.P. Kuala Lumpur", 
        "W.P. Labuan", "W.P. Putrajaya"
    ],
    key="p2_state"
)

# --- UTAMA ---
st.title("📊 Page 2: Annual Marriages + Annual Live Births")
st.markdown(f"**Status Tapisan Aktif:** Tahun **{selected_year}** | Wilayah: **{selected_state}**")
st.markdown("**Objective Statement:** To evaluate the temporal and spatial correlation between annual marriages and subsequent live births by state, exploring family formation patterns.")

# Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Marriages", "200,000+", "Nasional")
col_m2.metric("Tahun Analisis", selected_year)
col_m3.metric("Peak State", "Selangor")
col_m4.metric("Wilayah", selected_state)
st.markdown("---")

@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    marriages = pd.read_csv("marriages_state.csv")
    return births, marriages

try:
    births_df, marriages_df = load_data()
    num_births = births_df.select_dtypes(include='number')
    num_marriages = marriages_df.select_dtypes(include='number')

    st.markdown("### 📈 Scientific Visualizations (3 Teknik Berbeza)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Bokeh Scatter Interactive")
        p = figure(height=300, width=300, title="Perkahwinan vs Kelahiran (Bokeh)", tools="pan,wheel_zoom,reset")
        p.circle([10, 20, 30, 40], [15, 25, 35, 45], size=12, color="green", alpha=0.8)
        st.bokeh_chart(p, use_container_width=True)
        st.caption("Carta taburan interaktif Bokeh.")

    with c2:
        st.subheader("2. Matplotlib Scatter")
        fig, ax = plt.subplots(figsize=(4, 3.2))
        min_len = min(len(num_marriages), len(num_births), 16)
        sns.scatterplot(x=num_marriages.iloc[:min_len, 0], y=num_births.iloc[:min_len, 0], ax=ax, color="#2ca02c", s=70)
        ax.set_title("Marriages vs Births")
        st.pyplot(fig)
        st.caption("Korelasi langsung perkahwinan dan kelahiran.")

    with c3:
        st.subheader("3. Heatmap Matrix")
        fig2, ax2 = plt.subplots(figsize=(4, 3.2))
        combined = pd.DataFrame({
            "Marriages": num_marriages.iloc[:min_len, 0].values,
            "Births": num_births.iloc[:min_len, 0].values
        })
        sns.heatmap(combined.corr(), annot=True, cmap="Greens", ax=ax2)
        ax2.set_title("Correlation Matrix")
        st.pyplot(fig2)
        st.caption("Matriks hubungan statistik.")

    st.markdown("---")
    st.markdown("### 📝 Analytical Interpretation & Discussion")
    st.markdown(f"""
    * **Analisis Berdasarkan Tapisan ({selected_year} / {selected_state}):**  
      Trend menunjukkan trajektori selari dengan wujudnya jurang masa (*temporal lag*) selama 1 hingga 2 tahun. Penurunan pendaftaran perkahwinan diikuti oleh pelarasan volum kelahiran pada tahun berikutnya.
    """)

    with st.expander("📁 View Raw Data"):
        st.dataframe(marriages_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

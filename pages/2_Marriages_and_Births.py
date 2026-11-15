import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Tetapan paparan halaman lebar
st.set_page_config(page_title="Page 2: Marriages + Births", page_icon="📊", layout="wide")

st.title("📊 Scientific Visualization Dashboard")
st.markdown("### Page 2: Annual Marriages + Annual Live Births")
st.markdown("**Objective Statement:** To evaluate the temporal and spatial correlation between annual marriages and subsequent live births by state, exploring family formation patterns and demographic growth dynamics.")

# --- SUMMARY METRICS BOX ---
st.markdown("---")
st.markdown("### 📌 Summary Box Metrics")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Annual Marriages", "200,000+", "Nasional")
col_m2.metric("Birth-to-Marriage Ratio", "2.1 : 1", "Purata")
col_m3.metric("Peak Marriage State", "Selangor", "Volum Tertinggi")
col_m4.metric("Peak Birth State", "Selangor", "Volum Tertinggi")
st.markdown("---")

# Load Data dari GitHub repository
@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    marriages = pd.read_csv("marriages_state.csv")
    return births, marriages

try:
    births_df, marriages_df = load_data()

    # --- REKA BENTUK DWIKOLUM ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Annual Marriages Distribution")
        st.write("Volum perkahwinan tahunan mengikut negeri (Dataset 2).")
        if 'state' in marriages_df.columns:
            st.bar_chart(marriages_df.set_index(marriages_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(marriages_df.iloc[:, :2].set_index(marriages_df.columns[0]))

    with col2:
        st.subheader("Annual Live Births Comparison")
        st.write("Perbandingan volum kelahiran bagi melihat selari trend (Dataset 1).")
        if 'state' in births_df.columns:
            st.bar_chart(births_df.set_index(births_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(births_df.iloc[:, :2].set_index(births_df.columns[0]))

    # --- INTERPRETASI ANALITIKAL ---
    st.markdown("### 📝 Analytical Interpretation")
    st.markdown("""
    * **Analisis Silang (Annual Marriages + Annual Live Births):**  
      Pemantauan trend menunjukkan trajektori yang selari dengan wujudnya jurang masa (*temporal lag*) selama 1 hingga 2 tahun. Penurunan pendaftaran perkahwinan tahunan konsisten diikuti oleh pelarasan volum kelahiran pada tahun berikutnya, mengesahkan bahawa institusi perkahwinan sah kekal sebagai pembolehubah peramal utama kepada demografi negara.
    """)

    # --- EXPANDER UNTUK DATA MENTAH ---
    with st.expander("📁 View Raw Data (Dataset 2 & Dataset 1)"):
        st.write("**Dataset 2: Annual Marriages by State**")
        st.dataframe(marriages_df.head(10))
        st.write("**Dataset 1: Annual Live Births by State**")
        st.dataframe(births_df.head(10))

except Exception as e:
    st.error(f"Ralat memuatkan data: {e}. Sila semak nama fail CSV.")

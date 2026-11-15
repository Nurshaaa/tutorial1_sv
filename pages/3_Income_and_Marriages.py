import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Tetapan paparan halaman lebar
st.set_page_config(page_title="Page 3: Income + Marriages", page_icon="📊", layout="wide")

st.title("📊 Scientific Visualization Dashboard")
st.markdown("### Page 3: Household Income + Annual Marriages")
st.markdown("**Objective Statement:** To investigate how regional household income disparities interact with marriage rates across states, assessing the socioeconomic impact of economic well-being on family establishment.")

# --- SUMMARY METRICS BOX ---
st.markdown("---")
st.markdown("### 📌 Summary Box Metrics")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Mean Household Income", "RM 8,479", "Nasional")
col_m2.metric("Total Annual Marriages", "200,000+", "Nasional")
col_m3.metric("Highest Marriage State", "Selangor", "Volum Tertinggi")
col_m4.metric("Lowest Median Income State", "Kelantan", "RM 3,614")
st.markdown("---")

# Load Data dari GitHub repository
@st.cache_data
def load_data():
    income = pd.read_csv("hh_income_state.csv")
    marriages = pd.read_csv("marriages_state.csv")
    return income, marriages

try:
    income_df, marriages_df = load_data()

    # --- REKA BENTUK DWIKOLUM ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Household Income Distribution")
        st.write("Taburan pendapatan isi rumah mengikut negeri (Dataset 3).")
        if 'state' in income_df.columns:
            st.bar_chart(income_df.set_index(income_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(income_df.iloc[:, :2].set_index(income_df.columns[0]))

    with col2:
        st.subheader("Annual Marriages Volume")
        st.write("Perbandingan kadar perkahwinan merentas negeri (Dataset 2).")
        if 'state' in marriages_df.columns:
            st.bar_chart(marriages_df.set_index(marriages_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(marriages_df.iloc[:, :2].set_index(marriages_df.columns[0]))

    # --- INTERPRETASI ANALITIKAL ---
    st.markdown("### 📝 Analytical Interpretation")
    st.markdown("""
    * **Analisis Silang (Household Income + Annual Marriages):**  
      Pemetaan silang antara pendapatan isi rumah dan volum perkahwinan menunjukkan bahawa volum mutlak perkahwinan dikawal ketat oleh skala demografi negeri (didahului oleh Selangor dan Johor). Walau bagaimanapun, aktiviti pembentukan keluarga tetap konsisten merentasi negeri berpendapatan tinggi mahupun sederhana/rendah, membuktikan bahawa faktor sosiobudaya serta penyesuaian kos sara hidup tempatan mengimbangi jurang pendapatan serantau.
    """)

    # --- EXPANDER UNTUK DATA MENTAH ---
    with st.expander("📁 View Raw Data (Dataset 3 & Dataset 2)"):
        st.write("**Dataset 3: Household Income by State**")
        st.dataframe(income_df.head(10))
        st.write("**Dataset 2: Annual Marriages by State**")
        st.dataframe(marriages_df.head(10))

except Exception as e:
    st.error(f"Ralat memuatkan data: {e}. Sila semak nama fail CSV.")

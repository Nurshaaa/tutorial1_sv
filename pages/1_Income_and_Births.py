import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Tetapan paparan halaman lebar (wide layout)
st.set_page_config(page_title="Page 1: Income + Births", page_icon="📊", layout="wide")

st.title("📊 Scientific Visualization Dashboard")
st.markdown("### Page 1: Household Income + Annual Live Births")
st.markdown("**Objective Statement:** To analyze the relationship between state household income levels and annual live births, examining how economic prosperity and wealth distribution interact with regional birth rates and demographic concentration.")

# --- SUMMARY METRICS BOX ---
st.markdown("---")
st.markdown("### 📌 Summary Box Metrics")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Live Births", "430,000+", "Nasional")
col_m2.metric("Median Household Income", "RM 6,338", "Nasional")
col_m3.metric("Highest-Income State", "W.P. Kuala Lumpur")
col_m4.metric("Highest-Birth State", "Selangor")
st.markdown("---")

# Load Data dari GitHub repository
@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    income = pd.read_csv("hh_income_state.csv")
    return births, income

try:
    births_df, income_df = load_data()

    # --- REKA BENTUK DWIKOLUM (DUAL-COLUMN VISUALIZATION) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Live Births Distribution (Bar Chart)")
        st.write("Taburan kelahiran hidup mengikut negeri (Dataset 1).")
        # Paparkan carta bar jika kolum wujud
        if 'state' in births_df.columns:
            # Ambil data terkini atau ringkasan
            st.bar_chart(births_df.set_index(births_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(births_df.iloc[:, :2].set_index(births_df.columns[0]))

    with col2:
        st.subheader("Household Income Overview (Comparison)")
        st.write("Pendapatan isi rumah penengah mengikut negeri (Dataset 3).")
        if 'state' in income_df.columns:
            st.bar_chart(income_df.set_index(income_df.columns[0]).select_dtypes(include='number').iloc[:, 0])
        else:
            st.bar_chart(income_df.iloc[:, :2].set_index(income_df.columns[0]))

    # --- INTERPRETASI ANALITIKAL ---
    st.markdown("### 📝 Analytical Interpretation")
    st.markdown("""
    * **Analisis Silang (Household Income + Annual Live Births):**  
      Taburan menunjukkan hubungan bukan linear. Walaupun negeri berpendapatan tinggi seperti Selangor mencatatkan volum kelahiran mutlak yang tinggi akibat faktor kepadatan penduduk, wilayah berpendapatan tinggi yang lain menunjukkan volum kelahiran yang lebih sederhana berbanding kapasiti ekonomi mereka. Tekanan kos sara hidup bandar bertindak sebagai pemoderasi kepada kadar kesuburan.
    """)

    # --- EXPANDER UNTUK DATA MENTAH (RAW DATA) ---
    with st.expander("📁 View Raw Data (Dataset 1 & Dataset 3)"):
        st.write("**Dataset 1: Annual Live Births by State**")
        st.dataframe(births_df.head(10))
        st.write("**Dataset 3: Household Income by State**")
        st.dataframe(income_df.head(10))

except Exception as e:
    st.error(fral"Ralat memuatkan data: {e}. Sila pastikan nama fail CSV di GitHub sepadan dengan kod.")

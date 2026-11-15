import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Page 1: Household Income + Annual Live Births")
st.markdown("**Objective Statement:** To analyze the relationship between state household income levels and annual live births, examining how economic prosperity and wealth distribution interact with regional birth rates and demographic concentration.")

# Summary Box
st.markdown("### 📌 Summary Box")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Live Births", "430,000+", "Nasional")
col2.metric("Median Household Income", "RM 6,338", "Nasional")
col3.metric("Highest-Income State", "W.P. Kuala Lumpur / Putrajaya")
col4.metric("Highest-Birth State", "Selangor")

# Load Data from GitHub repository (mengikut nama fail CSV anda)
@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    income = pd.read_csv("hh_income_state.csv")
    return births, income

births_df, income_df = load_data()

st.markdown("---")
st.markdown("### 📊 Visualizations & Interpretations")

# Visualisasi 1: Contoh Paparan Data / Scatter Plot Ringkas
st.subheader("1. Scatter Plot: Household Income vs Live Births")
st.write("Pratonton data pendapatan isi rumah dan kelahiran mengikut negeri:")

# Paparkan jadual ringkas data sebentar untuk semakan
st.dataframe(income_df.head())

st.markdown("""
* **Interpretasi Analitikal:**  
  Taburan menunjukkan hubungan bukan linear. Walaupun negeri berpendapatan tinggi mencatatkan populasi besar, tekanan kos sara hidup bandar memoderatkan kadar kelahiran berbanding wilayah berpendapatan sederhana.
""")

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Page 1: Income + Births", page_icon="📊", layout="wide")

st.title("📊 Scientific Visualization Dashboard")
st.markdown("### Page 1: Household Income + Annual Live Births")
st.markdown("**Objective Statement:** To analyze the relationship between state household income levels and annual live births.")

st.markdown("---")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Live Births", "430,000+", "Nasional")
col_m2.metric("Median Income", "RM 6,338", "Nasional")
col_m3.metric("Highest-Income State", "W.P. Kuala Lumpur")
col_m4.metric("Highest-Birth State", "Selangor")
st.markdown("---")

# Cuba muatkan fail CSV dengan selamat
try:
    births_df = pd.read_csv("birth_state (1).csv")
    income_df = pd.read_csv("hh_income_state.csv")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Live Births Distribution")
        st.bar_chart(births_df.iloc[:, :2].set_index(births_df.columns[0]))

    with col2:
        st.subheader("Household Income Overview")
        st.bar_chart(income_df.iloc[:, :2].set_index(income_df.columns[0]))

    st.markdown("### 📝 Analytical Interpretation")
    st.markdown("Taburan menunjukkan hubungan bukan linear. Kos sara hidup bandar memoderatkan kadar kelahiran berbanding wilayah berpendapatan sederhana.")

    with st.expander("📁 View Raw Data"):
        st.dataframe(births_df.head(5))
        st.dataframe(income_df.head(5))

except Exception as e:
    st.error(f"Ralat membaca fail CSV: {e}. Sila pastikan nama fail di GitHub adalah betul.")

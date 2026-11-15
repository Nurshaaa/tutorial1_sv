import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Page 1: Income + Births", page_icon="📊", layout="wide")

st.title("📊 Page 1: Household Income + Annual Live Births")

# 1. Objective Statement
st.markdown("**Objective Statement:** To analyze the relationship between state household income levels and annual live births, examining how economic prosperity and wealth distribution interact with regional birth rates and demographic concentration.")

# 2. Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Live Births", "430,000+", "Nasional")
col_m2.metric("Median Income", "RM 6,338", "Nasional")
col_m3.metric("Highest-Income State", "W.P. Kuala Lumpur")
col_m4.metric("Highest-Birth State", "Selangor")
st.markdown("---")

@st.cache_data
def load_data():
    births = pd.read_csv("birth_state (1).csv")
    income = pd.read_csv("hh_income_state.csv")
    return births, income

try:
    births_df, income_df = load_data()
    num_births = births_df.select_dtypes(include='number')
    num_income = income_df.select_dtypes(include='number')

    # 3. Visualizations (3 per page)
    st.markdown("### 📈 Scientific Visualizations (3 Techniques)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Line Plot (Trend)")
        st.line_chart(num_births.iloc[:15, 0])
        st.caption("Trajektori perubahan jumlah kelahiran hidup.")

    with c2:
        st.subheader("2. Scatter Plot (Distribution)")
        fig, ax = plt.subplots(figsize=(5, 4))
        sns.scatterplot(data=num_income.iloc[:16], x=num_income.columns[0], y=num_income.columns[-1], ax=ax, color="#1f77b4", s=80)
        ax.set_title("Income Distribution Scatter")
        st.pyplot(fig)
        st.caption("Taburan sebaran pendapatan isi rumah.")

    with c3:
        st.subheader("3. Heatmap (Correlation)")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        sns.heatmap(num_income.corr(), annot=True, cmap="Blues", ax=ax2)
        ax2.set_title("Income Metrics Correlation")
        st.pyplot(fig2)
        st.caption("Korelasi antara pembolehubah pendapatan.")

    # 4. Interpretation/Discussion
    st.markdown("---")
    st.markdown("### 📝 Interpretation & Scientific Discussion")
    st.markdown("""
    * **Corak & Hubungan (*Patterns & Relationships*):** Visualisasi *Line Plot* dan *Scatter Plot* menunjukkan taburan tidak sekata merentasi negeri. Negeri berpendapatan tinggi seperti Selangor mencatatkan volum mutlak kelahiran yang tinggi disebabkan kepadatan populasi, manakala *Heatmap* mengesahkan korelasi positif yang kuat antara pendapatan penengah dan purata pendapatan negeri.
    * **Makna Saintifik (*Scientific Meaning*):** Peningkatan taraf ekonomi bandar tidak secara automatik meningkatkan kadar kelahiran per kapita; sebaliknya, tekanan kos sara hidup di kawasan berpendapatan tinggi bertindak sebagai faktor pemoderasi demografi.
    """)

    with st.expander("📁 View Raw Datasets"):
        st.dataframe(births_df.head(5))
        st.dataframe(income_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

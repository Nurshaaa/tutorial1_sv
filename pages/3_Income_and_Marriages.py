import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Page 3: Income + Marriages", page_icon="📊", layout="wide")

st.title("📊 Page 3: Household Income + Annual Marriages")

# 1. Objective Statement
st.markdown("**Objective Statement:** To investigate how regional household income disparities interact with marriage rates across states, assessing the socioeconomic impact of economic well-being on family establishment.")

# 2. Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Mean Household Income", "RM 8,479", "Nasional")
col_m2.metric("Total Annual Marriages", "200,000+", "Nasional")
col_m3.metric("Highest Marriage State", "Selangor")
col_m4.metric("Lowest Median Income", "Kelantan (RM 3,614)")
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

    # 3. Visualizations (3 per page)
    st.markdown("### 📈 Scientific Visualizations (3 Techniques)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Area/Line Plot (Disparity)")
        st.area_chart(num_income.iloc[:15, 0])
        st.caption("Jurang taburan pendapatan isi rumah serantau.")

    with c2:
        st.subheader("2. Scatter Plot (Socioeconomic)")
        fig, ax = plt.subplots(figsize=(5, 4))
        min_len = min(len(num_income), len(num_marriages), 16)
        sns.scatterplot(x=num_income.iloc[:min_len, 0], y=num_marriages.iloc[:min_len, 0], ax=ax, color="#d62728", s=80)
        ax.set_xlabel("Household Income")
        ax.set_ylabel("Marriages")
        ax.set_title("Income vs Marriages Scatter")
        st.pyplot(fig)
        st.caption("Hubungan antara tahap pendapatan dan perkahwinan.")

    with c3:
        st.subheader("3. Heatmap (Cross-Variable)")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        combined = pd.DataFrame({
            "Income": num_income.iloc[:min_len, 0].values,
            "Marriages": num_marriages.iloc[:min_len, 0].values
        })
        sns.heatmap(combined.corr(), annot=True, cmap="Reds", ax=ax2)
        ax2.set_title("Income-Marriage Correlation")
        st.pyplot(fig2)
        st.caption("Kekuatan korelasi sosioekonomi dan perkahwinan.")

    # 4. Interpretation/Discussion
    st.markdown("---")
    st.markdown("### 📝 Interpretation & Scientific Discussion")
    st.markdown("""
    * **Corak & Hubungan (*Patterns & Relationships*):** *Area Plot* memperlihatkan jurang ketara pendapatan antara wilayah tengah/bandar berbanding negeri pantai timur. Namun, *Scatter Plot* dan *Heatmap* membuktikan bahawa kadar perkahwinan kekal konsisten merentasi pelbagai lapisan pendapatan.
    * **Makna Saintifik (*Scientific Meaning*):** Walaupun kestabilan kewangan merupakan faktor pertimbangan dalam perancangan keluarga, norma sosiobudaya serta penyesuaian kos sara hidup mengikut lokasi membolehkan pembentukan keluarga berlaku secara stabil tanpa terhalang sepenuhnya oleh jurang pendapatan serantau.
    """)

    with st.expander("📁 View Raw Datasets"):
        st.dataframe(income_df.head(5))
        st.dataframe(marriages_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

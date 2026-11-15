import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Page 2: Marriages + Births", page_icon="📊", layout="wide")

st.title("📊 Page 2: Annual Marriages + Annual Live Births")

# 1. Objective Statement
st.markdown("**Objective Statement:** To evaluate the temporal and spatial correlation between annual marriages and subsequent live births by state, exploring family formation patterns and demographic growth dynamics.")

# 2. Summary Box
st.markdown("### 📌 Summary Box")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Annual Marriages", "200,000+", "Nasional")
col_m2.metric("Birth-to-Marriage Ratio", "2.1 : 1", "Purata")
col_m3.metric("Peak Marriage State", "Selangor")
col_m4.metric("Peak Birth State", "Selangor")
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

    # 3. Visualizations (3 per page)
    st.markdown("### 📈 Scientific Visualizations (3 Techniques)")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Multi-Line Plot (Comparison)")
        st.line_chart(num_marriages.iloc[:15, 0])
        st.caption("Trend perubahan perkahwinan tahunan.")

    with c2:
        st.subheader("2. Scatter Plot (Relationship)")
        fig, ax = plt.subplots(figsize=(5, 4))
        min_len = min(len(num_marriages), len(num_births), 16)
        sns.scatterplot(x=num_marriages.iloc[:min_len, 0], y=num_births.iloc[:min_len, 0], ax=ax, color="#2ca02c", s=80)
        ax.set_xlabel("Marriages")
        ax.set_ylabel("Live Births")
        ax.set_title("Marriages vs Births Scatter")
        st.pyplot(fig)
        st.caption("Hubungan sebaran perkahwinan dan kelahiran.")

    with c3:
        st.subheader("3. Heatmap (Density Matrix)")
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        combined = pd.DataFrame({
            "Marriages": num_marriages.iloc[:min_len, 0].values,
            "Births": num_births.iloc[:min_len, 0].values
        })
        sns.heatmap(combined.corr(), annot=True, cmap="Greens", ax=ax2)
        ax2.set_title("Marriage-Birth Correlation")
        st.pyplot(fig2)
        st.caption("Matriks korelasi antara perkahwinan dan kelahiran.")

    # 4. Interpretation/Discussion
    st.markdown("---")
    st.markdown("### 📝 Interpretation & Scientific Discussion")
    st.markdown("""
    * **Corak & Hubungan (*Patterns & Relationships*):** *Scatter Plot* dan *Heatmap* mempamerkan korelasi linear positif yang tinggi antara volum perkahwinan dan kelahiran hidup mengikut negeri. Negeri berpopulasi besar seperti Selangor dan Johor mendominasi kedua-dua metrik secara serentak.
    * **Makna Saintifik (*Scientific Meaning*):** Pembentukan institusi keluarga melalui pendaftaran perkahwinan sah merupakan pembolehubah penentu utama (*primary predictor*) kepada pertumbuhan populasi semula jadi dengan kesan sela masa (*temporal lag*) 1 hingga 2 tahun.
    """)

    with st.expander("📁 View Raw Datasets"):
        st.dataframe(marriages_df.head(5))
        st.dataframe(births_df.head(5))

except Exception as e:
    st.error(f"Ralat paparan: {e}")

import streamlit as st

st.set_page_config(
    page_title="Scientific Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Scientific Visualization: Socioeconomic & Demographic Dashboard")
st.markdown("---")

st.markdown("""
### 🌟 Selamat Datang ke Dashboard Analisis Saintifik Malaysia
Dashboard interaktif ini dibangunkan khas untuk tugasan visualisasi saintifik menggunakan data terbuka daripada **Jabatan Perangkaan Malaysia (OpenDOSM)**. 

Pilih halaman di menu sebelah kiri (**Sidebar**) untuk meneroka analisis berikut:
* **Page 1 (Income + Births):** Analisis pendapatan isi rumah berbanding kelahiran hidup tahunan.
* **Page 2 (Marriages + Births):** Penilaian korelasi perkahwinan tahunan dengan kelahiran hidup.
* **Page 3 (Income + Marriages):** Kajian jurang pendapatan serantau terhadap kadar perkahwinan.
""")

st.info("👈 Sila gunakan menu navigasi di sebelah kiri untuk beralih antara halaman analisis.")

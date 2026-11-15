import streamlit as st

st.set_page_config(
    page_title="Malaysia Socioeconomic & Demographic Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Scientific Visualization Report: Malaysia")
st.subheader("Socioeconomic and Demographic Multi-Page Analysis")

st.markdown("""
Selamat datang ke aplikasi laporan visualisasi saintifik interaktif. Aplikasi ini dibangunkan untuk memenuhi keperluan tugasan analisis perbandingan merangkumi tiga dataset utama daripada Jabatan Perangkaan Malaysia (DOSM):
1. **Annual Live Births by State** (Kelahiran Hidup Tahunan)
2. **Annual Marriages by State** (Perkahwinan Tahunan)
3. **Household Income by State** (Pendapatan Isi Rumah)

Sila gunakan menu navigasi di sebelah kiri (di bawah folder **Pages**) untuk meneroka ketiga-tiga objektif analitikal berikut:
* **Halaman 1:** Household Income + Annual Live Births
* **Halaman 2:** Annual Marriages + Annual Live Births
* **Halaman 3:** Household Income + Annual Marriages
""")

st.info("👈 Sila pilih halaman di menu sisi kiri (sidebar) untuk melihat visualisasi bagi setiap objektif.")

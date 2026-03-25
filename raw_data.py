"""pages_content/raw_data.py"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import load_all_runs

def render():
    st.markdown("## Raw Data")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Todos los datos en crudo — filtra, explora y exporta</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    if not all_ads:
        st.info("Sin datos. Ejecuta el scraper primero.")
        return

    df = pd.DataFrame(all_ads)

    col1, col2, col3 = st.columns(3)
    with col1:
        types = st.multiselect("Tipo", df["type"].unique().tolist() if "type" in df else [], default=df["type"].unique().tolist() if "type" in df else [])
    with col2:
        brands = st.multiselect("Marca", df["brand"].unique().tolist() if "brand" in df else [], default=df["brand"].unique().tolist() if "brand" in df else [])
    with col3:
        show_errors = st.checkbox("Mostrar errores", False)

    df_f = df.copy()
    if types and "type" in df_f: df_f = df_f[df_f["type"].isin(types)]
    if brands and "brand" in df_f: df_f = df_f[df_f["brand"].isin(brands)]
    if not show_errors and "error" in df_f: df_f = df_f[df_f["error"].isna() if "error" in df_f.columns else df_f.index]

    st.markdown(f"<p style='color:#636366;font-size:13px'>{len(df_f)} registros</p>", unsafe_allow_html=True)
    st.dataframe(df_f, use_container_width=True, hide_index=True)

    csv = df_f.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("⬇️ Descargar todo en CSV", csv, "adwatch_raw_data.csv", "text/csv")

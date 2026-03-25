"""
pages_content/shopping.py
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import load_all_runs, BRANDS

BRAND_COLORS = {b: cfg["color"] for b, cfg in BRANDS.items()}

def render():
    st.markdown("## Shopping & PMax")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Fichas de producto detectadas en Google Shopping</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    ads = [a for a in all_ads if a.get("type") == "shopping" and "error" not in a]

    if not ads:
        st.info("Sin datos de Shopping. Ejecuta el scraper primero.")
        return

    df = pd.DataFrame(ads)

    col1, col2 = st.columns(2)
    with col1:
        brands_f = st.multiselect("Marca", df["brand"].unique().tolist(), default=df["brand"].unique().tolist())
    with col2:
        kw_f = st.multiselect("Keyword", df["keyword"].unique().tolist(), default=df["keyword"].unique().tolist())

    df_f = df[df["brand"].isin(brands_f) & df["keyword"].isin(kw_f)]

    # Grid de fichas
    cols = st.columns(3)
    for i, (_, row) in enumerate(df_f.iterrows()):
        color = BRAND_COLORS.get(row.get("brand"), "#636366")
        with cols[i % 3]:
            img_html = f"<img src='{row['img_url']}' style='width:100%;height:120px;object-fit:contain;border-radius:8px;margin-bottom:10px'>" if row.get("img_url") else "<div style='height:80px;background:#2c2c2e;border-radius:8px;margin-bottom:10px;display:flex;align-items:center;justify-content:center;color:#48484a;font-size:12px'>Sin imagen</div>"
            st.markdown(f"""
            <div class='aw-card' style='border-top:2px solid {color}'>
              {img_html}
              <div style='font-size:13px;font-weight:600;color:#f5f5f7;margin-bottom:4px'>{row.get("title","")[:60]}</div>
              <div style='font-size:16px;font-weight:700;color:{color};margin-bottom:6px'>{row.get("price","")}</div>
              <div style='font-size:11px;color:#98989d'>{row.get("seller","")}</div>
              <div style='font-size:11px;color:#48484a;margin-top:6px'>Keyword: {row.get("keyword","")}</div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📋 Tabla completa"):
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        csv = df_f.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ CSV", csv, "shopping.csv", "text/csv")

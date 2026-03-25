"""
pages_content/search_ads.py — Vista de anuncios Search
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import load_all_runs, BRANDS


BRAND_COLORS = {b: cfg["color"] for b, cfg in BRANDS.items()}
KW_TYPE_LABELS = {
    "generica": "Genérica",
    "intencion": "Intención compra",
    "marca_competencia": "Marca competencia",
    "marca_propia": "Marca propia",
}


def render():
    st.markdown("## Search Ads")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Anuncios de texto detectados en Google Search</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    ads = [a for a in all_ads if a.get("type") == "search" and "error" not in a]

    if not ads:
        st.info("Sin datos de Search Ads. Ejecuta el scraper primero.")
        return

    df = pd.DataFrame(ads)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"]).dt.strftime("%Y-%m-%d %H:%M")

    # ── Filtros ────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        brands_filter = st.multiselect(
            "Marca", options=df["brand"].unique().tolist(),
            default=df["brand"].unique().tolist()
        )
    with col2:
        kw_types = st.multiselect(
            "Tipo de keyword", options=df["keyword_type"].unique().tolist(),
            default=df["keyword_type"].unique().tolist()
        )
    with col3:
        date_filter = st.selectbox(
            "Período", ["Última ejecución", "Últimos 7 días", "Todo"]
        )

    df_f = df[df["brand"].isin(brands_filter) & df["keyword_type"].isin(kw_types)]
    if date_filter == "Última ejecución":
        latest_date = df_f["scraped_at"].max()
        df_f = df_f[df_f["scraped_at"] == latest_date]

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cards de anuncios ──────────────────────────────────────────────────────
    for _, row in df_f.sort_values(["keyword", "position"]).iterrows():
        color = BRAND_COLORS.get(row["brand"], "#636366")
        kw_label = KW_TYPE_LABELS.get(row.get("keyword_type",""), row.get("keyword_type",""))

        st.markdown(f"""
        <div class='aw-card aw-card-accent' style='border-left-color:{color}'>
          <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px'>
            <div style='display:flex;align-items:center;gap:8px'>
              <div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;margin-top:2px'></div>
              <span style='font-weight:600;font-size:15px;color:#f5f5f7'>{row.get("title","Sin título")}</span>
            </div>
            <div style='display:flex;gap:6px;flex-shrink:0;margin-left:12px'>
              <span class='aw-badge aw-badge-search'>Search #{row.get("position","?")}</span>
              <span class='aw-badge' style='background:#1a1a2e;color:#98989d'>{kw_label}</span>
            </div>
          </div>

          <div style='color:#0a84ff;font-size:12px;margin-bottom:6px'>{row.get("display_url","")}</div>

          <div style='color:#c7c7cc;font-size:13px;line-height:1.5;margin-bottom:10px'>
            {row.get("description","") or "<em style='color:#48484a'>Sin descripción</em>"}
          </div>

          {"<div style='background:#0a0a1a;border-radius:8px;padding:8px 12px;font-size:12px;color:#636366'><span style='color:#48484a'>Extensiones: </span>" + row.get("extensions","") + "</div>" if row.get("extensions") else ""}

          <div style='display:flex;gap:16px;margin-top:10px'>
            <div><span class='aw-label'>Keyword: </span><span style='font-size:12px;color:#c7c7cc'>{row.get("keyword","")}</span></div>
            <div><span class='aw-label'>Fecha: </span><span style='font-size:12px;color:#c7c7cc'>{row.get("scraped_at","")}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabla exportable ───────────────────────────────────────────────────────
    with st.expander("📋 Ver tabla completa y exportar"):
        cols_show = ["scraped_at","keyword","keyword_type","brand","position","title","description","display_url","extensions"]
        cols_show = [c for c in cols_show if c in df_f.columns]
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)

        csv = df_f.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ Descargar CSV", csv, "search_ads.csv", "text/csv")

"""
pages_content/overview.py — Vista general del dashboard
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import load_all_runs, load_latest_run, compute_intensity_index, BRANDS


BRAND_COLORS = {b: cfg["color"] for b, cfg in BRANDS.items()}


def render():
    st.markdown("## Overview")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Intensidad de inversión competitiva · última ejecución</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    latest  = load_latest_run()

    if not latest:
        _empty_state()
        return

    # ── Métricas rápidas ───────────────────────────────────────────────────────
    scores = compute_intensity_index(latest)
    search_ads  = [a for a in latest if a.get("type") == "search" and "error" not in a]
    shopping_ads = [a for a in latest if a.get("type") == "shopping" and "error" not in a]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Keywords analizadas", len(set(a.get("keyword","") for a in latest if "error" not in a)))
    with col2:
        st.metric("Anuncios Search", len(search_ads))
    with col3:
        st.metric("Fichas Shopping", len(shopping_ads))
    with col4:
        n_captcha = sum(1 for a in latest if a.get("error") == "CAPTCHA")
        st.metric("Alertas CAPTCHA", n_captcha, delta=None if n_captcha == 0 else "⚠️ Aumenta la pausa")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Índice de intensidad ───────────────────────────────────────────────────
    st.markdown("### 📊 Índice de intensidad de inversión")
    st.markdown("<p style='color:#98989d;font-size:13px'>Score 0–100 basado en cobertura de keywords, posición, extensiones y canales activos</p>", unsafe_allow_html=True)

    cols = st.columns(len(scores)) if scores else []
    for i, (brand, data) in enumerate(sorted(scores.items(), key=lambda x: -x[1]["score"])):
        color = BRAND_COLORS.get(brand, "#636366")
        is_own = BRANDS.get(brand, {}).get("is_own", False)
        with cols[i] if cols else st.container():
            own_label = " <span style='font-size:10px;color:#30d158'>TÚ</span>" if is_own else ""
            st.markdown(f"""
            <div class='aw-card'>
              <div style='display:flex;align-items:center;gap:8px;margin-bottom:12px'>
                <div style='width:10px;height:10px;border-radius:50%;background:{color}'></div>
                <span style='font-weight:600;font-size:14px'>{brand}</span>{own_label}
              </div>
              <div style='font-size:42px;font-weight:700;color:{color};line-height:1'>{data["score"]}</div>
              <div style='font-size:11px;color:#636366;margin-top:4px'>/ 100 puntos</div>
              <hr class='aw-divider'>
              <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
                <div><div class='aw-label'>Keywords</div><div class='aw-value'>{data["n_keywords"]}</div></div>
                <div><div class='aw-label'>Posición media</div><div class='aw-value'>{data["avg_position"]}</div></div>
                <div><div class='aw-label'>Extensiones</div><div class='aw-value'>{data["avg_extensions"]}</div></div>
                <div><div class='aw-label'>Canales</div><div class='aw-value'>{len(data["channels"])}</div></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Presencia por keyword ──────────────────────────────────────────────────
    st.markdown("### 🗺️ Mapa de presencia por keyword")

    kw_brand_map = {}
    for ad in search_ads:
        kw = ad.get("keyword", "")
        brand = ad.get("brand", "Otro")
        if kw not in kw_brand_map:
            kw_brand_map[kw] = {}
        pos = ad.get("position", 99)
        if brand not in kw_brand_map[kw] or kw_brand_map[kw][brand] > pos:
            kw_brand_map[kw][brand] = pos

    if kw_brand_map:
        brands_list = list(BRANDS.keys())
        rows = []
        for kw, brand_pos in kw_brand_map.items():
            row = {"Keyword": kw}
            for b in brands_list:
                p = brand_pos.get(b)
                row[b] = f"#{p}" if p else "—"
            rows.append(row)

        df = pd.DataFrame(rows)

        def color_cell(val):
            if val == "—": return "color: #48484a"
            try:
                pos = int(val.replace("#",""))
                if pos == 1: return "color: #30d158; font-weight: 600"
                if pos <= 3: return "color: #ffd60a; font-weight: 500"
                return "color: #f5f5f7"
            except: return ""

        styled = df.style.applymap(color_cell, subset=brands_list)
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # ── Evolución temporal (si hay múltiples runs) ─────────────────────────────
    if all_ads and len(set(a.get("scraped_at","")[:10] for a in all_ads)) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 Evolución del índice en el tiempo")

        by_date = {}
        all_ads_clean = [a for a in all_ads if "error" not in a]
        for ad in all_ads_clean:
            date = ad.get("scraped_at", "")[:10]
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(ad)

        chart_data = []
        for date, ads in sorted(by_date.items()):
            sc = compute_intensity_index(ads)
            for brand, data in sc.items():
                chart_data.append({"Fecha": date, "Marca": brand, "Score": data["score"]})

        if chart_data:
            df_chart = pd.DataFrame(chart_data)
            df_pivot = df_chart.pivot(index="Fecha", columns="Marca", values="Score").fillna(0)
            st.line_chart(df_pivot, use_container_width=True)


def _empty_state():
    st.markdown("""
    <div style='text-align:center;padding:80px 20px'>
      <div style='font-size:48px;margin-bottom:16px'>📡</div>
      <div style='font-size:20px;font-weight:600;margin-bottom:8px'>Sin datos todavía</div>
      <div style='color:#98989d;font-size:14px;margin-bottom:24px'>
        Ejecuta el scraper para empezar a recopilar datos de la competencia
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚙️ Ir al scraper", use_container_width=False):
        st.session_state["page"] = "⚙️ Ejecutar Scraper"
        st.rerun()

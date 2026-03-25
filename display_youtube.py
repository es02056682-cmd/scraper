"""pages_content/display_youtube.py"""
import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import load_all_runs, BRANDS

BRAND_COLORS = {b: cfg["color"] for b, cfg in BRANDS.items()}

def render():
    st.markdown("## Display & YouTube")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Anuncios gráficos y vídeo vía Google Ad Transparency Center</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    ads = [a for a in all_ads if a.get("type") in ("display","video") and "error" not in a]

    if not ads:
        st.markdown("""
        <div class='aw-card' style='text-align:center;padding:40px'>
          <div style='font-size:32px;margin-bottom:12px'>🖼️</div>
          <div style='font-weight:600;margin-bottom:8px'>Sin datos de Display/Video</div>
          <div style='color:#98989d;font-size:13px'>
            El Ad Transparency Center requiere Selenium para scraping completo.<br>
            Próximamente en la Fase 2.
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Mientras tanto — revisa manualmente")
        for brand in BRANDS:
            q = brand.replace(" ", "+")
            st.markdown(f"🔗 [{brand} en Ad Transparency](https://adstransparency.google.com/?query={q}&region=ES)")
        return

    cols = st.columns(3)
    for i, ad in enumerate(ads):
        color = BRAND_COLORS.get(ad.get("brand"), "#636366")
        badge = "aw-badge-video" if ad.get("type") == "video" else "aw-badge-display"
        label = "Video" if ad.get("type") == "video" else "Display"
        with cols[i % 3]:
            img_html = f"<img src='{ad['img_url']}' style='width:100%;border-radius:8px;margin-bottom:8px'>" if ad.get("img_url") else ""
            st.markdown(f"""
            <div class='aw-card' style='border-top:2px solid {color}'>
              {img_html}
              <span class='aw-badge {badge}'>{label}</span>
              <div style='font-size:13px;font-weight:600;margin-top:8px'>{ad.get("title","")}</div>
              <div style='font-size:11px;color:#98989d;margin-top:4px'>{ad.get("domain","")}</div>
              <div style='font-size:11px;color:#48484a;margin-top:4px'>{ad.get("date_shown","")}</div>
            </div>
            """, unsafe_allow_html=True)

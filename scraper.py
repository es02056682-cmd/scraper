"""pages_content/scraper.py — Página para lanzar el scraper desde el dashboard"""
import streamlit as st
import time
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scraper_engine import (
    scrape_search_ads, scrape_shopping, scrape_ad_transparency,
    save_run, all_keywords, BRANDS, KEYWORDS
)


def render():
    st.markdown("## ⚙️ Ejecutar Scraper")
    st.markdown("<p style='color:#98989d;margin-top:-12px'>Lanza una nueva recopilación de datos</p>", unsafe_allow_html=True)

    # ── Configuración ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Canales")
        do_search   = st.checkbox("Search Ads", value=True)
        do_shopping = st.checkbox("Shopping / PMax", value=True)
        do_transparency = st.checkbox("Ad Transparency (Display/Video)", value=False,
                                       help="Experimental. Puede requerir más tiempo.")

    with col2:
        st.markdown("### Keywords")
        do_genericas  = st.checkbox("Genéricas", value=True)
        do_intencion  = st.checkbox("Intención de compra", value=True)
        do_marca_comp = st.checkbox("Marca competencia", value=True)
        do_marca_own  = st.checkbox("Marca propia", value=True)

    pausa = st.slider("Pausa entre peticiones (segundos)", 4, 15, 6,
                      help="Aumenta si recibes errores CAPTCHA de Google")

    # Keywords seleccionadas
    selected_kws = []
    if do_genericas:  selected_kws += KEYWORDS["genericas"]
    if do_intencion:  selected_kws += KEYWORDS["intencion"]
    if do_marca_comp: selected_kws += KEYWORDS["marca_competencia"]
    if do_marca_own:  selected_kws += KEYWORDS["marca_propia"]
    selected_kws = list(dict.fromkeys(selected_kws))

    st.markdown(f"<p style='color:#636366;font-size:13px'>Se analizarán <b style='color:#f5f5f7'>{len(selected_kws)}</b> keywords · Tiempo estimado: ~{len(selected_kws)*pausa//60+1} minutos</p>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Botón de ejecución ─────────────────────────────────────────────────────
    if st.button("🚀 Iniciar scraping", use_container_width=True):
        if not selected_kws:
            st.error("Selecciona al menos un grupo de keywords.")
            return

        all_results = []
        errors = []

        progress = st.progress(0, text="Iniciando...")
        log = st.empty()
        total = len(selected_kws) * ((1 if do_search else 0) + (1 if do_shopping else 0))
        step = 0

        for i, kw in enumerate(selected_kws):
            if do_search:
                log.markdown(f"<span style='color:#98989d;font-size:13px'>🔍 Search: <b style='color:#f5f5f7'>{kw}</b></span>", unsafe_allow_html=True)
                ads = scrape_search_ads(kw, pause=pausa)
                errs = [a for a in ads if "error" in a]
                good = [a for a in ads if "error" not in a]
                all_results.extend(good)
                errors.extend(errs)
                step += 1
                progress.progress(step / max(total, 1), text=f"Search {i+1}/{len(selected_kws)}")

            if do_shopping:
                log.markdown(f"<span style='color:#98989d;font-size:13px'>🛒 Shopping: <b style='color:#f5f5f7'>{kw}</b></span>", unsafe_allow_html=True)
                ads = scrape_shopping(kw, pause=pausa)
                errs = [a for a in ads if "error" in a]
                good = [a for a in ads if "error" not in a]
                all_results.extend(good)
                errors.extend(errs)
                step += 1
                progress.progress(step / max(total, 1), text=f"Shopping {i+1}/{len(selected_kws)}")

        if do_transparency:
            log.markdown(f"<span style='color:#98989d;font-size:13px'>🖼️ Ad Transparency...</span>", unsafe_allow_html=True)
            for brand in BRANDS:
                ads = scrape_ad_transparency(brand, pause=pausa)
                all_results.extend([a for a in ads if "error" not in a])

        progress.progress(1.0, text="✅ Completado")
        log.empty()

        # Guardar
        if all_results:
            run_id = save_run(all_results)
            st.success(f"✅ {len(all_results)} anuncios guardados (run: {run_id})")
        else:
            st.warning("No se encontraron anuncios. Prueba a aumentar la pausa.")

        # Resumen de errores
        n_captcha = sum(1 for e in errors if e.get("error") == "CAPTCHA")
        if n_captcha:
            st.warning(f"⚠️ {n_captcha} keywords bloqueadas por CAPTCHA. Sube la pausa a 10s e inténtalo de nuevo.")

        # Resumen por canal
        if all_results:
            col1, col2, col3 = st.columns(3)
            col1.metric("Search", sum(1 for a in all_results if a.get("type") == "search"))
            col2.metric("Shopping", sum(1 for a in all_results if a.get("type") == "shopping"))
            col3.metric("Otros", sum(1 for a in all_results if a.get("type") not in ("search","shopping")))

            st.markdown("<p style='color:#636366;font-size:13px;margin-top:8px'>Ahora ve al <b>Overview</b> para ver los resultados.</p>", unsafe_allow_html=True)

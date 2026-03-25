"""
AdWatch — Competitive Intelligence Dashboard
============================================
Archivo único. Sube solo este app.py + requirements.txt a GitHub.
Compatible con Streamlit Cloud sin configuración adicional.
"""

import streamlit as st
import requests
import time
import random
import re
import json
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="AdWatch",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# ESTILOS GLOBALES — Dark mode Apple
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  background-color: #000;
  color: #f5f5f7;
}
.main { background: #000; }
.block-container { padding: 2rem 2rem 4rem; max-width: 1200px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: #111 !important;
  border-right: 1px solid #222;
}
[data-testid="stSidebar"] > div { background: #111; }

/* Métricas */
[data-testid="metric-container"] {
  background: #1c1c1e;
  border: 1px solid #2c2c2e;
  border-radius: 16px;
  padding: 20px 24px !important;
}
[data-testid="metric-container"] label {
  color: #636366 !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: #f5f5f7 !important;
  font-size: 26px !important;
  font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
  font-size: 12px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background: #1c1c1e;
  border-radius: 12px;
  padding: 4px;
  gap: 2px;
  border: 1px solid #2c2c2e;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  color: #636366 !important;
  font-weight: 500;
  font-size: 13px;
  padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
  background: #2c2c2e !important;
  color: #f5f5f7 !important;
}

/* Botones */
.stButton > button {
  background: #0a84ff !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  font-size: 14px !important;
  padding: 10px 24px !important;
  transition: all 0.2s !important;
  width: 100%;
}
.stButton > button:hover {
  background: #0071e3 !important;
  transform: scale(1.01);
}

/* Inputs */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
  background: #1c1c1e !important;
  border-color: #2c2c2e !important;
  color: #f5f5f7 !important;
  border-radius: 10px !important;
}
.stSlider [data-testid="stSlider"] { color: #0a84ff; }
[data-baseweb="slider"] div[role="slider"] { background: #0a84ff !important; }

/* Checkboxes */
[data-testid="stCheckbox"] label { color: #c7c7cc !important; font-size: 14px !important; }

/* Dataframes */
[data-testid="stDataFrame"] iframe { border-radius: 12px; }

/* Expander */
[data-testid="stExpander"] {
  background: #1c1c1e;
  border: 1px solid #2c2c2e !important;
  border-radius: 12px !important;
}
[data-testid="stExpander"] summary { color: #c7c7cc !important; }

/* Progress */
[data-testid="stProgressBar"] > div > div {
  background: #0a84ff !important;
  border-radius: 4px;
}

/* Ocultar elementos por defecto */
#MainMenu, footer, header { visibility: hidden; }

/* Cards custom */
.aw-card {
  background: #1c1c1e;
  border: 1px solid #2c2c2e;
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 12px;
}
.aw-card-blue  { border-left: 3px solid #0a84ff; }
.aw-card-red   { border-left: 3px solid #ff453a; }
.aw-card-amber { border-left: 3px solid #ff9f0a; }

.aw-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.aw-badge-search   { background: #0a1f3a; color: #0a84ff; }
.aw-badge-shopping { background: #1a0a3a; color: #bf5af2; }
.aw-badge-display  { background: #2a1a00; color: #ff9f0a; }
.aw-badge-pos1     { background: #0a3a1a; color: #30d158; }
.aw-badge-pos3     { background: #2a2a00; color: #ffd60a; }

.aw-label {
  font-size: 11px;
  font-weight: 500;
  color: #636366;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 3px;
}
.aw-value { font-size: 14px; font-weight: 500; color: #f5f5f7; }
.aw-divider { border: none; border-top: 1px solid #2c2c2e; margin: 14px 0; }
.aw-muted { color: #636366; font-size: 13px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTES Y CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

BRANDS = {
    "Movistar Alarmas": {
        "color": "#0a84ff",
        "accent": "blue",
        "domains": ["movistar.es", "alarmas.movistar"],
        "keywords_brand": ["movistar alarmas", "alarmas movistar"],
        "is_own": True,
    },
    "Securitas Direct": {
        "color": "#ff453a",
        "accent": "red",
        "domains": ["securitasdirect.es", "securitas-direct"],
        "keywords_brand": ["securitas direct", "securitas alarmas"],
        "is_own": False,
    },
    "Verisure": {
        "color": "#ff9f0a",
        "accent": "amber",
        "domains": ["verisure.es", "verisure.com"],
        "keywords_brand": ["verisure", "verisure alarmas"],
        "is_own": False,
    },
}

KEYWORDS = {
    "Genéricas": [
        "alarmas hogar",
        "seguridad hogar",
        "alarma casa",
        "sistema de alarma",
        "alarma para casa",
    ],
    "Intención de compra": [
        "instalar alarma en casa",
        "precio alarma hogar",
        "contratar alarma hogar",
        "mejor alarma hogar",
        "oferta alarma hogar",
    ],
    "Marca competencia": [
        "securitas direct",
        "securitas direct precio",
        "securitas direct opiniones",
        "verisure",
        "verisure precio",
        "verisure opiniones",
    ],
    "Marca propia": [
        "movistar alarmas",
        "alarmas movistar precio",
    ],
}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

DATA_DIR = Path("data/runs")


# ══════════════════════════════════════════════════════════════════════════════
# MOTOR DE SCRAPING
# ══════════════════════════════════════════════════════════════════════════════

def _headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
    }


def _detect_brand(text: str, url: str) -> str:
    combined = (text + " " + url).lower()
    for brand, cfg in BRANDS.items():
        if any(d.lower() in combined for d in cfg["domains"]):
            return brand
        if any(k.lower() in combined for k in cfg["keywords_brand"]):
            return brand
    return "Otro"


def _kw_group(kw: str) -> str:
    kw_l = kw.lower()
    for group, kws in KEYWORDS.items():
        if kw_l in [k.lower() for k in kws]:
            return group
    return "Otras"


def _pause(base: float):
    time.sleep(base + random.uniform(0, base * 0.4))


def scrape_search(keyword: str, pause: float = 6.0) -> list[dict]:
    _pause(pause)
    params = {"q": keyword, "gl": "ES", "hl": "es", "num": 10, "pws": 0, "nfpr": 1}
    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=_headers(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        return [{"error": str(e), "keyword": keyword, "type": "search",
                 "scraped_at": datetime.now().isoformat()}]

    if "sorry" in r.url or r.status_code == 429:
        return [{"error": "CAPTCHA", "keyword": keyword, "type": "search",
                 "scraped_at": datetime.now().isoformat()}]

    soup = BeautifulSoup(r.text, "lxml")
    ads, pos = [], 1

    blocks = soup.find_all("div", attrs={"data-text-ad": "1"})
    if not blocks:
        for span in soup.find_all("span", string=re.compile(r"Patrocinado|Sponsored", re.I)):
            p = span.find_parent("div", class_=True)
            if p and p not in blocks:
                blocks.append(p)

    for block in blocks:
        title_el = block.find("div", attrs={"role": "heading"}) or block.find("h3")
        title = title_el.get_text(strip=True) if title_el else ""
        url_el = block.find("cite")
        display_url = url_el.get_text(strip=True) if url_el else ""
        desc_divs = block.find_all(["div", "span"],
                                    class_=re.compile(r"MUxGbd|yDYNvb|VwiC3b"))
        description = " ".join(
            d.get_text(strip=True) for d in desc_divs
            if d.get_text(strip=True) and d.get_text(strip=True) != title
        )[:400]
        link = block.find("a", href=True)
        dest_url = link["href"] if link else ""
        exts = []
        for ext in block.find_all("div", class_=re.compile(r"MhgNwc|OkkX2d")):
            t = ext.get_text(strip=True)
            if t and t not in (title, description):
                exts.append(t[:80])

        brand = _detect_brand(title + display_url, dest_url)
        ads.append({
            "scraped_at":  datetime.now().isoformat(),
            "type":        "search",
            "keyword":     keyword,
            "kw_group":    _kw_group(keyword),
            "position":    pos,
            "brand":       brand,
            "title":       title,
            "description": description,
            "display_url": display_url,
            "dest_url":    dest_url,
            "extensions":  " | ".join(exts[:5]),
            "n_ext":       len(exts),
        })
        pos += 1

    return ads


def scrape_shopping(keyword: str, pause: float = 6.0) -> list[dict]:
    _pause(pause)
    params = {"q": keyword, "tbm": "shop", "gl": "ES", "hl": "es", "pws": 0}
    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=_headers(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        return [{"error": str(e), "keyword": keyword, "type": "shopping",
                 "scraped_at": datetime.now().isoformat()}]

    if "sorry" in r.url or r.status_code == 429:
        return [{"error": "CAPTCHA", "keyword": keyword, "type": "shopping",
                 "scraped_at": datetime.now().isoformat()}]

    soup = BeautifulSoup(r.text, "lxml")
    results, pos = [], 1
    for item in soup.select(".sh-dgr__content, .u30d4, [data-sh-gr]")[:10]:
        title_el = item.select_one("h3, .tAxDx")
        title = title_el.get_text(strip=True) if title_el else ""
        price_el = item.select_one(".a8Pemb, .price")
        price = price_el.get_text(strip=True) if price_el else ""
        seller_el = item.select_one(".aULzUe, .E5ocAb")
        seller = seller_el.get_text(strip=True) if seller_el else ""
        link = item.select_one("a[href]")
        url = link["href"] if link else ""
        img = item.select_one("img")
        img_url = img.get("src", "") if img else ""
        brand = _detect_brand(title + seller, url)
        results.append({
            "scraped_at": datetime.now().isoformat(),
            "type":       "shopping",
            "keyword":    keyword,
            "kw_group":   _kw_group(keyword),
            "position":   pos,
            "brand":      brand,
            "title":      title,
            "price":      price,
            "seller":     seller,
            "dest_url":   url,
            "img_url":    img_url,
        })
        pos += 1
    return results


# ══════════════════════════════════════════════════════════════════════════════
# PERSISTENCIA
# ══════════════════════════════════════════════════════════════════════════════

def save_run(ads: list[dict]) -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(DATA_DIR / f"{run_id}.json", "w", encoding="utf-8") as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    return run_id


def load_all_runs() -> list[dict]:
    if not DATA_DIR.exists():
        return []
    all_ads = []
    for f in sorted(DATA_DIR.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                all_ads.extend(json.load(fh))
        except Exception:
            pass
    return all_ads


def load_latest_run() -> list[dict]:
    if not DATA_DIR.exists():
        return []
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


# ══════════════════════════════════════════════════════════════════════════════
# ÍNDICE DE INTENSIDAD
# ══════════════════════════════════════════════════════════════════════════════

def compute_intensity(ads: list[dict]) -> dict:
    from collections import defaultdict
    bd = defaultdict(lambda: {"keywords": set(), "positions": [], "n_ext": [], "types": set()})
    for ad in ads:
        if "error" in ad:
            continue
        b = ad.get("brand", "Otro")
        bd[b]["keywords"].add(ad.get("keyword", ""))
        if ad.get("position"):
            bd[b]["positions"].append(ad["position"])
        bd[b]["n_ext"].append(ad.get("n_ext", 0))
        bd[b]["types"].add(ad.get("type", ""))

    all_kws = max((len(v["keywords"]) for v in bd.values()), default=1)
    scores = {}
    for brand, d in bd.items():
        n_kws  = len(d["keywords"])
        avg_p  = sum(d["positions"]) / len(d["positions"]) if d["positions"] else 10
        avg_e  = sum(d["n_ext"]) / len(d["n_ext"]) if d["n_ext"] else 0
        n_t    = len(d["types"])
        score  = round(
            (n_kws / max(all_kws, 1)) * 40
            + max(0, (10 - avg_p) / 9) * 30
            + min(avg_e / 5, 1) * 20
            + (n_t / 2) * 10,
            1
        )
        scores[brand] = {
            "score": score,
            "n_keywords": n_kws,
            "avg_position": round(avg_p, 1),
            "avg_extensions": round(avg_e, 1),
            "channels": list(d["types"]),
        }
    return scores


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding:8px 0 20px'>
      <div style='font-size:22px;font-weight:700;color:#f5f5f7;letter-spacing:-0.5px'>📡 AdWatch</div>
      <div style='font-size:12px;color:#636366;margin-top:2px'>Competitive Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["Overview", "Search Ads", "Shopping & PMax", "Raw Data", "⚙️ Scraper"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top:24px'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:11px;color:#636366;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px'>Marcas</div>", unsafe_allow_html=True)
    for brand, cfg in BRANDS.items():
        own = " <span style='font-size:9px;color:#30d158;font-weight:700'>TÚ</span>" if cfg["is_own"] else ""
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>
          <div style='width:8px;height:8px;border-radius:50%;background:{cfg["color"]};flex-shrink:0'></div>
          <span style='font-size:13px;color:#c7c7cc'>{brand}{own}</span>
        </div>
        """, unsafe_allow_html=True)

    all_data = load_all_runs()
    latest   = load_latest_run()
    runs_count = len(list(DATA_DIR.glob("*.json"))) if DATA_DIR.exists() else 0
    last_date = ""
    if latest:
        try:
            last_date = latest[0].get("scraped_at","")[:10]
        except Exception:
            pass

    st.markdown(f"""
    <div style='margin-top:24px;padding:12px;background:#111;border-radius:10px;border:1px solid #222'>
      <div style='font-size:11px;color:#636366;text-transform:uppercase;letter-spacing:0.08em'>Estado</div>
      <div style='font-size:13px;color:#c7c7cc;margin-top:6px'>{runs_count} ejecuciones guardadas</div>
      <div style='font-size:12px;color:#48484a;margin-top:2px'>Última: {last_date or "—"}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "Overview":
    st.markdown("## Overview")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Intensidad de inversión publicitaria · resumen ejecutivo</p>", unsafe_allow_html=True)

    if not latest:
        st.markdown("""
        <div class='aw-card' style='text-align:center;padding:60px 20px'>
          <div style='font-size:40px;margin-bottom:12px'>📡</div>
          <div style='font-size:18px;font-weight:600;margin-bottom:8px'>Sin datos todavía</div>
          <div class='aw-muted'>Ve a la sección ⚙️ Scraper y lanza tu primera ejecución</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    clean = [a for a in latest if "error" not in a]
    search_ads  = [a for a in clean if a.get("type") == "search"]
    shopping_ads = [a for a in clean if a.get("type") == "shopping"]
    n_captcha = sum(1 for a in latest if a.get("error") == "CAPTCHA")

    # Métricas top
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Keywords analizadas", len(set(a.get("keyword","") for a in clean)))
    c2.metric("Anuncios Search", len(search_ads))
    c3.metric("Fichas Shopping", len(shopping_ads))
    c4.metric("Errores CAPTCHA", n_captcha,
              delta="Sube la pausa" if n_captcha > 0 else None,
              delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # Índice de intensidad
    st.markdown("### Índice de intensidad de inversión")
    st.markdown("<p class='aw-muted' style='font-size:12px'>Score 0–100 · cobertura keywords (40%) + posición (30%) + extensiones (20%) + canales (10%)</p>", unsafe_allow_html=True)

    scores = compute_intensity(clean)
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1]["score"])

    cols = st.columns(len(sorted_scores)) if sorted_scores else []
    for i, (brand, data) in enumerate(sorted_scores):
        cfg = BRANDS.get(brand, {})
        color = cfg.get("color", "#636366")
        is_own = cfg.get("is_own", False)
        own_html = "<span style='font-size:10px;color:#30d158;font-weight:700;margin-left:6px'>TÚ</span>" if is_own else ""

        # Score bar
        pct = data["score"]
        bar_html = f"""
        <div style='height:4px;background:#2c2c2e;border-radius:2px;margin:10px 0 14px'>
          <div style='height:4px;width:{pct}%;background:{color};border-radius:2px;transition:width 0.5s'></div>
        </div>"""

        ch_badges = "".join(
            f"<span class='aw-badge aw-badge-{'search' if c == 'search' else 'shopping'}'>{c}</span> "
            for c in data["channels"]
        )

        with cols[i]:
            st.markdown(f"""
            <div class='aw-card'>
              <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>
                <div style='width:10px;height:10px;border-radius:50%;background:{color}'></div>
                <span style='font-size:13px;font-weight:600;color:#c7c7cc'>{brand}{own_html}</span>
              </div>
              <div style='font-size:48px;font-weight:700;color:{color};line-height:1.1;margin-top:8px'>{data["score"]}</div>
              <div style='font-size:11px;color:#48484a'>/ 100 puntos</div>
              {bar_html}
              <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px'>
                <div><div class='aw-label'>Keywords</div><div class='aw-value'>{data["n_keywords"]}</div></div>
                <div><div class='aw-label'>Posición media</div><div class='aw-value'>{data["avg_position"]}</div></div>
                <div><div class='aw-label'>Extensiones</div><div class='aw-value'>{data["avg_extensions"]}</div></div>
                <div><div class='aw-label'>Canales</div><div class='aw-value'>{len(data["channels"])}</div></div>
              </div>
              <div style='display:flex;gap:4px;flex-wrap:wrap'>{ch_badges}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mapa de presencia por keyword
    st.markdown("### Mapa de presencia por keyword")
    if search_ads:
        kw_map = {}
        for ad in search_ads:
            kw = ad.get("keyword", "")
            brand = ad.get("brand", "Otro")
            pos = ad.get("position", 99)
            if kw not in kw_map:
                kw_map[kw] = {}
            if brand not in kw_map[kw] or kw_map[kw][brand] > pos:
                kw_map[kw][brand] = pos

        brand_list = list(BRANDS.keys())
        rows = []
        for kw, bp in kw_map.items():
            row = {"Keyword": kw, "Grupo": _kw_group(kw)}
            for b in brand_list:
                row[b] = f"#{bp[b]}" if b in bp else "—"
            rows.append(row)

        df_map = pd.DataFrame(rows)

        def _style_cell(val):
            if val == "—": return "color:#48484a"
            try:
                p = int(val.replace("#",""))
                if p == 1: return "color:#30d158;font-weight:600"
                if p <= 3: return "color:#ffd60a;font-weight:500"
                return "color:#c7c7cc"
            except: return ""

        styled = df_map.style.applymap(_style_cell, subset=brand_list)
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # Evolución temporal
    if all_data and len(set(a.get("scraped_at","")[:10] for a in all_data if "error" not in a)) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Evolución del score en el tiempo")
        by_date = {}
        for ad in [a for a in all_data if "error" not in a]:
            d = ad.get("scraped_at","")[:10]
            by_date.setdefault(d, []).append(ad)

        rows = []
        for date, ads in sorted(by_date.items()):
            for brand, data in compute_intensity(ads).items():
                rows.append({"Fecha": date, "Marca": brand, "Score": data["score"]})

        if rows:
            df_ev = pd.DataFrame(rows)
            df_piv = df_ev.pivot(index="Fecha", columns="Marca", values="Score").fillna(0)
            st.line_chart(df_piv, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: SEARCH ADS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Search Ads":
    st.markdown("## Search Ads")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Anuncios de texto detectados en Google Search</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    ads = [a for a in all_ads if a.get("type") == "search" and "error" not in a]

    if not ads:
        st.info("Sin datos de Search Ads. Ejecuta el scraper primero.")
        st.stop()

    df = pd.DataFrame(ads)

    # Filtros
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        bf = st.multiselect("Marca", sorted(df["brand"].unique()), default=sorted(df["brand"].unique()))
    with fc2:
        gf = st.multiselect("Grupo keyword", sorted(df["kw_group"].unique()), default=sorted(df["kw_group"].unique()))
    with fc3:
        runs_dates = sorted(df["scraped_at"].str[:10].unique(), reverse=True)
        date_sel = st.selectbox("Fecha", ["Última"] + runs_dates)

    df_f = df[df["brand"].isin(bf) & df["kw_group"].isin(gf)]
    if date_sel == "Última":
        last = df_f["scraped_at"].max()
        df_f = df_f[df_f["scraped_at"] == last]
    else:
        df_f = df_f[df_f["scraped_at"].str[:10] == date_sel]

    st.markdown(f"<p class='aw-muted'>{len(df_f)} anuncios</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Cards
    for _, row in df_f.sort_values(["keyword","position"]).iterrows():
        cfg = BRANDS.get(row["brand"], {})
        color = cfg.get("color", "#636366")
        accent = cfg.get("accent", "blue")
        pos = row.get("position", "?")
        pos_badge = "aw-badge-pos1" if pos == 1 else ("aw-badge-pos3" if pos <= 3 else "aw-badge-search")

        ext_html = ""
        if row.get("extensions"):
            ext_html = f"<div style='background:#111;border-radius:8px;padding:8px 12px;font-size:12px;color:#636366;margin-top:8px'><span style='color:#48484a'>Extensiones: </span>{row['extensions']}</div>"

        st.markdown(f"""
        <div class='aw-card aw-card-{accent}'>
          <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:8px'>
            <div style='display:flex;align-items:center;gap:8px'>
              <div style='width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;margin-top:3px'></div>
              <span style='font-weight:600;font-size:15px;color:#f5f5f7'>{row.get("title","Sin título")}</span>
            </div>
            <div style='display:flex;gap:6px;flex-shrink:0'>
              <span class='aw-badge {pos_badge}'>#{pos}</span>
              <span class='aw-badge' style='background:#1a1a1a;color:#636366'>{row.get("kw_group","")}</span>
            </div>
          </div>
          <div style='color:#0a84ff;font-size:12px;margin-bottom:6px'>{row.get("display_url","")}</div>
          <div style='color:#c7c7cc;font-size:13px;line-height:1.55'>{row.get("description","") or "<em style='color:#48484a'>Sin descripción capturada</em>"}</div>
          {ext_html}
          <div style='display:flex;gap:20px;margin-top:10px'>
            <span><span class='aw-label'>Keyword: </span><span style='font-size:12px;color:#c7c7cc'>{row.get("keyword","")}</span></span>
            <span><span class='aw-label'>Fecha: </span><span style='font-size:12px;color:#48484a'>{row.get("scraped_at","")[:16]}</span></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Exportar datos"):
        cols_show = ["scraped_at","keyword","kw_group","brand","position","title","description","display_url","extensions"]
        cols_show = [c for c in cols_show if c in df_f.columns]
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)
        st.download_button("⬇️ Descargar CSV", df_f.to_csv(index=False, encoding="utf-8-sig"),
                           "search_ads.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: SHOPPING & PMAX
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Shopping & PMax":
    st.markdown("## Shopping & PMax")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Fichas de producto detectadas en Google Shopping</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    ads = [a for a in all_ads if a.get("type") == "shopping" and "error" not in a]

    if not ads:
        st.info("Sin datos de Shopping. Ejecuta el scraper primero.")
        st.stop()

    df = pd.DataFrame(ads)

    fc1, fc2 = st.columns(2)
    with fc1:
        bf = st.multiselect("Marca", sorted(df["brand"].unique()), default=sorted(df["brand"].unique()))
    with fc2:
        kf = st.multiselect("Keyword", sorted(df["keyword"].unique()), default=sorted(df["keyword"].unique()))

    df_f = df[df["brand"].isin(bf) & df["keyword"].isin(kf)]

    cols = st.columns(3)
    for i, (_, row) in enumerate(df_f.iterrows()):
        cfg = BRANDS.get(row.get("brand",""), {})
        color = cfg.get("color", "#636366")
        img_html = (f"<img src='{row['img_url']}' style='width:100%;height:110px;object-fit:contain;border-radius:8px;margin-bottom:10px'>"
                    if row.get("img_url")
                    else "<div style='height:80px;background:#2c2c2e;border-radius:8px;margin-bottom:10px;display:flex;align-items:center;justify-content:center;color:#48484a;font-size:11px'>Sin imagen</div>")
        with cols[i % 3]:
            st.markdown(f"""
            <div class='aw-card' style='border-top:2px solid {color}'>
              {img_html}
              <div style='font-size:13px;font-weight:600;color:#f5f5f7;margin-bottom:4px'>{str(row.get("title",""))[:60]}</div>
              <div style='font-size:17px;font-weight:700;color:{color};margin-bottom:6px'>{row.get("price","")}</div>
              <div style='font-size:11px;color:#636366'>{row.get("seller","")}</div>
              <div style='font-size:11px;color:#48484a;margin-top:6px'>#{row.get("position","")} · {row.get("keyword","")}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 Exportar datos"):
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Descargar CSV", df_f.to_csv(index=False, encoding="utf-8-sig"),
                           "shopping.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: RAW DATA
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Raw Data":
    st.markdown("## Raw Data")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Todos los datos en crudo · filtra y exporta</p>", unsafe_allow_html=True)

    all_ads = load_all_runs()
    if not all_ads:
        st.info("Sin datos. Ejecuta el scraper primero.")
        st.stop()

    df = pd.DataFrame(all_ads)

    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        tf = st.multiselect("Tipo", sorted(df["type"].unique()) if "type" in df else [], default=sorted(df["type"].unique()) if "type" in df else [])
    with fc2:
        bf = st.multiselect("Marca", sorted(df["brand"].dropna().unique()) if "brand" in df else [], default=sorted(df["brand"].dropna().unique()) if "brand" in df else [])
    with fc3:
        show_err = st.checkbox("Incluir errores", False)

    df_f = df.copy()
    if tf and "type" in df_f:    df_f = df_f[df_f["type"].isin(tf)]
    if bf and "brand" in df_f:   df_f = df_f[df_f["brand"].isin(bf)]
    if not show_err and "error" in df_f.columns:
        df_f = df_f[df_f["error"].isna()]

    st.markdown(f"<p class='aw-muted'>{len(df_f)} registros</p>", unsafe_allow_html=True)
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Descargar todo en CSV",
                       df_f.to_csv(index=False, encoding="utf-8-sig"),
                       "adwatch_raw.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA: SCRAPER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "⚙️ Scraper":
    st.markdown("## ⚙️ Ejecutar Scraper")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Lanza una nueva recopilación de datos de la competencia</p>", unsafe_allow_html=True)

    st.markdown("""
    <div class='aw-card' style='background:#0a1f0a;border-color:#1a3a1a;margin-bottom:20px'>
      <div style='font-size:13px;color:#30d158;font-weight:500;margin-bottom:4px'>ℹ️ Sobre los CAPTCHAs</div>
      <div style='font-size:12px;color:#c7c7cc;line-height:1.6'>
        Streamlit Cloud usa IPs de servidor que Google puede bloquear. Si recibes errores CAPTCHA,
        <b>sube la pausa a 10–12s</b> o ejecuta el scraper desde tu ordenador local clonando el repo.
        Los datos se guardan localmente en <code>data/runs/</code>.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Configuración
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Canales**")
        do_search   = st.checkbox("Search Ads (texto)", value=True)
        do_shopping = st.checkbox("Shopping / PMax", value=True)

    with col2:
        st.markdown("**Grupos de keywords**")
        sel_groups = {}
        for group in KEYWORDS:
            sel_groups[group] = st.checkbox(group, value=True)

    pausa = st.slider("Pausa entre peticiones (segundos)", 4, 15, 7,
                      help="Mínimo recomendado: 6s. Sube a 10-12s si hay CAPTCHAs.")

    # Keywords seleccionadas
    kws = []
    for group, selected in sel_groups.items():
        if selected:
            kws += KEYWORDS[group]
    kws = list(dict.fromkeys(kws))

    n_calls = len(kws) * ((1 if do_search else 0) + (1 if do_shopping else 0))
    est_min = round(n_calls * pausa / 60, 1)

    st.markdown(f"""
    <div style='display:flex;gap:24px;margin:12px 0 20px;flex-wrap:wrap'>
      <div><span class='aw-label'>Keywords</span><br><span class='aw-value'>{len(kws)}</span></div>
      <div><span class='aw-label'>Peticiones totales</span><br><span class='aw-value'>{n_calls}</span></div>
      <div><span class='aw-label'>Tiempo estimado</span><br><span class='aw-value'>~{est_min} min</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Iniciar scraping"):
        if not kws:
            st.error("Selecciona al menos un grupo de keywords.")
            st.stop()
        if not do_search and not do_shopping:
            st.error("Selecciona al menos un canal.")
            st.stop()

        results, errors = [], []
        progress = st.progress(0, text="Preparando...")
        log_box  = st.empty()
        total_steps = n_calls
        step = 0

        for i, kw in enumerate(kws):
            if do_search:
                log_box.markdown(f"<span class='aw-muted'>🔍 Search · <b style='color:#f5f5f7'>{kw}</b></span>", unsafe_allow_html=True)
                res = scrape_search(kw, pause=pausa)
                good = [a for a in res if "error" not in a]
                bad  = [a for a in res if "error" in a]
                results.extend(good); errors.extend(bad)
                step += 1
                progress.progress(step / total_steps, text=f"Search {i+1}/{len(kws)}")

            if do_shopping:
                log_box.markdown(f"<span class='aw-muted'>🛒 Shopping · <b style='color:#f5f5f7'>{kw}</b></span>", unsafe_allow_html=True)
                res = scrape_shopping(kw, pause=pausa)
                good = [a for a in res if "error" not in a]
                bad  = [a for a in res if "error" in a]
                results.extend(good); errors.extend(bad)
                step += 1
                progress.progress(step / total_steps, text=f"Shopping {i+1}/{len(kws)}")

        progress.progress(1.0, text="✅ Completado")
        log_box.empty()

        if results:
            run_id = save_run(results)
            st.success(f"✅ {len(results)} anuncios guardados · run `{run_id}`")
        else:
            st.warning("No se encontraron anuncios. Prueba a aumentar la pausa.")

        n_cap = sum(1 for e in errors if e.get("error") == "CAPTCHA")
        if n_cap:
            st.warning(f"⚠️ {n_cap} keywords bloqueadas por CAPTCHA. Sube la pausa e inténtalo de nuevo.")

        if results:
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Search",   sum(1 for a in results if a.get("type") == "search"))
            rc2.metric("Shopping", sum(1 for a in results if a.get("type") == "shopping"))
            rc3.metric("Errores",  len(errors))
            st.markdown("<p class='aw-muted' style='margin-top:8px'>Ve al <b>Overview</b> para ver los resultados.</p>", unsafe_allow_html=True)

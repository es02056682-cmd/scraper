import streamlit as st
import requests
import time
import random
import re
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="AdWatch",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS como string simple (sin f-string ni triple comilla con llaves)
CSS = (
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');"
    "html,body,[class*='css']{"
    "font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;"
    "background-color:#000;color:#f5f5f7;}"
    ".main{background:#000;}"
    ".block-container{padding:2rem 2rem 4rem;max-width:1200px;}"
    "[data-testid='stSidebar']{background:#111!important;border-right:1px solid #222;}"
    "[data-testid='stSidebar']>div{background:#111;}"
    "[data-testid='metric-container']{"
    "background:#1c1c1e;border:1px solid #2c2c2e;border-radius:16px;padding:20px 24px!important;}"
    "[data-testid='metric-container'] label{"
    "color:#636366!important;font-size:11px!important;font-weight:500!important;"
    "text-transform:uppercase;letter-spacing:0.08em;}"
    "[data-testid='metric-container'] [data-testid='stMetricValue']{"
    "color:#f5f5f7!important;font-size:26px!important;font-weight:600!important;}"
    ".stTabs [data-baseweb='tab-list']{"
    "background:#1c1c1e;border-radius:12px;padding:4px;gap:2px;border:1px solid #2c2c2e;}"
    ".stTabs [data-baseweb='tab']{"
    "border-radius:8px;color:#636366!important;font-weight:500;font-size:13px;padding:6px 16px;}"
    ".stTabs [aria-selected='true']{background:#2c2c2e!important;color:#f5f5f7!important;}"
    ".stButton>button{"
    "background:#0a84ff!important;color:white!important;border:none!important;"
    "border-radius:10px!important;font-weight:500!important;font-size:14px!important;"
    "padding:10px 24px!important;transition:all 0.2s!important;width:100%;}"
    ".stButton>button:hover{background:#0071e3!important;}"
    "[data-testid='stCheckbox'] label{color:#c7c7cc!important;font-size:14px!important;}"
    "[data-testid='stExpander']{"
    "background:#1c1c1e;border:1px solid #2c2c2e!important;border-radius:12px!important;}"
    "[data-testid='stExpander'] summary{color:#c7c7cc!important;}"
    "[data-testid='stProgressBar']>div>div{background:#0a84ff!important;border-radius:4px;}"
    "#MainMenu,footer,header{visibility:hidden;}"
    ".aw-card{"
    "background:#1c1c1e;border:1px solid #2c2c2e;border-radius:16px;padding:20px 24px;margin-bottom:12px;}"
    ".aw-card-blue{border-left:3px solid #0a84ff;}"
    ".aw-card-red{border-left:3px solid #ff453a;}"
    ".aw-card-amber{border-left:3px solid #ff9f0a;}"
    ".aw-badge{"
    "display:inline-block;padding:3px 10px;border-radius:20px;"
    "font-size:11px;font-weight:600;letter-spacing:0.04em;}"
    ".aw-badge-search{background:#0a1f3a;color:#0a84ff;}"
    ".aw-badge-shopping{background:#1a0a3a;color:#bf5af2;}"
    ".aw-badge-pos1{background:#0a3a1a;color:#30d158;}"
    ".aw-badge-pos3{background:#2a2a00;color:#ffd60a;}"
    ".aw-label{"
    "font-size:11px;font-weight:500;color:#636366;"
    "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:3px;}"
    ".aw-value{font-size:14px;font-weight:500;color:#f5f5f7;}"
    ".aw-muted{color:#636366;font-size:13px;}"
    "</style>"
)
st.markdown(CSS, unsafe_allow_html=True)


# ── Configuracion ─────────────────────────────────────────────────────────────

BRANDS = {
    "Movistar Alarmas": {
        "color": "#0a84ff", "accent": "blue",
        "domains": ["movistar.es", "alarmas.movistar"],
        "keywords_brand": ["movistar alarmas", "alarmas movistar"],
        "is_own": True,
    },
    "Securitas Direct": {
        "color": "#ff453a", "accent": "red",
        "domains": ["securitasdirect.es", "securitas-direct"],
        "keywords_brand": ["securitas direct", "securitas alarmas"],
        "is_own": False,
    },
    "Verisure": {
        "color": "#ff9f0a", "accent": "amber",
        "domains": ["verisure.es", "verisure.com"],
        "keywords_brand": ["verisure", "verisure alarmas"],
        "is_own": False,
    },
}

KEYWORDS = {
    "Genericas": [
        "alarmas hogar", "seguridad hogar", "alarma casa",
        "sistema de alarma", "alarma para casa",
    ],
    "Intencion de compra": [
        "instalar alarma en casa", "precio alarma hogar",
        "contratar alarma hogar", "mejor alarma hogar", "oferta alarma hogar",
    ],
    "Marca competencia": [
        "securitas direct", "securitas direct precio", "securitas direct opiniones",
        "verisure", "verisure precio", "verisure opiniones",
    ],
    "Marca propia": [
        "movistar alarmas", "alarmas movistar precio",
    ],
}

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

DATA_DIR = Path("data/runs")


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
    }


def detect_brand(text, url):
    combined = (text + " " + url).lower()
    for brand, cfg in BRANDS.items():
        if any(d.lower() in combined for d in cfg["domains"]):
            return brand
        if any(k.lower() in combined for k in cfg["keywords_brand"]):
            return brand
    return "Otro"


def get_kw_group(kw):
    kw_l = kw.lower()
    for group, kws in KEYWORDS.items():
        if kw_l in [k.lower() for k in kws]:
            return group
    return "Otras"


def do_pause(base=6.0):
    time.sleep(base + random.uniform(0, base * 0.4))


# ── Scrapers ──────────────────────────────────────────────────────────────────

def scrape_search(keyword, pause=6.0):
    do_pause(pause)
    params = {"q": keyword, "gl": "ES", "hl": "es", "num": 10, "pws": 0, "nfpr": 1}
    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=get_headers(), timeout=15)
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
        desc_divs = block.find_all(["div", "span"], class_=re.compile(r"MUxGbd|yDYNvb|VwiC3b"))
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
        ads.append({
            "scraped_at": datetime.now().isoformat(),
            "type": "search", "keyword": keyword,
            "kw_group": get_kw_group(keyword), "position": pos,
            "brand": detect_brand(title + display_url, dest_url),
            "title": title, "description": description,
            "display_url": display_url, "dest_url": dest_url,
            "extensions": " | ".join(exts[:5]), "n_ext": len(exts),
        })
        pos += 1
    return ads


def scrape_shopping(keyword, pause=6.0):
    do_pause(pause)
    params = {"q": keyword, "tbm": "shop", "gl": "ES", "hl": "es", "pws": 0}
    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=get_headers(), timeout=15)
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
        results.append({
            "scraped_at": datetime.now().isoformat(),
            "type": "shopping", "keyword": keyword,
            "kw_group": get_kw_group(keyword), "position": pos,
            "brand": detect_brand(title + seller, url),
            "title": title, "price": price, "seller": seller,
            "dest_url": url, "img_url": img_url,
        })
        pos += 1
    return results


# ── Persistencia ──────────────────────────────────────────────────────────────

def save_run(ads):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(DATA_DIR / (run_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    return run_id


def load_all_runs():
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


def load_latest_run():
    if not DATA_DIR.exists():
        return []
    files = sorted(DATA_DIR.glob("*.json"))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)


# ── Indice de intensidad ──────────────────────────────────────────────────────

def compute_intensity(ads):
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
        n_kws = len(d["keywords"])
        avg_p = sum(d["positions"]) / len(d["positions"]) if d["positions"] else 10
        avg_e = sum(d["n_ext"]) / len(d["n_ext"]) if d["n_ext"] else 0
        n_t = len(d["types"])
        score = round(
            (n_kws / max(all_kws, 1)) * 40
            + max(0, (10 - avg_p) / 9) * 30
            + min(avg_e / 5, 1) * 20
            + (n_t / 2) * 10, 1
        )
        scores[brand] = {
            "score": score, "n_keywords": n_kws,
            "avg_position": round(avg_p, 1),
            "avg_extensions": round(avg_e, 1),
            "channels": list(d["types"]),
        }
    return scores


# ── Carga de datos ────────────────────────────────────────────────────────────

all_data = load_all_runs()
latest   = load_latest_run()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        "<div style='padding:8px 0 20px'>"
        "<div style='font-size:22px;font-weight:700;color:#f5f5f7'>AdWatch</div>"
        "<div style='font-size:12px;color:#636366;margin-top:2px'>Competitive Intelligence</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    page = st.radio("nav", ["Overview", "Search Ads", "Shopping", "Raw Data", "Scraper"],
                    label_visibility="collapsed")

    st.markdown(
        "<div style='margin-top:20px;font-size:11px;color:#636366;"
        "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px'>Marcas</div>",
        unsafe_allow_html=True,
    )
    for brand, cfg in BRANDS.items():
        own = " <span style='font-size:9px;color:#30d158;font-weight:700'>TU</span>" if cfg["is_own"] else ""
        st.markdown(
            "<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>"
            "<div style='width:8px;height:8px;border-radius:50%;background:" + cfg["color"] + "'></div>"
            "<span style='font-size:13px;color:#c7c7cc'>" + brand + own + "</span></div>",
            unsafe_allow_html=True,
        )

    runs_count  = len(list(DATA_DIR.glob("*.json"))) if DATA_DIR.exists() else 0
    latest_date = latest[0].get("scraped_at", "")[:10] if latest else "-"
    st.markdown(
        "<div style='margin-top:20px;padding:12px;background:#111;border-radius:10px;border:1px solid #222'>"
        "<div style='font-size:11px;color:#636366;text-transform:uppercase;letter-spacing:0.08em'>Estado</div>"
        "<div style='font-size:13px;color:#c7c7cc;margin-top:6px'>" + str(runs_count) + " ejecuciones</div>"
        "<div style='font-size:12px;color:#48484a;margin-top:2px'>Ultima: " + latest_date + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "Overview":
    st.markdown("## Overview")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Intensidad de inversion publicitaria</p>",
                unsafe_allow_html=True)

    if not latest:
        st.markdown(
            "<div class='aw-card' style='text-align:center;padding:60px 20px'>"
            "<div style='font-size:40px;margin-bottom:12px'>📡</div>"
            "<div style='font-size:18px;font-weight:600;margin-bottom:8px'>Sin datos todavia</div>"
            "<div class='aw-muted'>Ve a la seccion Scraper y lanza tu primera ejecucion</div>"
            "</div>", unsafe_allow_html=True,
        )
        st.stop()

    clean        = [a for a in latest if "error" not in a]
    search_ads   = [a for a in clean if a.get("type") == "search"]
    shopping_ads = [a for a in clean if a.get("type") == "shopping"]
    n_captcha    = sum(1 for a in latest if a.get("error") == "CAPTCHA")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Keywords", len(set(a.get("keyword", "") for a in clean)))
    c2.metric("Search Ads", len(search_ads))
    c3.metric("Shopping", len(shopping_ads))
    c4.metric("CAPTCHAs", n_captcha,
              delta="Sube la pausa" if n_captcha > 0 else None,
              delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Indice de intensidad")
    st.markdown(
        "<p class='aw-muted' style='font-size:12px'>"
        "Score 0-100: cobertura keywords (40%) + posicion (30%) + extensiones (20%) + canales (10%)"
        "</p>", unsafe_allow_html=True,
    )

    scores = compute_intensity(clean)
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1]["score"])
    cols = st.columns(max(len(sorted_scores), 1))

    for i, (brand, data) in enumerate(sorted_scores):
        cfg    = BRANDS.get(brand, {})
        color  = cfg.get("color", "#636366")
        is_own = cfg.get("is_own", False)
        own_html = "<span style='font-size:10px;color:#30d158;font-weight:700;margin-left:6px'>TU</span>" if is_own else ""
        pct = data["score"]
        ch_badges = "".join(
            "<span class='aw-badge aw-badge-" + ("search" if c == "search" else "shopping") + "'>"
            + c + "</span> " for c in data["channels"]
        )
        with cols[i]:
            st.markdown(
                "<div class='aw-card'>"
                "<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
                "<div style='width:10px;height:10px;border-radius:50%;background:" + color + "'></div>"
                "<span style='font-size:13px;font-weight:600;color:#c7c7cc'>" + brand + own_html + "</span>"
                "</div>"
                "<div style='font-size:48px;font-weight:700;color:" + color + ";line-height:1.1;margin-top:8px'>"
                + str(data["score"]) + "</div>"
                "<div style='font-size:11px;color:#48484a'>/ 100 puntos</div>"
                "<div style='height:4px;background:#2c2c2e;border-radius:2px;margin:10px 0 14px'>"
                "<div style='height:4px;width:" + str(pct) + "%;background:" + color + ";border-radius:2px'></div>"
                "</div>"
                "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px'>"
                "<div><div class='aw-label'>Keywords</div><div class='aw-value'>" + str(data["n_keywords"]) + "</div></div>"
                "<div><div class='aw-label'>Posicion media</div><div class='aw-value'>" + str(data["avg_position"]) + "</div></div>"
                "<div><div class='aw-label'>Extensiones</div><div class='aw-value'>" + str(data["avg_extensions"]) + "</div></div>"
                "<div><div class='aw-label'>Canales</div><div class='aw-value'>" + str(len(data["channels"])) + "</div></div>"
                "</div>"
                "<div style='display:flex;gap:4px;flex-wrap:wrap'>" + ch_badges + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Mapa de presencia por keyword")

    if search_ads:
        kw_map = {}
        for ad in search_ads:
            kw    = ad.get("keyword", "")
            brand = ad.get("brand", "Otro")
            pos   = ad.get("position", 99)
            kw_map.setdefault(kw, {})
            if brand not in kw_map[kw] or kw_map[kw][brand] > pos:
                kw_map[kw][brand] = pos

        brand_list = list(BRANDS.keys())
        rows = []
        for kw, bp in kw_map.items():
            row = {"Keyword": kw, "Grupo": get_kw_group(kw)}
            for b in brand_list:
                row[b] = "#" + str(bp[b]) if b in bp else "-"
            rows.append(row)

        df_map = pd.DataFrame(rows)

        def style_cell(val):
            if val == "-":
                return "color:#48484a"
            try:
                p = int(str(val).replace("#", ""))
                if p == 1:
                    return "color:#30d158;font-weight:600"
                if p <= 3:
                    return "color:#ffd60a;font-weight:500"
            except Exception:
                pass
            return "color:#c7c7cc"

        styled = df_map.style.applymap(style_cell, subset=brand_list)
        st.dataframe(styled, use_container_width=True, hide_index=True)

    if all_data and len(set(a.get("scraped_at", "")[:10] for a in all_data if "error" not in a)) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Evolucion del score")
        by_date = {}
        for ad in [a for a in all_data if "error" not in a]:
            d = ad.get("scraped_at", "")[:10]
            by_date.setdefault(d, []).append(ad)
        chart_rows = []
        for date, ads in sorted(by_date.items()):
            for brand, data in compute_intensity(ads).items():
                chart_rows.append({"Fecha": date, "Marca": brand, "Score": data["score"]})
        if chart_rows:
            df_ev  = pd.DataFrame(chart_rows)
            df_piv = df_ev.pivot(index="Fecha", columns="Marca", values="Score").fillna(0)
            st.line_chart(df_piv, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SEARCH ADS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Search Ads":
    st.markdown("## Search Ads")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Anuncios de texto detectados en Google Search</p>",
                unsafe_allow_html=True)

    ads = [a for a in all_data if a.get("type") == "search" and "error" not in a]
    if not ads:
        st.info("Sin datos. Ejecuta el scraper primero.")
        st.stop()

    df = pd.DataFrame(ads)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        bf = st.multiselect("Marca", sorted(df["brand"].unique()), default=sorted(df["brand"].unique()))
    with fc2:
        gf = st.multiselect("Grupo", sorted(df["kw_group"].unique()), default=sorted(df["kw_group"].unique()))
    with fc3:
        dates = sorted(df["scraped_at"].str[:10].unique(), reverse=True)
        date_sel = st.selectbox("Fecha", ["Ultima"] + list(dates))

    df_f = df[df["brand"].isin(bf) & df["kw_group"].isin(gf)]
    if date_sel == "Ultima":
        df_f = df_f[df_f["scraped_at"] == df_f["scraped_at"].max()]
    else:
        df_f = df_f[df_f["scraped_at"].str[:10] == date_sel]

    st.markdown("<p class='aw-muted'>" + str(len(df_f)) + " anuncios</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    for _, row in df_f.sort_values(["keyword", "position"]).iterrows():
        cfg    = BRANDS.get(str(row.get("brand", "")), {})
        color  = cfg.get("color", "#636366")
        accent = cfg.get("accent", "blue")
        pos    = row.get("position", "?")
        try:
            pos_int = int(pos)
            pos_class = "aw-badge-pos1" if pos_int == 1 else ("aw-badge-pos3" if pos_int <= 3 else "aw-badge-search")
        except Exception:
            pos_class = "aw-badge-search"

        ext_html = ""
        if row.get("extensions"):
            ext_html = (
                "<div style='background:#111;border-radius:8px;padding:8px 12px;"
                "font-size:12px;color:#636366;margin-top:8px'>"
                "<span style='color:#48484a'>Extensiones: </span>"
                + str(row["extensions"]) + "</div>"
            )

        desc = str(row.get("description", "")) or "<em style='color:#48484a'>Sin descripcion</em>"
        st.markdown(
            "<div class='aw-card aw-card-" + accent + "'>"
            "<div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:8px'>"
            "<div style='display:flex;align-items:center;gap:8px'>"
            "<div style='width:8px;height:8px;border-radius:50%;background:" + color + ";flex-shrink:0;margin-top:3px'></div>"
            "<span style='font-weight:600;font-size:15px;color:#f5f5f7'>" + str(row.get("title", "Sin titulo")) + "</span>"
            "</div>"
            "<div style='display:flex;gap:6px;flex-shrink:0'>"
            "<span class='aw-badge " + pos_class + "'>#" + str(pos) + "</span>"
            "<span class='aw-badge' style='background:#1a1a1a;color:#636366'>" + str(row.get("kw_group", "")) + "</span>"
            "</div></div>"
            "<div style='color:#0a84ff;font-size:12px;margin-bottom:6px'>" + str(row.get("display_url", "")) + "</div>"
            "<div style='color:#c7c7cc;font-size:13px;line-height:1.55'>" + desc + "</div>"
            + ext_html +
            "<div style='display:flex;gap:20px;margin-top:10px'>"
            "<span><span class='aw-label'>Keyword: </span>"
            "<span style='font-size:12px;color:#c7c7cc'>" + str(row.get("keyword", "")) + "</span></span>"
            "<span><span class='aw-label'>Fecha: </span>"
            "<span style='font-size:12px;color:#48484a'>" + str(row.get("scraped_at", ""))[:16] + "</span></span>"
            "</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Exportar"):
        cols_show = ["scraped_at", "keyword", "kw_group", "brand", "position",
                     "title", "description", "display_url", "extensions"]
        cols_show = [c for c in cols_show if c in df_f.columns]
        st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)
        st.download_button("Descargar CSV",
                           df_f.to_csv(index=False, encoding="utf-8-sig"),
                           "search_ads.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# SHOPPING
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Shopping":
    st.markdown("## Shopping & PMax")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Fichas en Google Shopping</p>",
                unsafe_allow_html=True)

    ads = [a for a in all_data if a.get("type") == "shopping" and "error" not in a]
    if not ads:
        st.info("Sin datos. Ejecuta el scraper primero.")
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
        cfg   = BRANDS.get(str(row.get("brand", "")), {})
        color = cfg.get("color", "#636366")
        img_html = (
            "<img src='" + str(row["img_url"]) + "' style='width:100%;height:110px;object-fit:contain;border-radius:8px;margin-bottom:10px'>"
            if row.get("img_url")
            else "<div style='height:80px;background:#2c2c2e;border-radius:8px;margin-bottom:10px;display:flex;align-items:center;justify-content:center;color:#48484a;font-size:11px'>Sin imagen</div>"
        )
        with cols[i % 3]:
            st.markdown(
                "<div class='aw-card' style='border-top:2px solid " + color + "'>"
                + img_html +
                "<div style='font-size:13px;font-weight:600;color:#f5f5f7;margin-bottom:4px'>"
                + str(row.get("title", ""))[:60] + "</div>"
                "<div style='font-size:17px;font-weight:700;color:" + color + ";margin-bottom:6px'>"
                + str(row.get("price", "")) + "</div>"
                "<div style='font-size:11px;color:#636366'>" + str(row.get("seller", "")) + "</div>"
                "<div style='font-size:11px;color:#48484a;margin-top:6px'>#"
                + str(row.get("position", "")) + " - " + str(row.get("keyword", "")) + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    with st.expander("Exportar"):
        st.dataframe(df_f, use_container_width=True, hide_index=True)
        st.download_button("Descargar CSV",
                           df_f.to_csv(index=False, encoding="utf-8-sig"),
                           "shopping.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# RAW DATA
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Raw Data":
    st.markdown("## Raw Data")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Todos los registros</p>",
                unsafe_allow_html=True)

    if not all_data:
        st.info("Sin datos. Ejecuta el scraper primero.")
        st.stop()

    df = pd.DataFrame(all_data)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        tf = st.multiselect("Tipo",
                            sorted(df["type"].unique()) if "type" in df.columns else [],
                            default=sorted(df["type"].unique()) if "type" in df.columns else [])
    with fc2:
        bf = st.multiselect("Marca",
                            sorted(df["brand"].dropna().unique()) if "brand" in df.columns else [],
                            default=sorted(df["brand"].dropna().unique()) if "brand" in df.columns else [])
    with fc3:
        show_err = st.checkbox("Incluir errores", False)

    df_f = df.copy()
    if tf and "type" in df_f.columns:
        df_f = df_f[df_f["type"].isin(tf)]
    if bf and "brand" in df_f.columns:
        df_f = df_f[df_f["brand"].isin(bf)]
    if not show_err and "error" in df_f.columns:
        df_f = df_f[df_f["error"].isna()]

    st.markdown("<p class='aw-muted'>" + str(len(df_f)) + " registros</p>",
                unsafe_allow_html=True)
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    st.download_button("Descargar CSV",
                       df_f.to_csv(index=False, encoding="utf-8-sig"),
                       "adwatch_raw.csv", "text/csv")


# ══════════════════════════════════════════════════════════════════════════════
# SCRAPER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Scraper":
    st.markdown("## Scraper")
    st.markdown("<p class='aw-muted' style='margin-top:-10px'>Lanza una nueva recopilacion de datos</p>",
                unsafe_allow_html=True)

    st.markdown(
        "<div class='aw-card' style='background:#0a1f0a;border-color:#1a3a1a;margin-bottom:20px'>"
        "<div style='font-size:13px;color:#30d158;font-weight:500;margin-bottom:4px'>Sobre los CAPTCHAs</div>"
        "<div style='font-size:12px;color:#c7c7cc;line-height:1.6'>"
        "Streamlit Cloud usa IPs de servidor que Google puede bloquear. "
        "Si recibes CAPTCHAs, sube la pausa a 10-12s o ejecuta desde tu ordenador local."
        "</div></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Canales**")
        do_search   = st.checkbox("Search Ads", value=True)
        do_shopping = st.checkbox("Shopping / PMax", value=True)
    with col2:
        st.markdown("**Keywords**")
        sel_groups = {}
        for group in KEYWORDS:
            sel_groups[group] = st.checkbox(group, value=True)

    pausa = st.slider("Pausa entre peticiones (segundos)", 4, 15, 7)

    kws = []
    for group, selected in sel_groups.items():
        if selected:
            kws += KEYWORDS[group]
    kws = list(dict.fromkeys(kws))

    n_calls = len(kws) * ((1 if do_search else 0) + (1 if do_shopping else 0))
    est_min = round(n_calls * pausa / 60, 1)

    st.markdown(
        "<div style='display:flex;gap:24px;margin:12px 0 20px;flex-wrap:wrap'>"
        "<div><div class='aw-label'>Keywords</div><div class='aw-value'>" + str(len(kws)) + "</div></div>"
        "<div><div class='aw-label'>Peticiones</div><div class='aw-value'>" + str(n_calls) + "</div></div>"
        "<div><div class='aw-label'>Tiempo estimado</div><div class='aw-value'>~" + str(est_min) + " min</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("Iniciar scraping"):
        if not kws or (not do_search and not do_shopping):
            st.error("Selecciona al menos un canal y un grupo de keywords.")
            st.stop()

        results, errors = [], []
        total_steps = max(n_calls, 1)
        progress = st.progress(0, text="Preparando...")
        log_box  = st.empty()
        step = 0

        for i, kw in enumerate(kws):
            if do_search:
                log_box.markdown(
                    "<span class='aw-muted'>Search: <b style='color:#f5f5f7'>" + kw + "</b></span>",
                    unsafe_allow_html=True,
                )
                res  = scrape_search(kw, pause=pausa)
                results.extend(a for a in res if "error" not in a)
                errors.extend(a for a in res if "error" in a)
                step += 1
                progress.progress(step / total_steps, text="Search " + str(i + 1) + "/" + str(len(kws)))

            if do_shopping:
                log_box.markdown(
                    "<span class='aw-muted'>Shopping: <b style='color:#f5f5f7'>" + kw + "</b></span>",
                    unsafe_allow_html=True,
                )
                res  = scrape_shopping(kw, pause=pausa)
                results.extend(a for a in res if "error" not in a)
                errors.extend(a for a in res if "error" in a)
                step += 1
                progress.progress(step / total_steps, text="Shopping " + str(i + 1) + "/" + str(len(kws)))

        progress.progress(1.0, text="Completado")
        log_box.empty()

        if results:
            run_id = save_run(results)
            st.success(str(len(results)) + " anuncios guardados - run: " + run_id)
        else:
            st.warning("No se encontraron anuncios. Prueba a aumentar la pausa.")

        n_cap = sum(1 for e in errors if e.get("error") == "CAPTCHA")
        if n_cap:
            st.warning(str(n_cap) + " keywords bloqueadas por CAPTCHA. Sube la pausa e intentalo de nuevo.")

        if results:
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Search",   sum(1 for a in results if a.get("type") == "search"))
            rc2.metric("Shopping", sum(1 for a in results if a.get("type") == "shopping"))
            rc3.metric("Errores",  len(errors))
            st.markdown("<p class='aw-muted' style='margin-top:8px'>Ve al Overview para ver los resultados.</p>",
                        unsafe_allow_html=True)

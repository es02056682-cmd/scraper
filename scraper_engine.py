"""
scraper_engine.py — Motor de scraping multi-canal
==================================================
Extrae anuncios de Google Search, Shopping y Ad Transparency Center.
Sin API de pago. Usa requests + BeautifulSoup.
"""

import requests
import time
import random
import re
import json
import hashlib
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional

# ── Configuración de marcas ────────────────────────────────────────────────────

BRANDS = {
    "Movistar Alarmas": {
        "color": "#0a84ff",
        "domains": ["movistar.es", "alarmas.movistar"],
        "keywords_brand": ["movistar alarmas", "alarmas movistar"],
        "is_own": True,
    },
    "Securitas Direct": {
        "color": "#ff453a",
        "domains": ["securitasdirect.es", "securitas-direct"],
        "keywords_brand": ["securitas direct", "securitas alarmas"],
        "is_own": False,
    },
    "Verisure": {
        "color": "#ff9f0a",
        "domains": ["verisure.es", "verisure.com"],
        "keywords_brand": ["verisure", "verisure alarmas"],
        "is_own": False,
    },
}

KEYWORDS = {
    "genericas": [
        "alarmas hogar",
        "seguridad hogar",
        "alarma casa",
        "sistema de alarma",
        "alarma para casa",
    ],
    "intencion": [
        "instalar alarma en casa",
        "precio alarma hogar",
        "contratar alarma hogar",
        "mejor alarma hogar",
        "alarma hogar precio",
        "oferta alarma hogar",
    ],
    "marca_competencia": [
        "securitas direct",
        "securitas direct precio",
        "securitas direct opiniones",
        "verisure",
        "verisure precio",
        "verisure opiniones",
    ],
    "marca_propia": [
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


def _headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def _detect_brand(text: str, url: str) -> Optional[str]:
    """Detecta a qué marca pertenece un anuncio."""
    combined = (text + " " + url).lower()
    for brand, cfg in BRANDS.items():
        if any(d.lower() in combined for d in cfg["domains"]):
            return brand
        if any(kw.lower() in combined for kw in cfg["keywords_brand"]):
            return brand
    return None


def _pause(base: float = 5.0):
    time.sleep(base + random.uniform(0, base * 0.5))


# ── Search Ads ─────────────────────────────────────────────────────────────────

def scrape_search_ads(keyword: str, pause: float = 5.0) -> list[dict]:
    """Extrae anuncios de texto de Google Search para una keyword."""
    _pause(pause)

    params = {
        "q": keyword, "gl": "ES", "hl": "es",
        "num": 10, "pws": 0, "nfpr": 1,
    }

    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=_headers(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        return [{"error": str(e), "keyword": keyword, "type": "search"}]

    if "sorry" in r.url or r.status_code == 429:
        return [{"error": "CAPTCHA", "keyword": keyword, "type": "search"}]

    soup = BeautifulSoup(r.text, "lxml")
    ads = []

    # Selector principal: bloques de anuncio
    ad_blocks = soup.find_all("div", attrs={"data-text-ad": "1"})

    # Fallback: buscar por marcador "Patrocinado"
    if not ad_blocks:
        for span in soup.find_all("span", string=re.compile(r"Patrocinado|Sponsored", re.I)):
            p = span.find_parent("div", class_=True)
            if p and p not in ad_blocks:
                ad_blocks.append(p)

    position = 1
    for block in ad_blocks:
        # Título
        title_el = (block.find("div", attrs={"role": "heading"}) or block.find("h3"))
        title = title_el.get_text(strip=True) if title_el else ""

        # URL visible
        url_el = block.find("cite")
        display_url = url_el.get_text(strip=True) if url_el else ""

        # Descripción
        desc_divs = block.find_all(["div", "span"],
                                    class_=re.compile(r"MUxGbd|yDYNvb|VwiC3b"))
        description = " ".join(
            d.get_text(strip=True) for d in desc_divs
            if d.get_text(strip=True) and d.get_text(strip=True) != title
        )[:400]

        # URL destino
        link = block.find("a", href=True)
        dest_url = link["href"] if link else ""

        # Extensiones (sitelinks)
        extensions = []
        for ext in block.find_all("div", class_=re.compile(r"MhgNwc|OkkX2d|sitelinks")):
            t = ext.get_text(strip=True)
            if t and t not in (title, description):
                extensions.append(t[:80])

        brand = _detect_brand(title + display_url, dest_url)

        ads.append({
            "scraped_at":   datetime.now().isoformat(),
            "type":         "search",
            "keyword":      keyword,
            "keyword_type": _kw_type(keyword),
            "position":     position,
            "brand":        brand or "Otro",
            "title":        title,
            "description":  description,
            "display_url":  display_url,
            "dest_url":     dest_url,
            "extensions":   " | ".join(extensions[:5]),
            "n_extensions": len(extensions),
        })
        position += 1

    return ads


# ── Shopping / PMax ────────────────────────────────────────────────────────────

def scrape_shopping(keyword: str, pause: float = 5.0) -> list[dict]:
    """Extrae fichas de Google Shopping para una keyword."""
    _pause(pause)

    params = {
        "q": keyword, "tbm": "shop",
        "gl": "ES", "hl": "es", "pws": 0,
    }

    try:
        r = requests.get("https://www.google.com/search",
                         params=params, headers=_headers(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        return [{"error": str(e), "keyword": keyword, "type": "shopping"}]

    if "sorry" in r.url or r.status_code == 429:
        return [{"error": "CAPTCHA", "keyword": keyword, "type": "shopping"}]

    soup = BeautifulSoup(r.text, "lxml")
    results = []
    position = 1

    for item in soup.select(".sh-dgr__content, .u30d4, [data-sh-gr]")[:12]:
        title_el = item.select_one("h3, .tAxDx, [aria-label]")
        title = title_el.get_text(strip=True) if title_el else ""

        price_el = item.select_one(".a8Pemb, .price, [data-price]")
        price = price_el.get_text(strip=True) if price_el else ""

        seller_el = item.select_one(".aULzUe, .E5ocAb, .seller")
        seller = seller_el.get_text(strip=True) if seller_el else ""

        link = item.select_one("a[href]")
        url = link["href"] if link else ""

        img = item.select_one("img")
        img_url = img.get("src", "") if img else ""

        brand = _detect_brand(title + seller, url)

        results.append({
            "scraped_at":   datetime.now().isoformat(),
            "type":         "shopping",
            "keyword":      keyword,
            "keyword_type": _kw_type(keyword),
            "position":     position,
            "brand":        brand or "Otro",
            "title":        title,
            "price":        price,
            "seller":       seller,
            "dest_url":     url,
            "img_url":      img_url,
        })
        position += 1

    return results


# ── Google Ad Transparency Center ──────────────────────────────────────────────

def scrape_ad_transparency(brand_name: str, pause: float = 6.0) -> list[dict]:
    """
    Extrae anuncios (Display, Video, Search) del Ad Transparency Center de Google.
    URL: https://adstransparency.google.com/advertiser/...
    """
    _pause(pause)

    # Búsqueda de anunciante en el Transparency Center
    search_url = "https://adstransparency.google.com/advertiser/search"
    params = {"query": brand_name, "region": "ES"}

    try:
        r = requests.get(search_url, params=params, headers=_headers(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        return [{"error": str(e), "brand": brand_name, "type": "transparency"}]

    soup = BeautifulSoup(r.text, "lxml")
    results = []

    # Extrae tarjetas de anuncios del Transparency Center
    for card in soup.select(".creative-card, [data-creative-id], .ad-card")[:20]:
        ad_type = "display"
        if card.select_one("video, [data-video]"):
            ad_type = "video"
        elif card.select_one(".text-ad, [data-text-ad]"):
            ad_type = "search"

        title_el = card.select_one("h3, .ad-title, .creative-title")
        title = title_el.get_text(strip=True) if title_el else ""

        img_el = card.select_one("img")
        img_url = img_el.get("src", "") if img_el else ""

        domain_el = card.select_one(".domain, .advertiser-domain")
        domain = domain_el.get_text(strip=True) if domain_el else ""

        date_el = card.select_one(".date, .first-shown")
        date_shown = date_el.get_text(strip=True) if date_el else ""

        results.append({
            "scraped_at":  datetime.now().isoformat(),
            "type":        ad_type,
            "brand":       brand_name,
            "title":       title,
            "img_url":     img_url,
            "domain":      domain,
            "date_shown":  date_shown,
        })

    return results


# ── Índice de intensidad ───────────────────────────────────────────────────────

def compute_intensity_index(ads: list[dict]) -> dict:
    """
    Calcula un proxy de intensidad de inversión por marca.
    Score = f(nº keywords, posición media, nº extensiones, frecuencia)
    Máximo 100 puntos.
    """
    from collections import defaultdict
    import numpy as np

    brand_data = defaultdict(lambda: {
        "keywords": set(), "positions": [], "extensions": [], "types": set()
    })

    for ad in ads:
        if "error" in ad:
            continue
        b = ad.get("brand", "Otro")
        brand_data[b]["keywords"].add(ad.get("keyword", ""))
        if ad.get("position"):
            brand_data[b]["positions"].append(ad["position"])
        brand_data[b]["extensions"].append(ad.get("n_extensions", 0))
        brand_data[b]["types"].add(ad.get("type", ""))

    all_kws = max((len(v["keywords"]) for v in brand_data.values()), default=1)
    scores = {}

    for brand, data in brand_data.items():
        n_kws = len(data["keywords"])
        avg_pos = sum(data["positions"]) / len(data["positions"]) if data["positions"] else 10
        avg_ext = sum(data["extensions"]) / len(data["extensions"]) if data["extensions"] else 0
        n_types = len(data["types"])

        # Componentes del score (suma 100)
        kw_score  = (n_kws / max(all_kws, 1)) * 40        # 40 pts: cobertura de keywords
        pos_score = max(0, (10 - avg_pos) / 9) * 30       # 30 pts: mejor posición
        ext_score = min(avg_ext / 5, 1) * 20              # 20 pts: extensiones activas
        type_score = (n_types / 4) * 10                   # 10 pts: diversidad de canales

        total = round(kw_score + pos_score + ext_score + type_score, 1)

        scores[brand] = {
            "score":       total,
            "n_keywords":  n_kws,
            "avg_position": round(avg_pos, 1),
            "avg_extensions": round(avg_ext, 1),
            "channels":    list(data["types"]),
        }

    return scores


# ── Helpers ────────────────────────────────────────────────────────────────────

def _kw_type(kw: str) -> str:
    kw_lower = kw.lower()
    for brand, cfg in BRANDS.items():
        if any(k in kw_lower for k in cfg["keywords_brand"]):
            return "marca_competencia" if not cfg["is_own"] else "marca_propia"
    intent_words = ["precio", "contratar", "instalar", "mejor", "oferta"]
    if any(w in kw_lower for w in intent_words):
        return "intencion"
    return "generica"


def all_keywords() -> list[str]:
    """Devuelve todas las keywords aplanadas."""
    kws = []
    for group in KEYWORDS.values():
        kws.extend(group)
    return list(dict.fromkeys(kws))  # deduplica manteniendo orden


# ── Persistencia ───────────────────────────────────────────────────────────────

DATA_DIR = Path("data")

def save_run(ads: list[dict], run_id: str = None) -> str:
    """Guarda una ejecución de scraping en data/runs/."""
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "runs").mkdir(exist_ok=True)

    run_id = run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / "runs" / f"{run_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ads, f, ensure_ascii=False, indent=2)
    return run_id


def load_all_runs() -> list[dict]:
    """Carga y combina todas las ejecuciones guardadas."""
    runs_dir = DATA_DIR / "runs"
    if not runs_dir.exists():
        return []
    all_ads = []
    for f in sorted(runs_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fh:
            all_ads.extend(json.load(fh))
    return all_ads


def load_latest_run() -> list[dict]:
    """Carga solo la última ejecución."""
    runs_dir = DATA_DIR / "runs"
    if not runs_dir.exists():
        return []
    files = sorted(runs_dir.glob("*.json"))
    if not files:
        return []
    with open(files[-1], encoding="utf-8") as f:
        return json.load(f)

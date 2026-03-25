# 📡 AdWatch — Competitive Intelligence Dashboard

Dashboard dark mode estilo Apple para monitorizar la inversión publicitaria de Securitas Direct, Verisure y Movistar Alarmas en Google Ads.

## Stack
- **Streamlit** — dashboard web
- **requests + BeautifulSoup** — scraping sin API de pago
- **pandas** — análisis de datos
- **GitHub + Streamlit Cloud** — deploy gratuito

---

## 🚀 Setup en 5 pasos

### 1. Clona el repo
```bash
git clone https://github.com/TU_USUARIO/adwatch.git
cd adwatch
```

### 2. Instala dependencias (local)
```bash
pip install -r requirements.txt
```

### 3. Ejecuta en local
```bash
streamlit run app.py
```

### 4. Sube a GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 5. Deploy en Streamlit Cloud (gratis)
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repo `adwatch` y el archivo `app.py`
4. ✅ Tu dashboard estará en `https://TU_USUARIO-adwatch.streamlit.app`

---

## 📁 Estructura del proyecto

```
adwatch/
├── app.py                    # Punto de entrada Streamlit
├── scraper_engine.py         # Motor de scraping multi-canal
├── requirements.txt
├── .gitignore
├── pages_content/
│   ├── overview.py           # Vista general + índice de intensidad
│   ├── search_ads.py         # Anuncios de texto
│   ├── shopping.py           # Google Shopping / PMax
│   ├── display_youtube.py    # Display y video (Fase 2)
│   ├── raw_data.py           # Datos en crudo + exportación
│   └── scraper.py            # Panel para lanzar el scraper
└── data/
    └── runs/                 # JSONs con cada ejecución (autogenerado)
```

---

## ⚙️ Cómo usar

1. Abre el dashboard → sección **⚙️ Ejecutar Scraper**
2. Selecciona canales y keywords
3. Ajusta la pausa (mínimo 6s para evitar CAPTCHAs)
4. Pulsa **Iniciar scraping**
5. Ve al **Overview** para ver resultados

Para ejecución diaria automática, usa **GitHub Actions** (ver sección avanzada).

---

## 📊 Índice de intensidad

Proxy de inversión publicitaria calculado sobre señales públicas:

| Componente | Peso | Qué mide |
|---|---|---|
| Cobertura de keywords | 40% | En cuántas keywords aparece |
| Posición media | 30% | Qué tan arriba aparece |
| Extensiones activas | 20% | Cuántas extensiones usa |
| Diversidad de canales | 10% | Search, Shopping, Display, Video |

---

## ⚠️ Notas

- **CAPTCHA**: Si Google bloquea las peticiones, sube la pausa a 10-12s
- **Frecuencia recomendada**: una ejecución diaria, a la misma hora
- **Datos**: se guardan en `data/runs/` como JSON, no se borran entre ejecuciones
- Los datos de Display/Video requieren Selenium (Fase 2)

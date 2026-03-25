# 📡 AdWatch — Competitive Intelligence Dashboard

Dashboard dark mode para monitorizar la inversión publicitaria de Securitas Direct, Verisure y Movistar Alarmas en Google Ads.

## Estructura (archivo único)
```
adwatch/
├── app.py            ← todo el código aquí
├── requirements.txt
├── .gitignore
└── data/runs/        ← se crea automáticamente al scraper
```

## Deploy en Streamlit Cloud

1. Sube estos 3 archivos a un repo de GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta el repo → archivo principal: `app.py`
4. ✅ Listo

## Uso

1. Abre el dashboard → **⚙️ Scraper**
2. Selecciona canales y keywords
3. Pausa recomendada: 7–10s
4. **Overview** → ver resultados y score de intensidad

## Nota sobre CAPTCHAs

Streamlit Cloud usa IPs de servidor que Google puede bloquear.
Para ejecución diaria sin problemas, clona el repo y ejecuta localmente:
```bash
pip install -r requirements.txt
streamlit run app.py
```

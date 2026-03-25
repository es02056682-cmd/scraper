"""
AdWatch — Competitive Intelligence Dashboard
============================================
Streamlit app principal. Punto de entrada.
"""

import streamlit as st

st.set_page_config(
    page_title="AdWatch — Competitive Intel",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos globales dark mode estilo Apple
st.markdown("""
<style>
  /* Base */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #000000;
    color: #f5f5f7;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #1c1c1e;
    border-right: 1px solid #2c2c2e;
  }
  [data-testid="stSidebar"] .stMarkdown p {
    color: #98989d;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
  }

  /* Métricas */
  [data-testid="metric-container"] {
    background: #1c1c1e;
    border: 1px solid #2c2c2e;
    border-radius: 16px;
    padding: 20px 24px;
  }
  [data-testid="metric-container"] label {
    color: #98989d !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f5f5f7 !important;
    font-size: 28px !important;
    font-weight: 600 !important;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #1c1c1e;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #98989d;
    font-weight: 500;
    font-size: 14px;
  }
  .stTabs [aria-selected="true"] {
    background: #2c2c2e !important;
    color: #f5f5f7 !important;
  }

  /* Dataframes */
  [data-testid="stDataFrame"] {
    border: 1px solid #2c2c2e;
    border-radius: 12px;
    overflow: hidden;
  }

  /* Botones */
  .stButton > button {
    background: #0a84ff;
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 500;
    font-size: 14px;
    padding: 8px 20px;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: #0071e3;
    transform: scale(1.01);
  }

  /* Selectbox y multiselect */
  [data-testid="stSelectbox"], [data-testid="stMultiSelect"] {
    background: #1c1c1e;
  }

  /* Cards personalizadas */
  .aw-card {
    background: #1c1c1e;
    border: 1px solid #2c2c2e;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
  }
  .aw-card-accent {
    border-left: 3px solid #0a84ff;
  }
  .aw-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
  }
  .aw-badge-active   { background: #1a3a1a; color: #30d158; }
  .aw-badge-inactive { background: #3a1a1a; color: #ff453a; }
  .aw-badge-search   { background: #1a2a3a; color: #0a84ff; }
  .aw-badge-shopping { background: #2a1a3a; color: #bf5af2; }
  .aw-badge-display  { background: #3a2a1a; color: #ff9f0a; }
  .aw-badge-video    { background: #3a1a1a; color: #ff453a; }

  .aw-label {
    font-size: 11px;
    font-weight: 500;
    color: #98989d;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 4px;
  }
  .aw-value {
    font-size: 15px;
    font-weight: 500;
    color: #f5f5f7;
  }
  .aw-divider {
    border: none;
    border-top: 1px solid #2c2c2e;
    margin: 16px 0;
  }

  /* Ocultar elementos Streamlit por defecto */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Navegación principal
from pages_content import overview, search_ads, shopping, display_youtube, raw_data, scraper

# Sidebar
with st.sidebar:
    st.markdown("## 📡 AdWatch")
    st.markdown("Competitive Intelligence")
    st.markdown("---")

    page = st.radio(
        "Navegación",
        options=["Overview", "Search Ads", "Shopping & PMax", "Display & YouTube", "Raw Data", "⚙️ Ejecutar Scraper"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("Marcas monitorizadas")
    st.markdown("""
    <div style='display:flex;flex-direction:column;gap:8px;margin-top:4px'>
      <div style='display:flex;align-items:center;gap:8px'>
        <div style='width:8px;height:8px;border-radius:50%;background:#0a84ff'></div>
        <span style='font-size:13px;color:#f5f5f7'>Movistar Alarmas</span>
        <span style='font-size:10px;color:#30d158;margin-left:auto'>TÚ</span>
      </div>
      <div style='display:flex;align-items:center;gap:8px'>
        <div style='width:8px;height:8px;border-radius:50%;background:#ff453a'></div>
        <span style='font-size:13px;color:#f5f5f7'>Securitas Direct</span>
      </div>
      <div style='display:flex;align-items:center;gap:8px'>
        <div style='width:8px;height:8px;border-radius:50%;background:#ff9f0a'></div>
        <span style='font-size:13px;color:#f5f5f7'>Verisure</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<span style='font-size:11px;color:#48484a'>Última actualización<br>Ejecuta el scraper para datos reales</span>", unsafe_allow_html=True)

# Routing
if page == "Overview":
    overview.render()
elif page == "Search Ads":
    search_ads.render()
elif page == "Shopping & PMax":
    shopping.render()
elif page == "Display & YouTube":
    display_youtube.render()
elif page == "Raw Data":
    raw_data.render()
elif page == "⚙️ Ejecutar Scraper":
    scraper.render()

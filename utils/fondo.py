import streamlit as st

# URL de Unsplash — mina de cobre a tajo abierto, tonos tierra, alta resolución
# Foto: Dominik Vanyi · https://unsplash.com/photos/aerial-view-of-brown-and-gray-mountain-Mk2ls9UBO2E
FONDO_URL = (
    "https://images.unsplash.com/photo-1517089596392-fb9a9033e05b"
    "?q=80&w=1920&auto=format&fit=crop"
)

def aplicar_fondo(url: str = FONDO_URL, opacidad: float = 0.06):
    """
    Aplica una imagen de fondo muy transparente desde una URL (Unsplash).

    Parámetros:
        url      : URL pública de la imagen
        opacidad : 0.0 (invisible) → 1.0 (sólida) — recomendado 0.04–0.09
    """
    capa_blanca = round(1 - opacidad, 3)

    st.markdown(f"""
    <style>
    /* ── Fondo minero ── */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    /* Capa blanca para controlar opacidad visual */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(255, 255, 255, {capa_blanca});
        pointer-events: none;
        z-index: 0;
    }}
    /* Contenido por encima */
    [data-testid="stAppViewContainer"] > * {{
        position: relative;
        z-index: 1;
    }}
    /* Sidebar limpio, sin imagen */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.97) !important;
    }}
    /* Header translúcido */
    [data-testid="stHeader"] {{
        background: rgba(255, 255, 255, 0.80) !important;
        backdrop-filter: blur(6px);
    }}

    /* ── Tabs — contenedor completo ── */
    [data-testid="stTabs"] {{
        background: rgba(109, 58, 31, 0.07) !important;
        border-radius: 12px !important;
        padding: 0 !important;
        overflow: hidden !important;
    }}
    /* Barra de pestañas */
    [data-testid="stTabs"] [role="tablist"] {{
        background: #3B1A08 !important;
        border-radius: 12px 12px 0 0 !important;
        border-bottom: none !important;
        padding: 4px 8px 0 8px !important;
        gap: 2px !important;
    }}
    /* Tab inactivo */
    [data-testid="stTabs"] [role="tab"] {{
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.55) !important;
        border: none !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 18px !important;
        background: transparent !important;
        transition: color 0.15s, background 0.15s;
    }}
    /* Tab inactivo hover */
    [data-testid="stTabs"] [role="tab"]:hover {{
        color: rgba(255,255,255,0.85) !important;
        background: rgba(255,255,255,0.08) !important;
    }}
    /* Tab activo */
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        color: #1A1008 !important;
        font-weight: 700 !important;
        background: #E8B84B !important;
        border-radius: 8px 8px 0 0 !important;
    }}
    /* Quitar línea azul por defecto de Streamlit */
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]::after {{
        display: none !important;
    }}
    /* Contenido del tab activo */
    [data-testid="stTabs"] [role="tabpanel"] {{
        background: rgba(255, 252, 248, 0.92) !important;
        border-radius: 0 0 12px 12px !important;
        padding: 16px 20px !important;
        border: 0.5px solid rgba(109,58,31,0.15) !important;
        border-top: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Mapa — IMDM", layout="wide", initial_sidebar_state="expanded")

from utils.fondo import aplicar_fondo
aplicar_fondo(opacidad=0.15)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stDataFrame, .stMarkdown, button, input, select {
    font-family: 'DM Sans', sans-serif !important;
}
.block-container { max-width:100%; padding:1.5rem 2rem 2rem 2rem; }
.hero { background:#1C1008; border-radius:14px; padding:24px 30px; margin-bottom:18px;
        display:flex; align-items:flex-start; justify-content:space-between; gap:24px; }
.hero-eye { font-size:10px; font-weight:600; letter-spacing:.10em; text-transform:uppercase;
            color:rgba(255,255,255,.38); margin-bottom:7px; }
.hero-title { color:#fff; font-size:22px; font-weight:700; margin:0 0 7px 0;
              letter-spacing:-0.02em; line-height:1.25; }
.hero-sub { color:rgba(255,255,255,.42); font-size:12.5px; margin:0; line-height:1.6; max-width:480px; }
.hero-right { display:flex; flex-direction:column; align-items:flex-end; gap:9px; flex-shrink:0; }
.hero-badges { display:flex; gap:7px; }
.hero-badge { background:rgba(255,255,255,.07); border:0.5px solid rgba(255,255,255,.14);
              border-radius:9px; padding:9px 16px; text-align:center; }
.hero-badge strong { display:block; font-size:18px; font-weight:700; color:#E8B84B; line-height:1; }
.hero-badge span { font-size:9px; color:rgba(255,255,255,.4); letter-spacing:.07em;
                   text-transform:uppercase; margin-top:2px; display:block; }
.badge-alto       { background:#EAF3DE; color:#27500A; }
.badge-medio      { background:#FFF0D6; color:#7A4000; }
.badge-bajo       { background:#FFE8D6; color:#8B2500; }
.badge-deficiente { background:#FDECEA; color:#7B2F1F; }
.badge-critico    { background:#FDECEA; color:#7B1F1F; }
.kpi-card  { border-radius:11px; padding:13px 16px; }
.kpi-label { font-size:9px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
             opacity:.6; margin-bottom:4px; }
.kpi-value { font-size:20px; font-weight:700; line-height:1; letter-spacing:-.02em; }
.kpi-sub   { font-size:10px; opacity:.5; margin-top:2px; }
.section-header { font-size:9px; font-weight:600; letter-spacing:.09em; text-transform:uppercase;
                  color:#A07850; margin-bottom:10px; }
.footer { text-align:center; font-size:11px; color:#CCC; margin-top:28px;
          padding-top:14px; border-top:0.5px solid #EDE0D0; }
</style>
""", unsafe_allow_html=True)

C_DARK  = "#6D3A1F"
C_MED   = "#A0622A"
C_WARM  = "#C88B3A"
C_GOLD  = "#E8B84B"
KPI_STYLES = [("#1C1008","#FFFFFF"),("#A0622A","#FFFFFF"),
              ("#C88B3A","#FFFFFF"),("#E8B84B","#3B2000")]

# ── Coordenadas y metadata por empresa ──
# Fuente: ubicación de la operación principal de cada empresa
EMPRESA_META = {
    "Compañía Minera Antamina":         {"lat": -9.533,  "lon": -77.166, "region": "Áncash"},
    "Compañía Minera Antapaccay":       {"lat": -14.820, "lon": -71.629, "region": "Cusco"},
    "Compañía Minera Coimolache":       {"lat": -6.617,  "lon": -78.817, "region": "Cajamarca"},
    "Compañía de Minas Buenaventura":   {"lat": -11.583, "lon": -76.650, "region": "Lima/Pasco"},
    "Gold Fields La Cima":              {"lat": -6.658,  "lon": -78.767, "region": "Cajamarca"},
    "Minera Chinalco Perú":             {"lat": -11.600, "lon": -75.900, "region": "Junín"},
    "Minera Las Bambas":                {"lat": -13.841, "lon": -72.183, "region": "Apurímac"},
    "Minera Yanacocha":                 {"lat": -6.973,  "lon": -78.603, "region": "Cajamarca"},
    "Minsur":                           {"lat": -14.150, "lon": -70.317, "region": "Puno"},
    "Nexa Resources Perú":              {"lat": -10.683, "lon": -76.217, "region": "Pasco"},
    "Sociedad Minera El Brocal":        {"lat": -10.617, "lon": -76.383, "region": "Pasco"},
    "Volcan Compañía Minera":           {"lat": -11.467, "lon": -76.067, "region": "Junín"},
}

def rango_info(v):
    if v >= 80:   return "#4CAF50", "#EAF3DE", "#27500A", "Desempeño sobresaliente"
    elif v >= 60: return "#E8B84B", "#FFF0D6", "#7A4000", "Buen desempeño"
    elif v >= 40: return "#C88B3A", "#FFE8D6", "#8B2500", "Desempeño regular"
    elif v >= 20: return "#E07B39", "#FDECEA", "#7B2F1F", "Desempeño deficiente"
    else:         return "#E24B4A", "#FDECEA", "#7B1F1F", "Desempeño crítico"

def clasificar(v):
    if v >= 80:   return "Desempeño sobresaliente", "badge badge-alto"
    elif v >= 60: return "Buen desempeño",          "badge badge-medio"
    elif v >= 40: return "Desempeño regular",       "badge badge-bajo"
    elif v >= 20: return "Desempeño deficiente",    "badge badge-deficiente"
    else:         return "Desempeño crítico",       "badge badge-critico"

# ══════════════════════════════════════════
# CARGA Y CÁLCULO
# ══════════════════════════════════════════
@st.cache_data
def load_and_score():
    df    = pd.read_csv("data/data_mineras.csv",      sep=";", encoding="utf-8-sig")
    p_ind = pd.read_csv("data/pesos_indicadores.csv", sep=";", encoding="utf-8-sig").dropna(subset=["indicador"])
    p_dim = pd.read_csv("data/pesos_dimensiones.csv", sep=",", encoding="utf-8-sig")

    pdim    = p_dim.set_index("dimension")["peso"].to_dict()
    p_local = p_ind.set_index("indicador")["peso_local"].to_dict()

    BENEFICIO = {"empleo_local","inversion_minera","produccion_valor","canon_minero","sentimiento_social"}
    COSTO     = {"num_conflictos","multa_ambiental","pasivos_ambientales","NBI"}
    PISO = 0.01

    def mm_b(s):
        r = s.max()-s.min()
        return pd.Series(1.0, index=s.index) if r==0 else ((s-s.min())/r).clip(lower=PISO)
    def mm_c(s):
        r = s.max()-s.min()
        return pd.Series(1.0, index=s.index) if r==0 else ((s.max()-s)/r).clip(lower=PISO)
    def topsis(df_n, pw):
        cols = list(pw.keys()); V = df_n[cols].copy()
        for c in cols: V[c] = V[c]*pw[c]
        dp = np.sqrt(((V[cols]-V[cols].max())**2).sum(axis=1))
        dn = np.sqrt(((V[cols]-V[cols].min())**2).sum(axis=1))
        return (dn/(dp+dn+1e-10)).clip(0,1)

    df2 = df.copy().rename(columns={"Año":"anio","Empresa":"razon_social"})
    df2["anio"] = df2["anio"].astype(int)

    INDS = list(p_local.keys())
    for ind in INDS:
        fn = mm_b if ind in BENEFICIO else mm_c
        df2[f"n_{ind}"] = df2.groupby("anio")[ind].transform(fn)

    df_t = df2[["razon_social","anio"]].copy()
    for ind in INDS: df_t[ind] = df2[f"n_{ind}"]

    dim_inds = {
        "Social":    ["num_conflictos","sentimiento_social","NBI"],
        "Ambiental": ["multa_ambiental","pasivos_ambientales"],
        "Economica": ["empleo_local","inversion_minera","produccion_valor","canon_minero"],
    }
    for dim, inds in dim_inds.items():
        df_t[f"score_{dim.lower()}"] = topsis(df_t, {i: p_local[i] for i in inds})

    ws, wa, we = pdim["Social"], pdim["Ambiental"], pdim["Economica"]
    df_t["score_imdm"] = (
        df_t["score_social"]**ws * df_t["score_ambiental"]**wa * df_t["score_economica"]**we
    )
    for c in ["score_social","score_ambiental","score_economica","score_imdm"]:
        df_t[c] = (df_t[c]*100).round(1)

    # Score histórico (decaimiento λ=0.15, T_REF=2024)
    LAMBDA, T_REF = 0.15, 2024
    def sh(g):
        g = g.copy(); g["w"] = np.exp(-LAMBDA*(T_REF-g["anio"])); w = g["w"].sum()
        return pd.Series({
            "sh_social":    round((g["score_social"]   *g["w"]).sum()/w, 1),
            "sh_ambiental": round((g["score_ambiental"]*g["w"]).sum()/w, 1),
            "sh_economica": round((g["score_economica"]*g["w"]).sum()/w, 1),
            "sh_imdm":      round((g["score_imdm"]     *g["w"]).sum()/w, 1),
        })
    hist = (df_t[["razon_social","anio","score_social","score_ambiental","score_economica","score_imdm"]]
            .groupby("razon_social").apply(sh).reset_index())

    return df_t, hist

scores_anuales, historico = load_and_score()
anio_max = scores_anuales["anio"].max()

# Enriquecer histórico con metadata geográfica
historico["region"]  = historico["razon_social"].map(lambda e: EMPRESA_META.get(e,{}).get("region","—"))
historico["lat"]     = historico["razon_social"].map(lambda e: EMPRESA_META.get(e,{}).get("lat", -9.5))
historico["lon"]     = historico["razon_social"].map(lambda e: EMPRESA_META.get(e,{}).get("lon",-75.5))

# ══════════════════════════════════════════
# HERO
# ══════════════════════════════════════════
n_emp  = historico["razon_social"].nunique()
n_reg  = historico["region"].nunique()
sh_avg = round(historico["sh_imdm"].mean(), 1)

st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-eye">IMDM · Distribución geográfica</div>
    <div class="hero-title">Mapa de empresas mineras</div>
    <div class="hero-sub">Ubicación de las {n_emp} empresas evaluadas. El color del marcador
    refleja el score IMDM histórico. Haz clic en un marcador para ver el detalle.</div>
  </div>
  <div class="hero-right">
    <div class="hero-badges">
      <div class="hero-badge"><strong>{n_emp}</strong><span>Empresas</span></div>
      <div class="hero-badge"><strong>{n_reg}</strong><span>Regiones</span></div>
      <div class="hero-badge"><strong>{sh_avg}</strong><span>IMDM prom.</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# FILTROS
# ══════════════════════════════════════════
cf1, cf2 = st.columns(2)
with cf1:
    filtro_region = st.selectbox(
        "Región", ["Todas"] + sorted(historico["region"].dropna().unique()),
        label_visibility="visible"
    )
with cf2:
    filtro_rango = st.selectbox(
        "Clasificación IMDM",
        ["Todas", "Desempeño sobresaliente (≥80)", "Buen desempeño (60–79)",
         "Desempeño regular (40–59)", "Desempeño deficiente (20–39)", "Desempeño crítico (<20)"],
        label_visibility="visible"
    )

filtrado = historico.copy()
if filtro_region != "Todas": filtrado = filtrado[filtrado["region"] == filtro_region]
if filtro_rango == "Desempeño sobresaliente (≥80)":    filtrado = filtrado[filtrado["sh_imdm"] >= 80]
elif filtro_rango == "Buen desempeño (60–79)":         filtrado = filtrado[(filtrado["sh_imdm"]>=60)&(filtrado["sh_imdm"]<80)]
elif filtro_rango == "Desempeño regular (40–59)":      filtrado = filtrado[(filtrado["sh_imdm"]>=40)&(filtrado["sh_imdm"]<60)]
elif filtro_rango == "Desempeño deficiente (20–39)":   filtrado = filtrado[(filtrado["sh_imdm"]>=20)&(filtrado["sh_imdm"]<40)]
elif filtro_rango == "Desempeño crítico (<20)":        filtrado = filtrado[filtrado["sh_imdm"] < 20]

# ══════════════════════════════════════════
# KPIs REACTIVOS
# ══════════════════════════════════════════
kpis = [
    (len(filtrado),                                              "Empresas",      "en el filtro"),
    (filtrado["region"].nunique(),                              "Regiones",      "cubiertas"),
    (round(filtrado["sh_imdm"].mean(),1) if len(filtrado) else "—", "IMDM promedio", "histórico"),
    (round(filtrado["sh_imdm"].max(),1)  if len(filtrado) else "—", "IMDM máximo",   "en el filtro"),
]
cols = st.columns(4)
for col,(val,label,sub),(bg,fg) in zip(cols, kpis, KPI_STYLES):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="background:{bg};color:{fg};">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
st.markdown(f'<div class="section-header">Distribución geográfica · {len(filtrado)} empresas · IMDM histórico 2020–2024</div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════
# MAPA FOLIUM
# ══════════════════════════════════════════
mapa = folium.Map(
    location=[-9.5, -75.5],
    zoom_start=6,
    tiles="CartoDB positron",
    min_zoom=5,
    max_zoom=13,
)
mapa.fit_bounds([[-18.5, -81.5], [0.5, -68.5]])

for _, row in filtrado.iterrows():
    mc, bg_c, fg_c, rng_lbl = rango_info(row["sh_imdm"])

    # Score puntual del año más reciente para el popup
    sc_anio = scores_anuales[
        (scores_anuales["razon_social"]==row["razon_social"]) &
        (scores_anuales["anio"]==anio_max)
    ]
    sc_anio_imdm = f"{sc_anio['score_imdm'].values[0]:.1f}" if not sc_anio.empty else "—"

    popup_html = f"""
    <div style="font-family:'DM Sans',sans-serif;min-width:220px;padding:4px;">
      <div style="font-size:13px;font-weight:700;color:#1A1008;margin-bottom:8px;
                  border-bottom:1px solid #EDE0D0;padding-bottom:6px;line-height:1.3;">
        {row['razon_social']}
      </div>
      <table style="width:100%;font-size:12px;border-collapse:collapse;">
        <tr>
          <td style="color:#A07850;padding:3px 0;">Región</td>
          <td style="font-weight:500;text-align:right;">{row['region']}</td>
        </tr>
        <tr>
          <td style="color:#A07850;padding:3px 0;">Social hist.</td>
          <td style="font-weight:500;text-align:right;">{row['sh_social']:.1f}</td>
        </tr>
        <tr>
          <td style="color:#A07850;padding:3px 0;">Ambiental hist.</td>
          <td style="font-weight:500;text-align:right;">{row['sh_ambiental']:.1f}</td>
        </tr>
        <tr>
          <td style="color:#A07850;padding:3px 0;">Económico hist.</td>
          <td style="font-weight:500;text-align:right;">{row['sh_economica']:.1f}</td>
        </tr>
        <tr>
          <td style="color:#A07850;padding:3px 0;">IMDM {anio_max}</td>
          <td style="font-weight:500;text-align:right;">{sc_anio_imdm}</td>
        </tr>
        <tr style="border-top:1px solid #EDE0D0;">
          <td style="color:#1A1008;font-weight:700;padding-top:5px;">IMDM histórico</td>
          <td style="text-align:right;padding-top:5px;">
            <span style="background:{bg_c};color:{fg_c};font-weight:700;
                         padding:2px 9px;border-radius:12px;font-size:12px;">
              {row['sh_imdm']:.1f} · {rng_lbl}
            </span>
          </td>
        </tr>
      </table>
    </div>
    """

    # Radio proporcional al score (entre 8 y 18px)
    radio = 8 + int((row["sh_imdm"] / 100) * 10)

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=radio,
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"{row['razon_social']} — {row['sh_imdm']:.1f} pts · {rng_lbl}",
        color="#FFFFFF",
        weight=2,
        fill=True,
        fill_color=mc,
        fill_opacity=0.88,
    ).add_to(mapa)

# Leyenda
legend_html = """
<div style="position:fixed;bottom:30px;left:30px;z-index:1000;
            background:white;border-radius:10px;padding:14px 18px;
            border:0.5px solid #EDE0D0;font-family:'DM Sans',sans-serif;">
  <div style="font-size:9px;font-weight:600;letter-spacing:.09em;
              text-transform:uppercase;color:#A07850;margin-bottom:10px;">
    Score IMDM histórico
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <div style="width:13px;height:13px;border-radius:50%;background:#4CAF50;border:2px solid #fff;box-shadow:0 0 0 1px #ccc;"></div>
    <span style="font-size:11px;color:#333;">Desempeño sobresaliente &nbsp;≥ 80</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <div style="width:13px;height:13px;border-radius:50%;background:#E8B84B;border:2px solid #fff;box-shadow:0 0 0 1px #ccc;"></div>
    <span style="font-size:11px;color:#333;">Buen desempeño &nbsp;60–79</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <div style="width:13px;height:13px;border-radius:50%;background:#C88B3A;border:2px solid #fff;box-shadow:0 0 0 1px #ccc;"></div>
    <span style="font-size:11px;color:#333;">Desempeño regular &nbsp;40–59</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
    <div style="width:13px;height:13px;border-radius:50%;background:#E07B39;border:2px solid #fff;box-shadow:0 0 0 1px #ccc;"></div>
    <span style="font-size:11px;color:#333;">Desempeño deficiente &nbsp;20–39</span>
  </div>
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:2px;">
    <div style="width:13px;height:13px;border-radius:50%;background:#E24B4A;border:2px solid #fff;box-shadow:0 0 0 1px #ccc;"></div>
    <span style="font-size:11px;color:#333;">Desempeño crítico &nbsp;&lt; 20</span>
  </div>
  <div style="margin-top:10px;padding-top:8px;border-top:0.5px solid #EDE0D0;
              font-size:10px;color:#A07850;">
    Tamaño proporcional al score
  </div>
</div>
"""
mapa.get_root().html.add_child(folium.Element(legend_html))

st_folium(mapa, use_container_width=True, height=540)

st.divider()

# ══════════════════════════════════════════
# TABLA
# ══════════════════════════════════════════
st.markdown('<div class="section-header">Empresas visualizadas · score histórico</div>',
            unsafe_allow_html=True)

df_tabla = (
    filtrado[["razon_social","region","sh_social","sh_ambiental","sh_economica","sh_imdm"]]
    .sort_values("sh_imdm", ascending=False)
    .rename(columns={
        "razon_social":  "Empresa",
        "region":        "Región",
        "sh_social":     "Social",
        "sh_ambiental":  "Ambiental",
        "sh_economica":  "Económico",
        "sh_imdm":       "IMDM",
    })
)
st.dataframe(
    df_tabla, use_container_width=True, hide_index=True, height=300,
    column_config={
        "Empresa":   st.column_config.TextColumn("Empresa"),
        "Región":    st.column_config.TextColumn("Región",   width="small"),
        "Social":    st.column_config.ProgressColumn("Social",    min_value=0, max_value=100, format="%.1f"),
        "Ambiental": st.column_config.ProgressColumn("Ambiental", min_value=0, max_value=100, format="%.1f"),
        "Económico": st.column_config.ProgressColumn("Económico", min_value=0, max_value=100, format="%.1f"),
        "IMDM":      st.column_config.ProgressColumn("IMDM",      min_value=0, max_value=100, format="%.1f"),
    }
)

st.markdown("""
<div class="footer">
  Indicador Multidimensional de Desempeño Minero · Perú 2020–2024 · Universidad del Pacífico
</div>""", unsafe_allow_html=True)
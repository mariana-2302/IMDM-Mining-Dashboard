import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Evaluación SENACE — IMDM", layout="wide", initial_sidebar_state="expanded")

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

.selector-bar { background:#FAF6F0; border:0.5px solid #EDE0D0; border-radius:12px;
                padding:12px 18px; margin-bottom:16px;
                display:flex; align-items:center; gap:14px; flex-wrap:wrap; }
.selector-label { font-size:9px; font-weight:600; letter-spacing:.08em;
                  text-transform:uppercase; color:#A07850; margin-bottom:2px; }
.selector-empresa { font-size:16px; font-weight:700; color:#1A1008; line-height:1.2; }
.badge { display:inline-block; font-size:11px; font-weight:700; padding:4px 13px; border-radius:20px; }
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

.peso-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.peso-bar-track { flex:1; background:rgba(0,0,0,.07); border-radius:3px; height:7px; overflow:hidden; }
.peso-bar-fill  { height:100%; border-radius:3px; }

.datos-table { width:100%; border-collapse:collapse; font-size:12px; }
.datos-table th { font-size:9px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
                  color:#A07850; padding:8px 12px; border-bottom:2px solid #EDE0D0; text-align:right; }
.datos-table th:first-child { text-align:left; width:185px; }
.datos-table th:nth-child(2) { text-align:center; width:46px; }
.datos-table td { padding:8px 12px; text-align:right; border-bottom:0.5px solid rgba(0,0,0,.05); }
.datos-table td:first-child { text-align:left; font-weight:500; color:#3B2000; }
.datos-table td:nth-child(2) { text-align:center; }
.datos-table .dim-sep td { padding:4px 12px; font-size:9px; font-weight:700;
                            letter-spacing:.08em; text-transform:uppercase;
                            border-bottom:none; border-top:1px solid #EDE0D0; }
.datos-table .dim-sep-s td { color:#6D3A1F; background:rgba(109,58,31,0.04); }
.datos-table .dim-sep-a td { color:#A0622A; background:rgba(160,98,42,0.05); }
.datos-table .dim-sep-e td { color:#C88B3A; background:rgba(200,139,58,0.05); }
.datos-table .row-s { background:rgba(109,58,31,0.04); }
.datos-table .row-a { background:rgba(160,98,42,0.06); }
.datos-table .row-e { background:rgba(200,139,58,0.06); }
.datos-table .row-imdm { background:#1C1008; }
.datos-table .row-imdm td { color:#E8B84B; font-weight:700; border-bottom:none; }
.datos-table .row-imdm td:first-child { color:#E8B84B; }
.val-costo { color:#8B2500; font-weight:600; }
.val-benef { color:#27500A; font-weight:600; }
.val-zero  { color:#BBB; }
.dim-tag { display:inline-block; font-size:9px; font-weight:700; padding:2px 7px; border-radius:10px; }
.tag-s { background:#6D3A1F; color:#fff; }
.tag-a { background:#A0622A; color:#fff; }
.tag-e { background:#C88B3A; color:#3B2000; }
.score-pill { display:inline-block; padding:2px 9px; border-radius:10px;
              font-weight:700; font-size:11px; }

.footer { text-align:center; font-size:11px; color:#CCC; margin-top:28px;
          padding-top:14px; border-top:0.5px solid #EDE0D0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════
C_DARK  = "#6D3A1F"
C_MED   = "#A0622A"
C_WARM  = "#C88B3A"
C_GOLD  = "#E8B84B"
C_LIGHT = "#F5D980"
LAMBDA  = 0.15
T_REF   = 2024
KPI_STYLES = [("#1C1008","#FFFFFF"),("#A0622A","#FFFFFF"),("#C88B3A","#FFFFFF"),("#E8B84B","#3B2000")]

NOMBRES_IND = {
    "num_conflictos":      "Conflictos sociales",
    "sentimiento_social":  "Sentimiento social",
    "NBI":                 "NBI",
    "multa_ambiental":     "Multa ambiental",
    "pasivos_ambientales": "Pasivos ambientales",
    "empleo_local":        "Empleo local",
    "inversion_minera":    "Inversión minera",
    "produccion_valor":    "Producción valorizada",
    "canon_minero":        "Canon minero",
}
DIM_TAG = {
    "num_conflictos": "S", "sentimiento_social": "S", "NBI": "S",
    "multa_ambiental": "A", "pasivos_ambientales": "A",
    "empleo_local": "E", "inversion_minera": "E",
    "produccion_valor": "E", "canon_minero": "E",
}

def clasificar(v):
    if v >= 80:   return "Desempeño sobresaliente", "badge badge-alto"
    elif v >= 60: return "Buen desempeño",          "badge badge-medio"
    elif v >= 40: return "Desempeño regular",       "badge badge-bajo"
    elif v >= 20: return "Desempeño deficiente",    "badge badge-deficiente"
    else:         return "Desempeño crítico",       "badge badge-critico"

def rango_bg(v):
    if v >= 80:   return "#EAF3DE", "#27500A"
    elif v >= 60: return "#FFF0D6", "#7A4000"
    elif v >= 40: return "#FFE8D6", "#8B2500"
    elif v >= 20: return "#FDECEA", "#7B2F1F"
    else:         return "#FDECEA", "#7B1F1F"

# ══════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    df    = pd.read_csv("data/data_mineras.csv",      sep=";", encoding="utf-8-sig")
    p_ind = pd.read_csv("data/pesos_indicadores.csv", sep=";", encoding="utf-8-sig")
    p_dim = pd.read_csv("data/pesos_dimensiones.csv", sep=",", encoding="utf-8-sig")
    p_ind = p_ind.dropna(subset=["indicador"])
    return df, p_ind, p_dim

data, pesos_ind, pesos_dim = load_data()

# ══════════════════════════════════════════
# CÁLCULO SCORES ANUALES
# ══════════════════════════════════════════
@st.cache_data
def calcular_scores(data, pesos_ind, pesos_dim):
    pdim    = pesos_dim.set_index("dimension")["peso"].to_dict()
    p_local = pesos_ind.set_index("indicador")["peso_local"].to_dict()

    BENEFICIO = {"empleo_local", "inversion_minera", "produccion_valor", "canon_minero", "sentimiento_social"}
    COSTO     = {"num_conflictos", "multa_ambiental", "pasivos_ambientales", "NBI"}
    PISO = 0.01

    def mm_b(s):
        r = s.max() - s.min()
        return pd.Series(1.0, index=s.index) if r == 0 else ((s - s.min()) / r).clip(lower=PISO)

    def mm_c(s):
        r = s.max() - s.min()
        return pd.Series(1.0, index=s.index) if r == 0 else ((s.max() - s) / r).clip(lower=PISO)

    def topsis(df_n, pw):
        cols = list(pw.keys())
        V = df_n[cols].copy()
        for c in cols:
            V[c] = V[c] * pw[c]
        dp = np.sqrt(((V[cols] - V[cols].max()) ** 2).sum(axis=1))
        dn = np.sqrt(((V[cols] - V[cols].min()) ** 2).sum(axis=1))
        return (dn / (dp + dn + 1e-10)).clip(0, 1)

    df2 = data.copy().rename(columns={"Año": "anio", "Empresa": "razon_social"})
    df2["anio"] = df2["anio"].astype(int)

    INDS = list(p_local.keys())
    for ind in INDS:
        if ind in BENEFICIO:
            df2[f"n_{ind}"] = df2.groupby("anio")[ind].transform(mm_b)
        else:
            df2[f"n_{ind}"] = df2.groupby("anio")[ind].transform(mm_c)

    df_t = df2[["razon_social", "anio"]].copy()
    for ind in INDS:
        df_t[ind] = df2[f"n_{ind}"]

    dim_inds = {
        "Social":    ["num_conflictos", "sentimiento_social", "NBI"],
        "Ambiental": ["multa_ambiental", "pasivos_ambientales"],
        "Economica": ["empleo_local", "inversion_minera", "produccion_valor", "canon_minero"],
    }
    for dim, inds in dim_inds.items():
        pw_dim = {ind: p_local[ind] for ind in inds}
        df_t[f"score_{dim.lower()}"] = topsis(df_t, pw_dim)

    ws, wa, we = pdim["Social"], pdim["Ambiental"], pdim["Economica"]
    df_t["score_imdm"] = (
        df_t["score_social"]    ** ws *
        df_t["score_ambiental"] ** wa *
        df_t["score_economica"] ** we
    )
    for c in ["score_social", "score_ambiental", "score_economica", "score_imdm"]:
        df_t[c] = (df_t[c] * 100).round(1)

    return df_t, pdim

scores_anuales, pdim = calcular_scores(data, pesos_ind, pesos_dim)
anios = sorted(scores_anuales["anio"].unique())

# ══════════════════════════════════════════
# SCORE HISTÓRICO
# ══════════════════════════════════════════
@st.cache_data
def calcular_historico(scores_anuales):
    def sh(g):
        g = g.copy()
        g["w"] = np.exp(-LAMBDA * (T_REF - g["anio"]))
        w = g["w"].sum()
        return pd.Series({
            "sh_social":    round((g["score_social"]    * g["w"]).sum() / w, 1),
            "sh_ambiental": round((g["score_ambiental"] * g["w"]).sum() / w, 1),
            "sh_economica": round((g["score_economica"] * g["w"]).sum() / w, 1),
            "sh_imdm":      round((g["score_imdm"]      * g["w"]).sum() / w, 1),
        })
    return scores_anuales.groupby("razon_social").apply(sh).reset_index()

historico  = calcular_historico(scores_anuales)
sh_prom    = round(historico["sh_imdm"].mean(), 1)
n_emp      = historico["razon_social"].nunique()
imdm_prom  = round(scores_anuales["score_imdm"].mean(), 1)

# ══════════════════════════════════════════
# HERO
# ══════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-eye">IMDM · Evaluación SENACE · Etapa 6 EIA-d</div>
    <div class="hero-title">Desempeño minero empresarial</div>
    <div class="hero-sub">Score calculado con TOPSIS por dimensión y media geométrica ponderada ANP.
    Selecciona una empresa y el modo de visualización. Período 2020–2024.</div>
  </div>
  <div class="hero-right">
    <div class="hero-badges">
      <div class="hero-badge"><strong>{n_emp}</strong><span>Empresas</span></div>
      <div class="hero-badge"><strong>{imdm_prom}</strong><span>IMDM prom.</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SELECTOR + MODO
# ══════════════════════════════════════════
col_sel, col_modo, col_anio, col_badge = st.columns([3, 2, 2, 1])

with col_sel:
    empresa_sel = st.selectbox(
        "Empresa", sorted(historico["razon_social"].unique()),
        label_visibility="collapsed"
    )

with col_modo:
    modo = st.radio(
        "Modo", ["Anual", "Histórico"],
        horizontal=True, label_visibility="collapsed"
    )

with col_anio:
    if modo == "Anual":
        anio_sel = st.select_slider("Año", options=anios, value=anios[-1], label_visibility="collapsed")
    else:
        st.empty()

# Datos según modo
if modo == "Anual":
    fila = scores_anuales[
        (scores_anuales["razon_social"] == empresa_sel) &
        (scores_anuales["anio"] == anio_sel)
    ].iloc[0]
    s_social = fila["score_social"]
    s_amb    = fila["score_ambiental"]
    s_eco    = fila["score_economica"]
    s_imdm   = fila["score_imdm"]
    sub_imdm = f"año {anio_sel}"
    lbl_gauge = f"Score IMDM · {anio_sel}"
else:
    fila = historico[historico["razon_social"] == empresa_sel].iloc[0]
    s_social = fila["sh_social"]
    s_amb    = fila["sh_ambiental"]
    s_eco    = fila["sh_economica"]
    s_imdm   = fila["sh_imdm"]
    sub_imdm = "histórico 2020–2024"
    lbl_gauge = "Score IMDM histórico"

clas_txt, clas_cls = clasificar(s_imdm)

with col_badge:
    st.markdown(f"<div style='padding-top:6px;'><span class='{clas_cls}'>{clas_txt}</span></div>",
                unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════
kpis = [
    (f"{s_social:.1f}",  "Social",    "score dimensión"),
    (f"{s_amb:.1f}",     "Ambiental", "score dimensión"),
    (f"{s_eco:.1f}",     "Económico", "score dimensión"),
    (f"{s_imdm:.1f}",    "IMDM",      sub_imdm),
]
cols = st.columns(4)
for col, (val, label, sub), (bg, fg) in zip(cols, kpis, KPI_STYLES):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="background:{bg};color:{fg};">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# GAUGE + RADAR
# ══════════════════════════════════════════
col_g, col_r = st.columns(2)

with col_g:
    st.markdown(f'<div class="section-header">{lbl_gauge}</div>', unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=s_imdm,
        number=dict(font=dict(size=44, family="DM Sans", color="#1A1008"), suffix=" pts"),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickvals=[0, 20, 40, 60, 80, 100],
                ticktext=["0", "20", "40", "60", "80", "100"],
                tickfont=dict(size=11, family="DM Sans", color="#A07850"),
                tickcolor="#EDE0D0",
            ),
            bar=dict(color=C_DARK, thickness=0.5),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0,  20], color="#FDECEA"),
                dict(range=[20, 40], color="#FFE8D6"),
                dict(range=[40, 60], color="#FFF0D6"),
                dict(range=[60, 80], color="#FFFBE6"),
                dict(range=[80,100], color="#EAF3DE"),
            ],
            threshold=dict(line=dict(color=C_GOLD, width=3), thickness=0.85, value=s_imdm),
            shape="angular",
        ),
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=30, r=30, t=20, b=20),
        height=300,
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_r:
    st.markdown('<div class="section-header">Perfil dimensional vs. sector</div>', unsafe_allow_html=True)
    cats = ["Social", "Ambiental", "Económico"]
    vals = [s_social, s_amb, s_eco]
    prom = [
        round(historico["sh_social"].mean(),    1),
        round(historico["sh_ambiental"].mean(), 1),
        round(historico["sh_economica"].mean(), 1),
    ]
    fig_r = go.Figure()
    fig_r.add_trace(go.Scatterpolar(
        r=prom + [prom[0]], theta=cats + [cats[0]], fill="toself",
        fillcolor="rgba(232,184,75,0.10)",
        line=dict(color=C_GOLD, width=1.5, dash="dot"),
        name="Promedio sector",
    ))
    fig_r.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
        fillcolor="rgba(109,58,31,0.18)",
        line=dict(color=C_DARK, width=2.5),
        name=empresa_sel[:28],
        marker=dict(size=7, color=C_DARK),
    ))
    fig_r.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                tickfont=dict(size=10, family="DM Sans"),
                gridcolor="rgba(0,0,0,0.08)", linecolor="rgba(0,0,0,0.10)"),
            angularaxis=dict(tickfont=dict(size=12, family="DM Sans", color="#1A1008"),
                linecolor="rgba(0,0,0,0.10)"),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08,
            font=dict(size=11, family="DM Sans")),
        margin=dict(l=40, r=40, t=10, b=40),
        height=300,
    )
    st.plotly_chart(fig_r, use_container_width=True)

st.divider()

# ══════════════════════════════════════════
# EVOLUCIÓN HISTÓRICA (siempre visible)
# ══════════════════════════════════════════
st.markdown('<div class="section-header">Evolución histórica por dimensión</div>', unsafe_allow_html=True)

df_evo = scores_anuales[scores_anuales["razon_social"] == empresa_sel].sort_values("anio")

fig_evo = go.Figure()
trazos = [
    ("score_imdm",      "IMDM global",  C_DARK,  3.0,   None,    8),
    ("score_social",    "Social",       C_MED,   1.8,   "dot",   5),
    ("score_ambiental", "Ambiental",    C_WARM,  1.8,   "dot",   5),
    ("score_economica", "Económico",    C_GOLD,  1.8,   "dot",   5),
]
for col, name, color, width, dash, msize in trazos:
    line_kw = dict(color=color, width=width)
    if dash:
        line_kw["dash"] = dash
    fig_evo.add_trace(go.Scatter(
        x=df_evo["anio"], y=df_evo[col],
        name=name, mode="lines+markers",
        line=line_kw,
        marker=dict(color=C_GOLD if col == "score_imdm" else color,
                    size=msize,
                    line=dict(color=C_DARK, width=2) if col == "score_imdm" else dict(width=0)),
        hovertemplate=f"<b>%{{x}}</b> {name}: %{{y:.1f}}<extra></extra>",
    ))

for yv, lc in [(80, "#27500A"), (60, C_GOLD), (40, C_MED)]:
    fig_evo.add_hline(y=yv, line=dict(color=lc, dash="dot", width=0.8), opacity=0.4)

fig_evo.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, tickfont=dict(size=11, family="DM Sans"),
               dtick=1, tickformat="d"),
    yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(0,0,0,0.06)",
               tickfont=dict(size=11, family="DM Sans"), title="Score (0–100)"),
    legend=dict(orientation="h", x=0, y=-0.18, font=dict(size=11, family="DM Sans")),
    margin=dict(l=0, r=0, t=10, b=40),
    height=280,
)
st.plotly_chart(fig_evo, use_container_width=True)

st.divider()

# ══════════════════════════════════════════
# TABS
# ══════════════════════════════════════════
tab_rank, tab_datos, tab_pesos = st.tabs(["Ranking", "Datos reales", "Pesos ANP"])

# ── Tab: Ranking ──
with tab_rank:
    st.markdown('<div class="section-header">Ranking histórico · todas las empresas</div>',
                unsafe_allow_html=True)
    rank = historico.sort_values("sh_imdm", ascending=True).copy()
    fig_rank = go.Figure(go.Bar(
        x=rank["sh_imdm"],
        y=rank["razon_social"],
        orientation="h",
        marker=dict(
            color=[rango_bg(v)[0] for v in rank["sh_imdm"]],
            line=dict(color=[rango_bg(v)[1] for v in rank["sh_imdm"]], width=1),
        ),
        text=rank["sh_imdm"].apply(lambda v: f"{v:.1f}"),
        textposition="outside",
        textfont=dict(size=11, family="DM Sans", color="#5A3A00"),
        hovertemplate="<b>%{y}</b>: %{x:.1f}<extra></extra>",
    ))
    for xv, lc in [(80, "#27500A"), (60, C_GOLD), (40, C_MED)]:
        fig_rank.add_vline(x=xv, line=dict(color=lc, dash="dot", width=1.2), opacity=0.6)
    fig_rank.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans")),
        margin=dict(l=0, r=50, t=10, b=0),
        height=340,
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.dataframe(
        historico[["razon_social", "sh_social", "sh_ambiental", "sh_economica", "sh_imdm"]]
        .sort_values("sh_imdm", ascending=False)
        .rename(columns={
            "razon_social":  "Empresa",
            "sh_social":     "Social",
            "sh_ambiental":  "Ambiental",
            "sh_economica":  "Económico",
            "sh_imdm":       "IMDM",
        }),
        use_container_width=True, hide_index=True,
        column_config={
            "Empresa":   st.column_config.TextColumn("Empresa"),
            "Social":    st.column_config.ProgressColumn("Social",    min_value=0, max_value=100, format="%.1f"),
            "Ambiental": st.column_config.ProgressColumn("Ambiental", min_value=0, max_value=100, format="%.1f"),
            "Económico": st.column_config.ProgressColumn("Económico", min_value=0, max_value=100, format="%.1f"),
            "IMDM":      st.column_config.ProgressColumn("IMDM",      min_value=0, max_value=100, format="%.1f"),
        }
    )

# ── Tab: Datos reales ──
with tab_datos:
    st.markdown(f'<div class="section-header">{empresa_sel} · indicadores reales por año</div>',
                unsafe_allow_html=True)

    df_raw    = data[data["Empresa"] == empresa_sel].sort_values("Año").copy()
    anios_raw = sorted(df_raw["Año"].unique())
    df_sc     = scores_anuales[scores_anuales["razon_social"] == empresa_sel].sort_values("anio")

    COSTO  = {"num_conflictos", "multa_ambiental", "pasivos_ambientales", "NBI"}
    BENEF  = {"sentimiento_social", "empleo_local", "inversion_minera", "produccion_valor", "canon_minero"}

    def fmt_val(ind, v):
        if ind in ("inversion_minera", "produccion_valor", "canon_minero"):
            return f"{v/1e6:,.1f}M"
        elif ind == "multa_ambiental":
            return f"S/ {v:,.0f}" if v > 0 else "0"
        elif ind in ("NBI", "sentimiento_social"):
            return f"{v:.3f}"
        else:
            return f"{v:,.0f}"

    def val_class(ind, v):
        if ind in COSTO:
            return "val-zero" if v == 0 else "val-costo"
        return "val-benef"

    def score_pill(sv):
        bg, fg = rango_bg(sv)
        return f'<span class="score-pill" style="background:{bg};color:{fg};">{sv:.1f}</span>'

    # Encabezados
    ths = "".join(f"<th>{a}</th>" for a in anios_raw)

    # Grupos de indicadores
    grupos = [
        ("Social",    "s", ["num_conflictos","sentimiento_social","NBI"]),
        ("Ambiental", "a", ["multa_ambiental","pasivos_ambientales"]),
        ("Económica", "e", ["empleo_local","inversion_minera","produccion_valor","canon_minero"]),
    ]

    tbody = ""
    for dim_nombre, dim_key, inds in grupos:
        n_cols = 2 + len(anios_raw)
        tbody += f'<tr class="dim-sep dim-sep-{dim_key}"><td colspan="{n_cols}">{dim_nombre}</td></tr>'
        for ind in inds:
            tds = ""
            for a in anios_raw:
                r = df_raw[df_raw["Año"] == a]
                if r.empty:
                    tds += "<td>—</td>"
                else:
                    v   = r[ind].values[0]
                    txt = fmt_val(ind, v)
                    cls = val_class(ind, v)
                    tds += f'<td class="{cls}">{txt}</td>'
            tag = dim_key.upper()
            tbody += f'''<tr class="row-{dim_key}">
              <td>{NOMBRES_IND[ind]}</td>
              <td><span class="dim-tag tag-{dim_key}">{tag}</span></td>
              {tds}
            </tr>'''

    # Fila score IMDM
    score_tds = ""
    for a in anios_raw:
        r = df_sc[df_sc["anio"] == a]
        score_tds += f"<td>{score_pill(r['score_imdm'].values[0])}</td>" if not r.empty else "<td>—</td>"

    tbody += f'''<tr class="row-imdm">
      <td>Score IMDM</td><td></td>{score_tds}
    </tr>'''

    st.markdown(f"""
    <table class="datos-table">
      <thead><tr><th>Indicador</th><th>Dim.</th>{ths}</tr></thead>
      <tbody>{tbody}</tbody>
    </table>""", unsafe_allow_html=True)

# ── Tab: Pesos ANP ──
with tab_pesos:
    tp1, tp2, tp3 = st.columns(3)
    DIM_INFO = {
        "Social":    (C_DARK,  "#6D3A1F"),
        "Ambiental": (C_MED,   "#A0622A"),
        "Economica": (C_WARM,  "#7A5F10"),
    }
    dim_inds_pesos = {
        "Social":    ["sentimiento_social", "num_conflictos", "NBI"],
        "Ambiental": ["multa_ambiental", "pasivos_ambientales"],
        "Economica": ["produccion_valor", "empleo_local", "inversion_minera", "canon_minero"],
    }
    p_local_map = pesos_ind.set_index("indicador")["peso_local"].to_dict()
    p_dim_map   = pesos_dim.set_index("dimension")["peso"].to_dict()

    for col_tab, (dim, inds) in zip([tp1, tp2, tp3], dim_inds_pesos.items()):
        bar_color, txt_color = DIM_INFO[dim]
        with col_tab:
            st.markdown(
                f'<div class="section-header" style="color:{txt_color};">'
                f'{dim} · {p_dim_map[dim]:.4f}</div>',
                unsafe_allow_html=True
            )
            max_local = max(p_local_map[i] for i in inds)
            for ind in inds:
                pl  = p_local_map[ind]
                pct = (pl / max_local) * 100
                st.markdown(f"""
                <div style="margin-bottom:10px;">
                  <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px;">
                    <span style="color:#3B2000;">{NOMBRES_IND[ind]}</span>
                    <span style="font-weight:700;color:{txt_color};">{pl:.4f}</span>
                  </div>
                  <div style="background:rgba(0,0,0,.06);border-radius:4px;height:6px;overflow:hidden;">
                    <div style="width:{pct:.0f}%;height:100%;background:{bar_color};border-radius:4px;"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
  Indicador Multidimensional de Desempeño Minero · Perú 2020–2024 · Universidad del Pacífico
</div>""", unsafe_allow_html=True)
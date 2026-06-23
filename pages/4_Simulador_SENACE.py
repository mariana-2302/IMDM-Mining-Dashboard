import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador SENACE — IMDM", layout="wide", initial_sidebar_state="expanded")

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
                display:flex; align-items:center; justify-content:space-between; gap:12px; }
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
.kpi-sub   { font-size:11px; margin-top:5px; font-weight:700; }

.section-header { font-size:9px; font-weight:600; letter-spacing:.09em; text-transform:uppercase;
                  color:#A07850; margin-bottom:10px; }

.dim-chip { border-radius:9px; padding:11px 14px; text-align:center; }
.dim-chip-label { font-size:9px; font-weight:600; letter-spacing:.07em;
                  text-transform:uppercase; opacity:.6; margin-bottom:3px; }
.dim-chip-val { font-size:18px; font-weight:700; line-height:1; }

.hint { font-size:10px; color:#A07850; margin-top:2px; }

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
T_SIM   = 2025   # año del escenario hipotético
KPI_STYLES = [("#1C1008","#FFFFFF"),("#A0622A","#FFFFFF"),
              ("#C88B3A","#FFFFFF"),("#E8B84B","#3B2000")]

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

def delta_html(antes, despues, fg):
    d = round(despues - antes, 1)
    if d > 0:   return f'<span style="color:#A8D87E;font-weight:700;">▲ +{d}</span>'
    elif d < 0: return f'<span style="color:#F4A4A4;font-weight:700;">▼ {d}</span>'
    else:       return f'<span style="opacity:.5;font-weight:700;">— sin cambio</span>'

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
# SCORES ANUALES + HISTÓRICO
# ══════════════════════════════════════════
@st.cache_data
def calcular_scores(data, pesos_ind, pesos_dim):
    pdim    = pesos_dim.set_index("dimension")["peso"].to_dict()
    p_local = pesos_ind.set_index("indicador")["peso_local"].to_dict()

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
        cols = list(pw.keys())
        V = df_n[cols].copy()
        for c in cols: V[c] = V[c]*pw[c]
        dp = np.sqrt(((V[cols]-V[cols].max())**2).sum(axis=1))
        dn = np.sqrt(((V[cols]-V[cols].min())**2).sum(axis=1))
        return (dn/(dp+dn+1e-10)).clip(0,1)

    df2 = data.copy().rename(columns={"Año":"anio","Empresa":"razon_social"})
    df2["anio"] = df2["anio"].astype(int)

    INDS = list(p_local.keys())
    for ind in INDS:
        if ind in BENEFICIO:
            df2[f"n_{ind}"] = df2.groupby("anio")[ind].transform(mm_b)
        else:
            df2[f"n_{ind}"] = df2.groupby("anio")[ind].transform(mm_c)

    df_t = df2[["razon_social","anio"]].copy()
    for ind in INDS:
        df_t[ind] = df2[f"n_{ind}"]

    dim_inds = {
        "Social":    ["num_conflictos","sentimiento_social","NBI"],
        "Ambiental": ["multa_ambiental","pasivos_ambientales"],
        "Economica": ["empleo_local","inversion_minera","produccion_valor","canon_minero"],
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
    for c in ["score_social","score_ambiental","score_economica","score_imdm"]:
        df_t[c] = (df_t[c]*100).round(1)

    return df_t, pdim, p_local

scores_anuales, pdim, p_local = calcular_scores(data, pesos_ind, pesos_dim)

@st.cache_data
def calcular_historico(scores_anuales):
    def sh(g):
        g = g.copy()
        g["w"] = np.exp(-LAMBDA*(T_REF - g["anio"]))
        w = g["w"].sum()
        return pd.Series({
            "sh_social":    round((g["score_social"]    * g["w"]).sum()/w, 1),
            "sh_ambiental": round((g["score_ambiental"] * g["w"]).sum()/w, 1),
            "sh_economica": round((g["score_economica"] * g["w"]).sum()/w, 1),
            "sh_imdm":      round((g["score_imdm"]      * g["w"]).sum()/w, 1),
        })
    return scores_anuales.groupby("razon_social").apply(sh).reset_index()

historico   = calcular_historico(scores_anuales)
imdm_sector = round(historico["sh_imdm"].mean(), 1)
n_emp       = historico["razon_social"].nunique()

# ══════════════════════════════════════════
# FUNCIONES TOPSIS PARA ESCENARIO NUEVO
# normaliza contra distribución histórica completa
# ══════════════════════════════════════════
def norm_b_val(val, serie):
    mn, mx = serie.min(), serie.max()
    return 1.0 if mx==mn else float(np.clip((val-mn)/(mx-mn), 0.01, 1.0))

def norm_c_val(val, serie):
    mn, mx = serie.min(), serie.max()
    return 1.0 if mx==mn else float(np.clip((mx-val)/(mx-mn), 0.01, 1.0))

def topsis_1row(vals_norm, pesos):
    cols = list(pesos.keys())
    v         = np.array([vals_norm[c]*pesos[c] for c in cols])
    ideal_pos = np.array([pesos[c]*1.0  for c in cols])
    ideal_neg = np.array([pesos[c]*0.01 for c in cols])
    dp = np.sqrt(np.sum((v-ideal_pos)**2))
    dn = np.sqrt(np.sum((v-ideal_neg)**2))
    return float(np.clip(dn/(dp+dn+1e-10), 0, 1)) * 100

# ══════════════════════════════════════════
# HERO
# ══════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-eye">IMDM · Simulador SENACE</div>
    <div class="hero-title">Simulación de escenario hipotético</div>
    <div class="hero-sub">Ingresa los indicadores proyectados y observa cómo impactan
    el score de la empresa. El nuevo año se incorpora con su peso temporal correspondiente.</div>
  </div>
  <div class="hero-right">
    <div class="hero-badges">
      <div class="hero-badge"><strong>{imdm_sector}</strong><span>IMDM sector</span></div>
      <div class="hero-badge"><strong>{n_emp}</strong><span>Empresas</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# SELECTOR DE EMPRESA
# ══════════════════════════════════════════
empresa_sel = st.selectbox(
    "Empresa", sorted(historico["razon_social"].unique()),
    label_visibility="collapsed"
)
info_hist = historico[historico["razon_social"]==empresa_sel].iloc[0]
clas_txt, clas_cls = clasificar(info_hist["sh_imdm"])

st.markdown(f"""
<div class="selector-bar">
  <div>
    <div class="selector-label">Empresa seleccionada</div>
    <div class="selector-empresa">{empresa_sel}</div>
  </div>
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="text-align:right;">
      <div style="font-size:22px;font-weight:700;color:#1A1008;line-height:1;">{info_hist['sh_imdm']:.1f}</div>
      <div style="font-size:9px;color:#A07850;text-transform:uppercase;letter-spacing:.06em;">IMDM histórico actual</div>
    </div>
    <span class="{clas_cls}">{clas_txt}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# FORMULARIO — 3 columnas por dimensión
# ══════════════════════════════════════════
st.markdown('<div class="section-header">Parámetros del escenario hipotético · año 2025</div>',
            unsafe_allow_html=True)

col_s, col_a, col_e = st.columns(3)

with col_s:
    st.markdown(f'<div style="font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{C_DARK};margin-bottom:12px;">Social</div>', unsafe_allow_html=True)

    num_conflictos = st.number_input(
        "Conflictos activos", min_value=0, max_value=50,
        value=int(round(data["num_conflictos"].mean())),
        help="Número de conflictos sociales activos · rango histórico: 0 – 12"
    )
    st.markdown('<div class="hint">Rango histórico: 0 – 12</div>', unsafe_allow_html=True)

    sentimiento = st.slider(
        "Sentimiento social", min_value=-0.36, max_value=0.18,
        value=round(float(data["sentimiento_social"].mean()), 2), step=0.01,
        help="Índice de sentimiento NLP · rango histórico: −0.36 a +0.18"
    )
    st.markdown(f'<div class="hint">Rango histórico: −0.36 a +0.18</div>', unsafe_allow_html=True)

    nbi = st.slider(
        "NBI distrital", min_value=0.0, max_value=0.55,
        value=round(float(data["NBI"].mean()), 2), step=0.01,
        help="Proporción de hogares con NBI · rango histórico: 0.00 – 0.55"
    )
    st.markdown('<div class="hint">Rango histórico: 0.00 – 0.55</div>', unsafe_allow_html=True)

with col_a:
    st.markdown(f'<div style="font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{C_MED};margin-bottom:12px;">Ambiental</div>', unsafe_allow_html=True)

    multa = st.number_input(
        "Multa ambiental (S/)", min_value=0.0,
        value=0.0, step=10000.0, format="%.0f",
        help="Monto total de multas OEFA · rango histórico: 0 – 4,445,672"
    )
    st.markdown('<div class="hint">Rango histórico: 0 – 4,445,672</div>', unsafe_allow_html=True)

    pasivos = st.number_input(
        "Pasivos ambientales", min_value=0,
        value=int(round(data["pasivos_ambientales"].mean())),
        help="Número de pasivos ambientales mineros · rango histórico: 0 – 3,092"
    )
    st.markdown('<div class="hint">Rango histórico: 0 – 3,092</div>', unsafe_allow_html=True)

with col_e:
    st.markdown(f'<div style="font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#7A5F10;margin-bottom:12px;">Económica</div>', unsafe_allow_html=True)

    empleo = st.number_input(
        "Empleo local", min_value=0,
        value=int(round(data["empleo_local"].mean())),
        help="Número de trabajadores locales · rango histórico: 11 – 17,864"
    )
    st.markdown('<div class="hint">Rango histórico: 11 – 17,864</div>', unsafe_allow_html=True)

    inversion = st.number_input(
        "Inversión minera (USD)", min_value=0.0,
        value=float(round(data["inversion_minera"].mean()/1e6, 0))*1e6,
        step=1e6, format="%.0f",
        help="Inversión minera en USD · rango histórico: 14.7M – 689.4M"
    )
    st.markdown('<div class="hint">Rango histórico: 14.7M – 689.4M</div>', unsafe_allow_html=True)

    produccion = st.number_input(
        "Producción valorizada (USD)", min_value=0.0,
        value=float(round(data["produccion_valor"].mean()/1e6, 0))*1e6,
        step=10e6, format="%.0f",
        help="Producción valorizada en USD · rango histórico: 116M – 6,322M"
    )
    st.markdown('<div class="hint">Rango histórico: 116M – 6,322M</div>', unsafe_allow_html=True)

    canon = st.number_input(
        "Canon minero (USD)", min_value=0.0,
        value=float(round(data["canon_minero"].mean()/1e6, 0))*1e6,
        step=1e6, format="%.0f",
        help="Canon minero estimado en USD · rango histórico: 6M – 346M"
    )
    st.markdown('<div class="hint">Rango histórico: 6M – 346M</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
simular = st.button("▶  Simular escenario", use_container_width=True, type="primary")

# ══════════════════════════════════════════
# RESULTADO
# ══════════════════════════════════════════
if simular:

    # ── Normalizar indicadores del escenario ──
    n_conf = norm_c_val(num_conflictos, data["num_conflictos"])
    n_sent = norm_b_val(sentimiento,    data["sentimiento_social"])
    n_nbi  = norm_c_val(nbi,            data["NBI"])
    n_mult = norm_c_val(multa,          data["multa_ambiental"])
    n_pas  = norm_c_val(pasivos,        data["pasivos_ambientales"])
    n_emp  = norm_b_val(empleo,         data["empleo_local"])
    n_inv  = norm_b_val(inversion,      data["inversion_minera"])
    n_prod = norm_b_val(produccion,     data["produccion_valor"])
    n_can  = norm_b_val(canon,          data["canon_minero"])

    # ── TOPSIS por dimensión ──
    s_soc = round(topsis_1row(
        {"num_conflictos": n_conf, "sentimiento_social": n_sent, "NBI": n_nbi},
        {k: p_local[k] for k in ["num_conflictos","sentimiento_social","NBI"]}
    ), 1)
    s_amb = round(topsis_1row(
        {"multa_ambiental": n_mult, "pasivos_ambientales": n_pas},
        {k: p_local[k] for k in ["multa_ambiental","pasivos_ambientales"]}
    ), 1)
    s_eco = round(topsis_1row(
        {"empleo_local": n_emp, "inversion_minera": n_inv,
         "produccion_valor": n_prod, "canon_minero": n_can},
        {k: p_local[k] for k in ["empleo_local","inversion_minera","produccion_valor","canon_minero"]}
    ), 1)

    ws, wa, we = pdim["Social"], pdim["Ambiental"], pdim["Economica"]
    s_imdm_nuevo = round((s_soc/100)**ws * (s_amb/100)**wa * (s_eco/100)**we * 100, 1)

    # ── Score histórico proyectado (incorpora año hipotético T_SIM) ──
    df_emp = scores_anuales[scores_anuales["razon_social"]==empresa_sel].copy()
    anios_emp = df_emp["anio"].values
    sc_hist   = df_emp["score_imdm"].values
    w_hist    = np.array([np.exp(-LAMBDA*(T_SIM - a)) for a in anios_emp])
    w_nuevo   = np.exp(-LAMBDA*(T_SIM - T_SIM))  # = 1.0

    sh_proy = round(
        (np.sum(w_hist * sc_hist) + w_nuevo * s_imdm_nuevo) /
        (np.sum(w_hist) + w_nuevo), 1
    )
    sh_actual = info_hist["sh_imdm"]

    # Proyectado por dimensión (media ponderada simple para tabla)
    def sh_dim_proy(col_hist, score_nuevo):
        sc_h = df_emp[col_hist].values
        return round(
            (np.sum(w_hist * sc_h) + w_nuevo * score_nuevo) /
            (np.sum(w_hist) + w_nuevo), 1
        )
    sh_soc_proy = sh_dim_proy("score_social",    s_soc)
    sh_amb_proy = sh_dim_proy("score_ambiental", s_amb)
    sh_eco_proy = sh_dim_proy("score_economica", s_eco)

    clas_proy_txt, clas_proy_cls = clasificar(sh_proy)

    st.divider()
    st.markdown('<div class="section-header">Resultado de la simulación</div>',
                unsafe_allow_html=True)

    # ── KPIs ──
    kpis_res = [
        (f"{sh_proy:.1f}",   "IMDM proyectado",  delta_html(sh_actual,              sh_proy,   "#fff")),
        (f"{s_soc:.1f}",     "Social",            delta_html(info_hist["sh_social"],    s_soc,   "#fff")),
        (f"{s_amb:.1f}",     "Ambiental",         delta_html(info_hist["sh_ambiental"], s_amb,   "#fff")),
        (f"{s_eco:.1f}",     "Económico",         delta_html(info_hist["sh_economica"], s_eco,   "#3B2000")),
    ]
    rcols = st.columns(4)
    for col, (val, label, delta), (bg, fg) in zip(rcols, kpis_res, KPI_STYLES):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="background:{bg};color:{fg};">
              <div class="kpi-label">{label}</div>
              <div class="kpi-value">{val}</div>
              <div class="kpi-sub">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:18px;'></div>", unsafe_allow_html=True)

    # ── Gauge + Evolución ──
    rg1, rg2 = st.columns(2)

    with rg1:
        st.markdown('<div class="section-header">IMDM proyectado vs. actual</div>',
                    unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sh_proy,
            number=dict(font=dict(size=44, family="DM Sans", color="#1A1008"), suffix=" pts"),
            gauge=dict(
                axis=dict(range=[0,100],
                    tickvals=[0,20,40,60,80,100],
                    ticktext=["0","20","40","60","80","100"],
                    tickfont=dict(size=11, family="DM Sans", color="#A07850")),
                bar=dict(color=C_DARK, thickness=0.5),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[0, 20],  color="#FDECEA"),
                    dict(range=[20, 40], color="#FFE8D6"),
                    dict(range=[40, 60], color="#FFF0D6"),
                    dict(range=[60, 80], color="#FFFBE6"),
                    dict(range=[80,100], color="#EAF3DE"),
                ],
                threshold=dict(
                    line=dict(color=C_GOLD, width=3),
                    thickness=0.85, value=sh_actual
                ),
                shape="angular",
            ),
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=10, b=0),
            height=240, font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_g, use_container_width=True)
        st.caption(f"Línea dorada = IMDM actual ({sh_actual:.1f}) · Aguja = IMDM proyectado")

        st.markdown(f"""
        <div style="text-align:center;margin-top:4px;">
          <span class="{clas_proy_cls}">{clas_proy_txt}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        dc1, dc2, dc3 = st.columns(3)
        for dc, (dl, dv, dbg, dfg) in zip([dc1,dc2,dc3],[
            ("Social",    s_soc, "#1C1008", "#fff"),
            ("Ambiental", s_amb, "#A0622A", "#fff"),
            ("Económico", s_eco, "#C88B3A", "#fff"),
        ]):
            with dc:
                st.markdown(f"""
                <div class="dim-chip" style="background:{dbg};color:{dfg};">
                  <div class="dim-chip-label">{dl}</div>
                  <div class="dim-chip-val">{dv:.1f}</div>
                </div>""", unsafe_allow_html=True)

    with rg2:
        st.markdown('<div class="section-header">Evolución histórica + escenario 2025</div>',
                    unsafe_allow_html=True)

        df_evo = df_emp.sort_values("anio")
        anios_evo  = list(df_evo["anio"].astype(int)) + [T_SIM]
        scores_evo = list(df_evo["score_imdm"]) + [s_imdm_nuevo]

        fig_evo = go.Figure()

        # Línea histórica
        fig_evo.add_trace(go.Scatter(
            x=list(df_evo["anio"].astype(int)),
            y=list(df_evo["score_imdm"]),
            mode="lines+markers",
            name="IMDM histórico",
            line=dict(color=C_DARK, width=2.5),
            marker=dict(color=C_GOLD, size=7,
                        line=dict(color=C_DARK, width=2)),
            hovertemplate="<b>%{x}</b>: %{y:.1f}<extra></extra>",
        ))
        # Punto proyectado conectado con línea punteada
        fig_evo.add_trace(go.Scatter(
            x=[list(df_evo["anio"].astype(int))[-1], T_SIM],
            y=[list(df_evo["score_imdm"])[-1], s_imdm_nuevo],
            mode="lines+markers",
            name=f"Escenario {T_SIM}",
            line=dict(color=C_DARK, width=2, dash="dot"),
            marker=dict(color=C_GOLD, size=10,
                        line=dict(color=C_DARK, width=2.5),
                        symbol="star"),
            hovertemplate=f"<b>{T_SIM} (escenario)</b>: %{{y:.1f}}<extra></extra>",
        ))
        for yv, lc in [(80,"#27500A"),(60,C_GOLD),(40,C_MED)]:
            fig_evo.add_hline(y=yv, line=dict(color=lc, dash="dot", width=0.8), opacity=0.4)

        fig_evo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=11, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(range=[0,105], showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=11, family="DM Sans"), title="Score (0–100)"),
            legend=dict(orientation="h", x=0, y=-0.18,
                        font=dict(size=11, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=40),
            height=200,
        )
        st.plotly_chart(fig_evo, use_container_width=True)

        # Comparativa barras
        st.markdown('<div class="section-header" style="margin-top:8px;">Comparativa</div>',
                    unsafe_allow_html=True)
        escenarios  = [f"Escenario {T_SIM}", "IMDM histórico actual", "Promedio sector"]
        valores_bar = [s_imdm_nuevo, sh_actual, imdm_sector]
        fig_bar = go.Figure(go.Bar(
            x=valores_bar, y=escenarios, orientation="h",
            marker=dict(color=[C_GOLD, C_DARK, C_MED], line=dict(width=0)),
            text=[f"{v:.1f}" for v in valores_bar],
            textposition="outside",
            textfont=dict(size=12, family="DM Sans", color="#3B2000"),
            hovertemplate="<b>%{y}</b>: %{x:.1f}<extra></extra>",
        ))
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0,115], showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, tickfont=dict(size=11, family="DM Sans")),
            margin=dict(l=0, r=50, t=0, b=0), height=130,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ── Tabla resumen dimensional ──
    st.markdown('<div class="section-header">Resumen por dimensión</div>',
                unsafe_allow_html=True)

    resumen_df = pd.DataFrame({
        "Dimensión":            ["Social", "Ambiental", "Económico", "IMDM"],
        "Score escenario":      [s_soc, s_amb, s_eco, s_imdm_nuevo],
        "Histórico actual":     [info_hist["sh_social"], info_hist["sh_ambiental"],
                                 info_hist["sh_economica"], sh_actual],
        "Histórico proyectado": [sh_soc_proy, sh_amb_proy, sh_eco_proy, sh_proy],
    })
    st.dataframe(
        resumen_df, hide_index=True, use_container_width=True,
        column_config={
            "Dimensión":            st.column_config.TextColumn("Dimensión"),
            "Score escenario":      st.column_config.NumberColumn("Score escenario",      format="%.1f"),
            "Histórico actual":     st.column_config.NumberColumn("Histórico actual",     format="%.1f"),
            "Histórico proyectado": st.column_config.ProgressColumn("Histórico proyectado",
                                        min_value=0, max_value=100, format="%.1f"),
        }
    )
    st.caption(f"* Histórico proyectado incorpora el escenario {T_SIM} con decaimiento exponencial (λ={LAMBDA}).")

st.markdown("""
<div class="footer">
  Indicador Multidimensional de Desempeño Minero · Perú 2020–2024 · Universidad del Pacífico
</div>""", unsafe_allow_html=True)
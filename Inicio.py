import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="IMDM — Inicio",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
.hero-sub { color:rgba(255,255,255,.42); font-size:12.5px; margin:0;
            line-height:1.6; max-width:480px; }
.hero-senace { background:rgba(232,184,75,.10); border:0.5px solid rgba(232,184,75,.30);
               border-radius:7px; padding:6px 13px; font-size:10px; color:rgba(255,255,255,.55);
               display:flex; align-items:center; gap:6px; margin-top:10px; width:fit-content; }
.dot-green { width:6px; height:6px; border-radius:50%; background:#4CAF50; flex-shrink:0; }
.hero-right { display:flex; flex-direction:column; align-items:flex-end; gap:9px; flex-shrink:0; }
.hero-badges { display:flex; gap:7px; }
.hero-badge { background:rgba(255,255,255,.07); border:0.5px solid rgba(255,255,255,.14);
              border-radius:9px; padding:9px 16px; text-align:center; }
.hero-badge strong { display:block; font-size:18px; font-weight:700; color:#E8B84B; line-height:1; }
.hero-badge span { font-size:9px; color:rgba(255,255,255,.4); letter-spacing:.07em;
                   text-transform:uppercase; margin-top:2px; display:block; }

.kpi-card  { border-radius:11px; padding:13px 16px; }
.kpi-label { font-size:9px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
             opacity:.6; margin-bottom:4px; }
.kpi-value { font-size:20px; font-weight:700; line-height:1; letter-spacing:-.02em; }
.kpi-sub   { font-size:10px; opacity:.5; margin-top:2px; }

.section-header { font-size:9px; font-weight:600; letter-spacing:.09em; text-transform:uppercase;
                  color:#A07850; margin-bottom:10px; }

.info-bar { background:#FFF8EC; border:0.5px solid #E8B84B; border-radius:10px;
            padding:9px 16px; font-size:12px; color:#5A3A00; margin-bottom:14px; }

.footer { text-align:center; font-size:11px; color:#CCC; margin-top:28px;
          padding-top:14px; border-top:0.5px solid #EDE0D0; }
</style>
""", unsafe_allow_html=True)

C_DARK  = "#6D3A1F"
C_MED   = "#A0622A"
C_WARM  = "#C88B3A"
C_GOLD  = "#E8B84B"
C_LIGHT = "#F5D980"
BAR_SCALE = [[0.0,C_LIGHT],[0.35,C_GOLD],[0.65,C_WARM],[1.0,C_DARK]]
KPI_STYLES = [("#1C1008","#FFFFFF"),("#A0622A","#FFFFFF"),
              ("#C88B3A","#FFFFFF"),("#E8B84B","#3B2000")]

EMPRESA_REGION = {
    "Compañía Minera Antamina":       "Áncash",
    "Compañía Minera Antapaccay":     "Cusco",
    "Compañía Minera Coimolache":     "Cajamarca",
    "Compañía de Minas Buenaventura": "Lima/Pasco",
    "Gold Fields La Cima":            "Cajamarca",
    "Minera Chinalco Perú":           "Junín",
    "Minera Las Bambas":              "Apurímac",
    "Minera Yanacocha":               "Cajamarca",
    "Minsur":                         "Puno",
    "Nexa Resources Perú":            "Pasco",
    "Sociedad Minera El Brocal":      "Pasco",
    "Volcan Compañía Minera":         "Junín",
}

# ══════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_csv("data/data_mineras.csv", sep=";", encoding="utf-8-sig")
    df["anio"] = df["Año"].astype(int)
    df["razon_social"] = df["Empresa"]
    return df

data = load_data()
anios      = sorted(data["anio"].unique())
n_empresas = data["razon_social"].nunique()
n_regiones = len(set(EMPRESA_REGION.values()))

# KPIs globales
total_conflictos = int(data["num_conflictos"].sum())
total_multas     = data["multa_ambiental"].sum()
total_empleo     = int(data["empleo_local"].sum())
total_produccion = data["produccion_valor"].sum()

# Panorama por año
conf_anio  = data.groupby("anio")["num_conflictos"].sum().reset_index()
multa_anio = data.groupby("anio")["multa_ambiental"].sum().reset_index()

# ══════════════════════════════════════════
# HERO
# ══════════════════════════════════════════
st.markdown(f"""
<div class="hero">
  <div>
    <div class="hero-eye">IMDM · Índice Multidimensional de Desempeño Minero</div>
    <div class="hero-title">Desempeño histórico de empresas<br>mineras en el Perú</div>
    <div class="hero-sub">Score integrado de dimensiones social, ambiental y económica
    para complementar la evaluación de nuevos proyectos a cargo de SENACE.
    Período {anios[0]}–{anios[-1]}.</div>
    <div class="hero-senace">
      <span class="dot-green"></span>
      Criterio adicional · Etapa 6 del EIA-d — SENACE
    </div>
  </div>
  <div class="hero-right">
    <div class="hero-badges">
      <div class="hero-badge"><strong>{n_empresas}</strong><span>Empresas</span></div>
      <div class="hero-badge"><strong>{len(anios)}</strong><span>Años</span></div>
      <div class="hero-badge"><strong>{n_regiones}</strong><span>Regiones</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# KPIs GLOBALES
# ══════════════════════════════════════════
kpis = [
    (total_conflictos,                      "Conflictos totales",   f"{anios[0]}–{anios[-1]}"),
    (f"S/ {total_multas/1e6:.1f}M",         "Multas ambientales",   "acumulado sector"),
    (f"{total_empleo:,}",                   "Empleos locales",      "acumulados sector"),
    (f"${total_produccion/1e9:.1f}B",       "Producción total",     "USD acumulado"),
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
# PANORAMA SECTOR
# ══════════════════════════════════════════
st.markdown(f'<div class="section-header">Panorama del sector · {int(anios[0])}–{int(anios[-1])}</div>',
            unsafe_allow_html=True)

pc1, pc2 = st.columns(2)

with pc1:
    fig_conf = go.Figure(go.Scatter(
        x=conf_anio["anio"], y=conf_anio["num_conflictos"],
        mode="lines+markers",
        line=dict(color=C_DARK, width=2.5),
        marker=dict(color=C_GOLD, size=7, line=dict(color=C_DARK, width=1.5)),
        fill="tozeroy", fillcolor="rgba(109,58,31,0.08)",
        hovertemplate="<b>%{x}</b>: %{y} conflictos<extra></extra>",
    ))
    fig_conf.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=11, family="DM Sans"),
                   dtick=1, tickformat="d"),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                   tickfont=dict(size=11, family="DM Sans")),
        margin=dict(l=0, r=0, t=10, b=0), height=220,
        title=dict(text="Conflictos activos por año · total sector",
                   font=dict(size=10, family="DM Sans", color="#A07850"),
                   x=0, pad=dict(b=8)),
    )
    st.plotly_chart(fig_conf, use_container_width=True)

with pc2:
    fig_mult = go.Figure(go.Bar(
        x=multa_anio["anio"],
        y=multa_anio["multa_ambiental"] / 1e6,
        marker=dict(
            color=multa_anio["multa_ambiental"],
            colorscale=BAR_SCALE, line=dict(width=0)
        ),
        text=(multa_anio["multa_ambiental"]/1e6).apply(lambda v: f"S/ {v:.1f}M"),
        textposition="outside",
        textfont=dict(size=10, family="DM Sans", color="#5A3A00"),
        hovertemplate="<b>%{x}</b>: S/ %{y:.1f}M<extra></extra>",
    ))
    fig_mult.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=11, family="DM Sans"), tickformat="d"),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                   tickfont=dict(size=11, family="DM Sans"), title="S/ millones"),
        margin=dict(l=0, r=0, t=10, b=0), height=220,
        title=dict(text="Multas ambientales por año · total sector (S/)",
                   font=dict(size=10, family="DM Sans", color="#A07850"),
                   x=0, pad=dict(b=8)),
    )
    st.plotly_chart(fig_mult, use_container_width=True)

st.divider()

# ══════════════════════════════════════════
# CONSULTA POR EMPRESA
# ══════════════════════════════════════════
st.markdown('<div class="section-header">Consulta por empresa</div>', unsafe_allow_html=True)

col_sel, col_anio = st.columns([3, 1])
with col_sel:
    empresa_sel = st.selectbox(
        "Empresa", sorted(data["razon_social"].unique()),
        label_visibility="collapsed"
    )
with col_anio:
    anio_sel = st.selectbox(
        "Año", anios[::-1], label_visibility="collapsed"
    )

region = EMPRESA_REGION.get(empresa_sel, "—")
st.markdown(f"""
<div class="info-bar">
  <b>{empresa_sel}</b> &nbsp;·&nbsp; {region}
</div>""", unsafe_allow_html=True)

# Fila del año seleccionado
row_anio = data[(data["razon_social"]==empresa_sel) & (data["anio"]==anio_sel)]

def val_o_guion(df, col, fmt=None):
    if df.empty: return "—"
    v = df[col].values[0]
    return fmt(v) if fmt else v

conf_val = val_o_guion(row_anio, "num_conflictos")
mult_val = val_o_guion(row_anio, "multa_ambiental",
                       lambda v: f"S/ {v:,.0f}" if v > 0 else "S/ 0")
emp_val  = val_o_guion(row_anio, "empleo_local",
                       lambda v: f"{int(v):,}")
prod_val = val_o_guion(row_anio, "produccion_valor",
                       lambda v: f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.0f}M")

kpis_emp = [
    (conf_val, "Conflictos",       str(anio_sel)),
    (mult_val, "Multa ambiental",  str(anio_sel)),
    (emp_val,  "Empleo local",     "trabajadores"),
    (prod_val, "Producción",       f"USD {anio_sel}"),
]
cols2 = st.columns(4)
for col, (val, label, sub), (bg, fg) in zip(cols2, kpis_emp, KPI_STYLES):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="background:{bg};color:{fg};">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# Datos históricos de la empresa
df_emp = data[data["razon_social"]==empresa_sel].sort_values("anio")

tab_s, tab_a, tab_e = st.tabs(["Social", "Ambiental", "Económico"])

# ── Social ──
with tab_s:
    cs1, cs2, cs3 = st.columns(3)

    with cs1:
        fig = go.Figure(go.Bar(
            x=df_emp["anio"], y=df_emp["num_conflictos"],
            marker=dict(color=df_emp["num_conflictos"],
                        colorscale=BAR_SCALE, line=dict(width=0)),
            hovertemplate="<b>%{x}</b>: %{y} conflictos<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=0), height=180,
            title=dict(text="Conflictos por año",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with cs2:
        fig2 = go.Figure(go.Scatter(
            x=df_emp["anio"], y=df_emp["sentimiento_social"],
            mode="lines+markers",
            line=dict(color=C_MED, width=2),
            marker=dict(color=C_GOLD, size=6, line=dict(color=C_MED, width=1.5)),
            fill="tozeroy", fillcolor="rgba(160,98,42,0.08)",
            hovertemplate="<b>%{x}</b>: %{y:.3f}<extra></extra>",
        ))
        fig2.add_hline(y=0, line=dict(color="rgba(0,0,0,0.15)", dash="dot", width=1))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=0), height=180,
            title=dict(text="Sentimiento social",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with cs3:
        fig3 = go.Figure(go.Scatter(
            x=df_emp["anio"], y=df_emp["NBI"],
            mode="lines+markers",
            line=dict(color=C_WARM, width=2),
            marker=dict(color=C_GOLD, size=6, line=dict(color=C_WARM, width=1.5)),
            hovertemplate="<b>%{x}</b>: %{y:.3f}<extra></extra>",
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=0), height=180,
            title=dict(text="NBI distrital",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        df_emp[["anio","num_conflictos","sentimiento_social","NBI"]]
        .rename(columns={"anio":"Año","num_conflictos":"Conflictos",
                         "sentimiento_social":"Sentimiento","NBI":"NBI"}),
        use_container_width=True, hide_index=True,
        column_config={
            "Año":        st.column_config.NumberColumn("Año", format="%d"),
            "Conflictos": st.column_config.NumberColumn("Conflictos", format="%d"),
            "Sentimiento":st.column_config.NumberColumn("Sentimiento", format="%.3f"),
            "NBI":        st.column_config.NumberColumn("NBI", format="%.3f"),
        }
    )

# ── Ambiental ──
with tab_a:
    ca1, ca2 = st.columns(2)

    with ca1:
        fig = go.Figure(go.Bar(
            x=df_emp["anio"],
            y=df_emp["multa_ambiental"] / 1e3,
            marker=dict(color=df_emp["multa_ambiental"],
                        colorscale=BAR_SCALE, line=dict(width=0)),
            hovertemplate="<b>%{x}</b>: S/ %{y:,.0f}K<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans"), title="S/ miles"),
            margin=dict(l=0, r=0, t=10, b=0), height=200,
            title=dict(text="Multa ambiental por año (S/)",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with ca2:
        fig2 = go.Figure(go.Scatter(
            x=df_emp["anio"], y=df_emp["pasivos_ambientales"],
            mode="lines+markers",
            line=dict(color=C_DARK, width=2),
            marker=dict(color=C_GOLD, size=6, line=dict(color=C_DARK, width=1.5)),
            fill="tozeroy", fillcolor="rgba(109,58,31,0.08)",
            hovertemplate="<b>%{x}</b>: %{y} pasivos<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=0), height=200,
            title=dict(text="Pasivos ambientales por año",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        df_emp[["anio","multa_ambiental","pasivos_ambientales"]]
        .rename(columns={"anio":"Año","multa_ambiental":"Multa ambiental (S/)",
                         "pasivos_ambientales":"Pasivos"}),
        use_container_width=True, hide_index=True,
        column_config={
            "Año":               st.column_config.NumberColumn("Año", format="%d"),
            "Multa ambiental (S/)": st.column_config.NumberColumn("Multa ambiental (S/)", format="%,.0f"),
            "Pasivos":           st.column_config.NumberColumn("Pasivos", format="%d"),
        }
    )

# ── Económico ──
with tab_e:
    ce1, ce2 = st.columns(2)

    with ce1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_emp["anio"], y=df_emp["produccion_valor"]/1e6,
            name="Producción (MUSD)", marker_color=C_DARK,
            hovertemplate="<b>%{x}</b>: $%{y:,.0f}M<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=df_emp["anio"], y=df_emp["inversion_minera"]/1e6,
            name="Inversión (MUSD)", mode="lines+markers",
            line=dict(color=C_GOLD, width=2),
            marker=dict(size=6),
            hovertemplate="<b>%{x}</b>: $%{y:,.0f}M<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans"), title="MUSD"),
            legend=dict(orientation="h", x=0, y=-0.25,
                        font=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=40), height=220,
            title=dict(text="Producción e inversión (MUSD)",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig, use_container_width=True)

    with ce2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_emp["anio"], y=df_emp["empleo_local"],
            name="Empleo local", marker_color=C_MED,
            hovertemplate="<b>%{x}</b>: %{y:,} empleos<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=df_emp["anio"], y=df_emp["canon_minero"]/1e6,
            name="Canon (MUSD)", mode="lines+markers",
            line=dict(color=C_WARM, width=2),
            marker=dict(size=6), yaxis="y2",
            hovertemplate="<b>%{x}</b>: $%{y:,.0f}M<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, tickfont=dict(size=10, family="DM Sans"),
                       dtick=1, tickformat="d"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.06)",
                       tickfont=dict(size=10, family="DM Sans"), title="Empleos"),
            yaxis2=dict(overlaying="y", side="right",
                        tickfont=dict(size=10, family="DM Sans"), title="Canon MUSD"),
            legend=dict(orientation="h", x=0, y=-0.25,
                        font=dict(size=10, family="DM Sans")),
            margin=dict(l=0, r=0, t=10, b=40), height=220,
            title=dict(text="Empleo local y canon minero",
                       font=dict(size=9, family="DM Sans", color="#A07850"), x=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        df_emp[["anio","produccion_valor","inversion_minera","empleo_local","canon_minero"]]
        .assign(
            produccion_valor=lambda d: (d["produccion_valor"]/1e6).round(1),
            inversion_minera=lambda d: (d["inversion_minera"]/1e6).round(1),
            canon_minero=lambda d:     (d["canon_minero"]/1e6).round(1),
        )
        .rename(columns={
            "anio":             "Año",
            "produccion_valor": "Producción (MUSD)",
            "inversion_minera": "Inversión (MUSD)",
            "empleo_local":     "Empleo local",
            "canon_minero":     "Canon (MUSD)",
        }),
        use_container_width=True, hide_index=True,
        column_config={
            "Año":              st.column_config.NumberColumn("Año", format="%d"),
            "Producción (MUSD)":st.column_config.NumberColumn("Producción (MUSD)", format="%.1f"),
            "Inversión (MUSD)": st.column_config.NumberColumn("Inversión (MUSD)",  format="%.1f"),
            "Empleo local":     st.column_config.NumberColumn("Empleo local",       format="%d"),
            "Canon (MUSD)":     st.column_config.NumberColumn("Canon (MUSD)",       format="%.1f"),
        }
    )

st.markdown("""
<div class="footer">
  Indicador Multidimensional de Desempeño Minero · Perú 2020–2024 · Universidad del Pacífico
</div>""", unsafe_allow_html=True)
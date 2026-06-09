"""
=============================================================
  DASHBOARD PERIKANAN TANGKAP JAWA TIMUR 2020-2024
  Framework: Streamlit + Plotly
  Ilmu Kelautan - Universitas Jenderal Soedirman
=============================================================
  pip install streamlit plotly pandas numpy
  streamlit run dashboard_ikan_streamlit.py
=============================================================
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Perikanan Jawa Timur",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #EFF9FF; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 10px rgba(0,119,182,0.12);
    }
    h1 { color: #03045E !important; }
    .stSelectbox label, .stSlider label { font-weight: 600; color: #03045E; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("GABUNGAN 20-24.csv")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "Tahun"                              : "tahun",
        "Provinsi"                           : "provinsi",
        "Jenis Ikan"                         : "jenis_ikan",
        "Volume (ton)"                       : "volume_ton",
        "Nilai (Rp. Juta)"                   : "nilai_juta",
        "Harga Rata-Rata Tertimbang (Rp/kg)" : "harga_rp_kg",
    })
    df["jenis_ikan"] = df["jenis_ikan"].str.title().str.strip()
    return df

df = load_data()

TAHUN_LIST = sorted(df["tahun"].unique())
SEMUA_IKAN = sorted(df["jenis_ikan"].unique())
PALETTE    = px.colors.qualitative.Bold
SEA_BLUE   = "#0077B6"
DARK_BG    = "#03045E"

def _label(col):
    return {
        "volume_ton" : "Volume (ton)",
        "nilai_juta" : "Nilai (Rp. Juta)",
        "harga_rp_kg": "Harga (Rp/kg)",
    }[col]

# ── HEADER ────────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,#03045E,#0077B6);
            padding:20px 28px;border-radius:14px;margin-bottom:20px;
            display:flex;align-items:center;gap:14px">
  <span style="font-size:2.6rem">🐟</span>
  <div>
    <h2 style="margin:0;color:white;font-size:1.6rem;font-weight:800">
      Dashboard Perikanan Tangkap Jawa Timur</h2>
    <p style="margin:0;color:#ADE8F4;font-size:0.85rem">
      Produksi 2020–2024 &nbsp;•&nbsp; Volume · Nilai · Harga · Komposisi Spesies
      &nbsp;•&nbsp; <b style="color:#90E0EF">Ilmu Kelautan UNSOED</b></p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR FILTER ────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Filter Data")
    st.divider()

    tahun_range = st.slider(
        "📅 Rentang Tahun",
        min_value=min(TAHUN_LIST),
        max_value=max(TAHUN_LIST),
        value=(min(TAHUN_LIST), max(TAHUN_LIST)),
    )

    metrik = st.selectbox(
        "📊 Metrik Utama",
        options=["volume_ton", "nilai_juta", "harga_rp_kg"],
        format_func=_label,
    )

    topn = st.select_slider(
        "🏆 Top-N Spesies",
        options=[5, 10, 15, 20, 30],
        value=10,
    )

    sp_filter = st.multiselect(
        "🐠 Filter Spesies (opsional)",
        options=SEMUA_IKAN,
        placeholder="Semua spesies...",
    )

    st.divider()
    st.markdown("""
    <small style='color:#666'>
    📁 <b>GABUNGAN_20-24.csv</b><br>
    1.314 baris · 528 spesies<br>
    Jawa Timur · 2020–2024
    </small>
    """, unsafe_allow_html=True)

# ── FILTER DATA ───────────────────────────────────────────
mask = (df["tahun"] >= tahun_range[0]) & (df["tahun"] <= tahun_range[1])
if sp_filter:
    mask &= df["jenis_ikan"].isin(sp_filter)
dff = df[mask]

# ── KPI CARDS ─────────────────────────────────────────────
tot_vol = dff["volume_ton"].sum()
tot_val = dff["nilai_juta"].sum()
n_sp    = dff["jenis_ikan"].nunique()
avg_hrg = (dff["harga_rp_kg"] * dff["volume_ton"]).sum() / max(dff["volume_ton"].sum(), 1)

k1, k2, k3, k4 = st.columns(4)
k1.metric("⚖️ Total Volume",    f"{tot_vol:,.1f} ton")
k2.metric("💰 Total Nilai",     f"Rp {tot_val/1e3:,.1f} M")
k3.metric("🐠 Jumlah Spesies",  str(n_sp))
k4.metric("📈 Harga Rata-rata", f"Rp {avg_hrg:,.0f}/kg")

st.divider()

# ── ROW 1: TREN + DONUT ───────────────────────────────────
col1, col2 = st.columns([2.2, 1])

with col1:
    agg_tren = dff.groupby("tahun")[metrik].sum().reset_index()

    fig_tren = go.Figure()
    fig_tren.add_trace(go.Scatter(
        x=agg_tren["tahun"], y=agg_tren[metrik],
        mode="lines+markers+text",
        line=dict(color=SEA_BLUE, width=3),
        marker=dict(size=10, color=SEA_BLUE, line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(0,119,182,0.1)",
        text=[f"{v:,.0f}" for v in agg_tren[metrik]],
        textposition="top center",
        textfont=dict(size=11, color=DARK_BG),
        hovertemplate=f"<b>%{{x}}</b><br>{_label(metrik)}: %{{y:,.1f}}<extra></extra>",
    ))
    for i in range(1, len(agg_tren)):
        prev = agg_tren[metrik].iloc[i-1]
        curr = agg_tren[metrik].iloc[i]
        if prev > 0:
            pct = (curr - prev) / prev * 100
            clr = "#27AE60" if pct >= 0 else "#E74C3C"
            fig_tren.add_annotation(
                x=agg_tren["tahun"].iloc[i], y=curr * 0.5,
                text=f"<b>{'▲' if pct>=0 else '▼'}{abs(pct):.1f}%</b>",
                showarrow=False, font=dict(size=11, color=clr),
            )
    fig_tren.update_layout(
        title=dict(text=f"📈 Tren {_label(metrik)} per Tahun",
                   font=dict(size=15, color=DARK_BG)),
        xaxis=dict(tickmode="array", tickvals=list(TAHUN_LIST), showgrid=False),
        yaxis=dict(gridcolor="#e8f4f8", title=_label(metrik)),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=60, r=20, t=50, b=40),
        showlegend=False, height=340,
    )
    st.plotly_chart(fig_tren, use_container_width=True)

with col2:
    agg_sp = dff.groupby("jenis_ikan")[metrik].sum().sort_values(ascending=False)
    top    = agg_sp.head(topn).copy()
    rest   = agg_sp.iloc[topn:].sum()
    if rest > 0:
        top["Lainnya"] = rest

    fig_donut = px.pie(
        values=top.values, names=top.index,
        color_discrete_sequence=PALETTE, hole=0.48,
    )
    fig_donut.update_traces(
        textposition="outside",           # ← pindah label ke luar slice
        textinfo="label+percent",         # ← tampilkan nama + persen
        hovertemplate="<b>%{label}</b><br>%{value:,.1f} (%{percent})<extra></extra>",
        pull=[0.04] + [0]*(len(top)-1),
        textfont=dict(size=10),           # ← font lebih kecil biar tidak nabrak
    )
    fig_donut.update_layout(
        title=dict(text=f"🐠 Top {topn} Spesies<br><sup>by {_label(metrik)}</sup>",
                   font=dict(size=14, color=DARK_BG)),
        margin=dict(l=60, r=60, t=65, b=60),   # ← margin lebih lebar untuk label luar
        paper_bgcolor="white",
        showlegend=True,                         # ← legend dinyalakan
        legend=dict(
            orientation="v",
            font=dict(size=9),
            x=1.02, y=0.5,
        ),
        height=420,                              # ← lebih tinggi supaya tidak kepotong
        annotations=[dict(text=f"Top {topn}", x=.5, y=.5,
                          showarrow=False, font=dict(size=12, color="#555"))],
    )
    st.plotly_chart(fig_donut, use_container_width=True)
    

# ── ROW 2: BAR + SCATTER ──────────────────────────────────
col3, col4 = st.columns([1.4, 1])

with col3:
    agg_bar = dff.groupby(["jenis_ikan","tahun"])[metrik].sum().reset_index()
    top_sp  = (agg_bar.groupby("jenis_ikan")[metrik]
                      .sum().sort_values(ascending=False)
                      .head(topn).index.tolist())
    agg_bar = agg_bar[agg_bar["jenis_ikan"].isin(top_sp)]
    agg_bar["jenis_ikan"] = pd.Categorical(
        agg_bar["jenis_ikan"], categories=top_sp[::-1], ordered=True)
    agg_bar = agg_bar.sort_values("jenis_ikan")

    fig_bar = px.bar(
        agg_bar, y="jenis_ikan", x=metrik, color="tahun",
        orientation="h",
        color_discrete_sequence=px.colors.sequential.Blues[2:],
        barmode="group",
        labels={metrik:_label(metrik), "jenis_ikan":"", "tahun":"Tahun"},
    )
    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b> (%{legendgroup})<br>%{x:,.1f}<extra></extra>"
    )
    fig_bar.update_layout(
        title=dict(text=f"🏆 Top {topn} Spesies per Tahun",
                   font=dict(size=15, color=DARK_BG)),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=10, r=20, t=50, b=50),
        xaxis=dict(gridcolor="#e8f4f8"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.22,
                    xanchor="center", x=.5, title=""),
        height=max(380, topn*30),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col4:

    pareto = (
        dff.groupby("jenis_ikan")[metrik]
        .sum()
        .sort_values(ascending=False)
        .head(topn)
        .reset_index()
    )

    pareto["cum_pct"] = (
        pareto[metrik].cumsum() /
        pareto[metrik].sum() * 100
    )

    fig_pareto = go.Figure()

    fig_pareto.add_trace(
        go.Bar(
            x=pareto["jenis_ikan"],
            y=pareto[metrik],
            name=_label(metrik),
        )
    )

    fig_pareto.add_trace(
        go.Scatter(
            x=pareto["jenis_ikan"],
            y=pareto["cum_pct"],
            mode="lines+markers",
            name="Kumulatif (%)",
            yaxis="y2",
        )
    )

    fig_pareto.update_layout(
        title=f"📊 Pareto Top {topn} Spesies",
        xaxis_title="Jenis Ikan",
        yaxis_title=_label(metrik),
        yaxis2=dict(
            title="Persentase Kumulatif (%)",
            overlaying="y",
            side="right",
            range=[0,100]
        ),
        height=450
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

# ── ROW 3: STACKED AREA CHART ─────────────────────────────

st.markdown("---")

agg_area = (
    dff.groupby(["tahun", "jenis_ikan"])[metrik]
    .sum()
    .reset_index()
)

top_area = (
    agg_area.groupby("jenis_ikan")[metrik]
    .sum()
    .sort_values(ascending=False)
    .head(topn)
    .index
)

agg_area = agg_area[
    agg_area["jenis_ikan"].isin(top_area)
]

fig_area = px.area(
    agg_area,
    x="tahun",
    y=metrik,
    color="jenis_ikan",
    labels={
        "tahun":"Tahun",
        metrik:_label(metrik),
        "jenis_ikan":"Jenis Ikan"
    }
)

fig_area.update_layout(
    title=f"📈 Kontribusi Top {topn} Spesies per Tahun",
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=500,
    legend_title="Spesies"
)

st.plotly_chart(fig_area, use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────
st.divider()
st.markdown("""
<p style='text-align:center;color:#6c757d;font-size:0.78rem'>
Dashboard Perikanan Tangkap Jawa Timur 2020–2024 &nbsp;•&nbsp;
Ilmu Kelautan UNSOED &nbsp;•&nbsp; Data: GABUNGAN_20-24.csv
</p>
""", unsafe_allow_html=True)

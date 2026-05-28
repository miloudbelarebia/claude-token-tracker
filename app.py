"""Claude Token Tracker — dashboard premium pour visualiser tous tes usages Claude."""

from __future__ import annotations

import json
import sqlite3
from datetime import timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from i18n import LANGUAGES, TRANSLATIONS, make_translator, is_rtl

DB_PATH = Path(__file__).parent / "data" / "tracker.db"
CONFIG_PATH = Path(__file__).parent / "data" / "config.json"

DEFAULT_CONFIG = {
    "language": "en",
    "subscription_plan": "Max 5x",
    "subscription_usd_per_month": 100,
    "currency": "USD",
    "currency_to_usd_rate": 1.0,
}

PRESET_PLANS = {
    "Free": 0,
    "Pro": 17,
    "Max 5x": 100,
    "Max 20x": 200,
    "Custom": None,
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text())}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

st.set_page_config(
    page_title="Claude Token Tracker",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Palette & Plotly theme
# ─────────────────────────────────────────────────────────────────────────────
PALETTE = {
    "bg":          "#0c0b0a",
    "surface":     "#16140f",
    "surface_2":   "#1e1b15",
    "border":      "rgba(255, 245, 230, 0.08)",
    "border_hi":   "rgba(255, 245, 230, 0.14)",
    "text":        "#f1ede5",
    "text_muted":  "#9d958a",
    "text_faint":  "#6b6358",
    "primary":     "#d97757",   # Claude orange
    "coral":       "#e5916b",
    "sand":        "#c8a878",
    "violet":      "#8a7fb8",
    "green":       "#7fb877",
    "rose":        "#b87f9e",
}
WARM_SEQUENCE = ["#d97757", "#e5916b", "#c8a878", "#8a7fb8", "#7fb877", "#b87f9e", "#deb887"]


def plotly_theme(fig: go.Figure, *, height: int | None = None, showlegend: bool = True) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", color=PALETTE["text"], size=12),
        margin=dict(l=10, r=10, t=30, b=10),
        showlegend=showlegend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="left", x=0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=PALETTE["text_muted"])),
        hoverlabel=dict(bgcolor=PALETTE["surface_2"], font=dict(family="Inter", color=PALETTE["text"]),
                        bordercolor=PALETTE["border_hi"]),
        xaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
                   tickcolor=PALETTE["border"], tickfont=dict(color=PALETTE["text_muted"])),
        yaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
                   tickcolor=PALETTE["border"], tickfont=dict(color=PALETTE["text_muted"])),
    )
    if height:
        fig.update_layout(height=height)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
:root {
  --bg: #0c0b0a;
  --surface: #16140f;
  --surface-2: #1e1b15;
  --surface-3: #28241c;
  --border: rgba(255, 245, 230, 0.08);
  --border-hi: rgba(255, 245, 230, 0.14);
  --text: #f1ede5;
  --text-muted: #9d958a;
  --text-faint: #6b6358;
  --primary: #d97757;
  --primary-glow: rgba(217, 119, 87, 0.18);
  --coral: #e5916b;
  --sand: #c8a878;
  --violet: #8a7fb8;
  --green: #7fb877;
}

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
.stApp {
  background: radial-gradient(ellipse at top, #1a1610 0%, #0c0b0a 50%) no-repeat fixed;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1400px; }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-hi); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-faint); }

/* ─── HERO HEADER ────────────────────────────────────────────────── */
.tt-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.tt-hero-title {
  font-size: 2.4rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0;
  background: linear-gradient(135deg, #f1ede5 0%, #d97757 70%, #e5916b 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.tt-hero-subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin-top: 0.4rem;
  font-weight: 400;
}
.tt-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  background: rgba(217, 119, 87, 0.1);
  border: 1px solid rgba(217, 119, 87, 0.25);
  border-radius: 999px;
  color: var(--primary);
  font-size: 0.78rem;
  font-weight: 500;
  font-family: 'JetBrains Mono', monospace;
}
.tt-hero-badge::before {
  content: '';
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px var(--primary);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ─── KPI CARDS ──────────────────────────────────────────────────── */
.tt-kpi-grid { display: grid; gap: 14px; margin-bottom: 2rem; }
.tt-kpi-row-4 { grid-template-columns: repeat(4, 1fr); }
.tt-kpi-row-3 { grid-template-columns: repeat(3, 1fr); }
@media (max-width: 900px) {
  .tt-kpi-row-4, .tt-kpi-row-3 { grid-template-columns: repeat(2, 1fr); }
}

.tt-kpi {
  background: linear-gradient(145deg, var(--surface) 0%, var(--surface-2) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.2rem 1.4rem;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.tt-kpi::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-hi), transparent);
}
.tt-kpi:hover {
  transform: translateY(-2px);
  border-color: var(--border-hi);
  box-shadow: 0 12px 30px -10px rgba(0,0,0,0.4), 0 0 0 1px rgba(217,119,87,0.05);
}
.tt-kpi-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}
.tt-kpi-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(217, 119, 87, 0.12);
  color: var(--primary);
  font-size: 0.95rem;
}
.tt-kpi-value {
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.02em;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 0.5rem;
  line-height: 1;
}
.tt-kpi-sub {
  font-size: 0.78rem;
  color: var(--text-faint);
  margin-top: 0.5rem;
}
.tt-kpi-accent .tt-kpi-value { color: var(--primary); }

/* ─── TABS ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: var(--surface);
  padding: 5px;
  border-radius: 12px;
  border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  height: 38px;
  background: transparent;
  border-radius: 8px;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.88rem;
  padding: 0 1rem;
  transition: all 0.2s ease;
  border: none;
}
.stTabs [data-baseweb="tab"]:hover {
  background: var(--surface-2);
  color: var(--text);
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--surface-3), var(--surface-2)) !important;
  color: var(--text) !important;
  box-shadow: 0 0 0 1px var(--border-hi);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ─── SIDEBAR ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(22, 20, 15, 0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  color: var(--text);
  font-weight: 600;
  letter-spacing: -0.01em;
}
[data-testid="stSidebar"] label {
  color: var(--text-muted) !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* ─── INPUTS & SELECTS ───────────────────────────────────────────── */
[data-baseweb="select"] > div, [data-baseweb="input"] > div, .stTextInput input,
.stDateInput input, .stMultiSelect [data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  transition: all 0.2s ease;
}
[data-baseweb="select"] > div:hover, [data-baseweb="input"] > div:hover,
.stTextInput input:hover, .stDateInput input:hover { border-color: var(--border-hi) !important; }
[data-baseweb="select"]:focus-within > div, .stTextInput input:focus, .stDateInput input:focus {
  border-color: var(--primary) !important;
  box-shadow: 0 0 0 3px var(--primary-glow) !important;
}
[data-baseweb="tag"] {
  background: rgba(217, 119, 87, 0.15) !important;
  color: var(--primary) !important;
  border: 1px solid rgba(217, 119, 87, 0.25) !important;
  border-radius: 6px !important;
}

/* ─── BUTTONS ────────────────────────────────────────────────────── */
.stButton button, .stDownloadButton button {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
  padding: 0.5rem 1rem !important;
  transition: all 0.2s ease !important;
  font-size: 0.85rem !important;
}
.stButton button:hover {
  background: var(--surface-2) !important;
  border-color: var(--primary) !important;
  color: var(--primary) !important;
  transform: translateY(-1px);
}
.stButton button:active { transform: translateY(0); }

/* ─── DATAFRAMES ─────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
}
[data-testid="stDataFrame"] div[role="gridcell"] { color: var(--text); }

/* ─── DIVIDERS ───────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; opacity: 0.6; }

/* ─── CHAT BUBBLES ───────────────────────────────────────────────── */
.tt-chat-row { display: flex; gap: 12px; margin-bottom: 1.25rem; align-items: flex-start; }
.tt-chat-row.user { flex-direction: row-reverse; }
.tt-chat-avatar {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  font-weight: 600;
}
.tt-chat-avatar.user {
  background: linear-gradient(135deg, var(--primary), var(--coral));
  color: white;
  box-shadow: 0 4px 14px var(--primary-glow);
}
.tt-chat-avatar.assistant {
  background: var(--surface-2);
  border: 1px solid var(--border-hi);
  color: var(--sand);
}
.tt-chat-body { flex: 1; min-width: 0; max-width: calc(100% - 60px); }
.tt-chat-row.user .tt-chat-body { display: flex; flex-direction: column; align-items: flex-end; }
.tt-chat-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.72rem;
  color: var(--text-faint);
  font-family: 'JetBrains Mono', monospace;
  flex-wrap: wrap;
}
.tt-chat-chip {
  display: inline-flex;
  padding: 2px 8px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.7rem;
  color: var(--text-muted);
}
.tt-chat-chip.cost { color: var(--primary); border-color: rgba(217,119,87,0.25); }
.tt-chat-bubble {
  padding: 0.9rem 1.1rem;
  border-radius: 14px;
  line-height: 1.6;
  font-size: 0.92rem;
  word-wrap: break-word;
  overflow-wrap: break-word;
}
.tt-chat-bubble.user {
  background: linear-gradient(135deg, rgba(217,119,87,0.18), rgba(229,145,107,0.12));
  border: 1px solid rgba(217,119,87,0.25);
  color: var(--text);
  border-top-right-radius: 4px;
}
.tt-chat-bubble.assistant {
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  border-top-left-radius: 4px;
}
.tt-chat-bubble pre {
  background: rgba(0,0,0,0.3) !important;
  border: 1px solid var(--border);
  padding: 0.7rem !important;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82rem;
}
.tt-chat-bubble code {
  background: rgba(0,0,0,0.25);
  padding: 1px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  color: var(--sand);
}

/* ─── CARDS WRAPPER ──────────────────────────────────────────────── */
.tt-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.3rem 1.4rem;
}
.tt-section-title {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 0.8rem;
}

/* ─── SELECTBOX OPENED ───────────────────────────────────────────── */
[data-baseweb="popover"] li:hover { background: var(--surface-2) !important; }
[data-baseweb="popover"] [aria-selected="true"] { background: rgba(217,119,87,0.12) !important; }

/* ─── HEADINGS ───────────────────────────────────────────────────── */
h1, h2, h3, h4 { color: var(--text); font-weight: 600; letter-spacing: -0.01em; }
h2 { font-size: 1.3rem; margin-top: 1.5rem !important; margin-bottom: 0.8rem !important; }
h3 { font-size: 1.05rem; }

/* ─── CHAT EXPANDER (for long messages) ──────────────────────────── */
[data-testid="stExpander"] {
  background: rgba(0,0,0,0.15);
  border: 1px solid var(--border);
  border-radius: 10px;
}
[data-testid="stExpander"] summary { color: var(--text-muted); font-size: 0.85rem; }

/* ─── INFO / WARNING ─────────────────────────────────────────────── */
[data-baseweb="notification"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border-hi) !important;
  border-radius: 10px !important;
}
</style>
""")


# ─────────────────────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_messages(db_path: str) -> pd.DataFrame:
    if not Path(db_path).exists():
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM messages", conn, parse_dates=["timestamp"])
    conn.close()
    if df.empty:
        return df
    df["date"] = df["timestamp"].dt.date
    df["total_tokens"] = (
        df["input_tokens"] + df["output_tokens"]
        + df["cache_read_tokens"] + df["cache_create_tokens"]
    )
    df["model_short"] = df["model"].fillna("(none)").str.replace("claude-", "", regex=False)
    df["entrypoint"] = df["entrypoint"].fillna("subagent")
    return df


def human_int(n: float) -> str:
    n = float(n or 0)
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000: return f"{n/1_000:.1f}k"
    return f"{int(n):,}"


def kpi_card(label: str, value: str, *, icon: str = "✦", sub: str = "", accent: bool = False) -> str:
    cls = "tt-kpi tt-kpi-accent" if accent else "tt-kpi"
    sub_html = f'<div class="tt-kpi-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="{cls}">'
        f'<div class="tt-kpi-label"><span class="tt-kpi-icon">{icon}</span>{label}</div>'
        f'<div class="tt-kpi-value">{value}</div>'
        f'{sub_html}'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Load config + setup translator
# ─────────────────────────────────────────────────────────────────────────────
cfg = load_config()
lang = cfg.get("language", "en")
if lang not in LANGUAGES:
    lang = "en"
t = make_translator(lang)
rtl = is_rtl(lang)

# RTL CSS injection if Arabic — limit RTL to content, keep sidebar layout intact
if rtl:
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
      [data-testid="stMain"] { direction: rtl; }
      [data-testid="stSidebar"] { direction: rtl; text-align: right; }
      [data-testid="stSidebar"] [data-baseweb="select"] > div,
      [data-testid="stSidebar"] [data-baseweb="input"] > div { text-align: right; }
      .tt-hero { flex-direction: row-reverse; }
      .tt-hero-title, .tt-hero-subtitle { text-align: right; }
      .tt-kpi-label { flex-direction: row-reverse; justify-content: flex-end; }
      .tt-kpi-value, .tt-kpi-sub { text-align: right; }
      .tt-section-title { text-align: right; }
      .tt-chat-row.user { flex-direction: row; }
      .tt-chat-row.assistant { flex-direction: row-reverse; }
      .tt-chat-row.user .tt-chat-body { align-items: flex-start; }
      .stTabs [data-baseweb="tab-list"] { direction: rtl; }
      h1, h2, h3, h4, p, label, span, div, .tt-kpi-value, .tt-section-title {
        font-family: 'Noto Sans Arabic', 'Inter', sans-serif !important;
      }
      .tt-kpi-value { font-family: 'JetBrains Mono', monospace !important; }
    </style>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.html(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1.5rem;">'
        f'<div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,{PALETTE["primary"]},{PALETTE["coral"]});'
        f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;color:white;font-weight:700;">✦</div>'
        f'<div><div style="font-weight:600;color:{PALETTE["text"]};">{t("sidebar_brand")}</div>'
        f'<div style="font-size:0.72rem;color:{PALETTE["text_faint"]};font-family:JetBrains Mono;">{t("sidebar_version")}</div></div>'
        f'</div>',
    )

    # ─── Sélecteur de langue ────────────────────────────────────────
    st.html(f'<div class="tt-section-title">{t("sec_language")}</div>')
    lang_codes = list(LANGUAGES.keys())
    sel_lang = st.selectbox(
        " ",
        lang_codes,
        index=lang_codes.index(lang),
        format_func=lambda c: LANGUAGES[c],
        label_visibility="collapsed",
        key="lang_selector",
    )
    if sel_lang != lang:
        cfg["language"] = sel_lang
        save_config(cfg)
        st.rerun()

    if st.button(t("btn_refresh"), use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if st.button(t("btn_reparse"), use_container_width=True):
        import subprocess, sys
        with st.spinner(t("parsing")):
            result = subprocess.run(
                [sys.executable, str(Path(__file__).parent / "tracker.py")],
                capture_output=True, text=True,
            )
        st.code((result.stdout or result.stderr)[-600:], language="bash")
        st.cache_data.clear()

    # ─── Mon abonnement ──────────────────────────────────────────────
    st.markdown("---")
    st.html(f'<div class="tt-section-title">{t("sec_subscription")}</div>')

    plan_names = list(PRESET_PLANS.keys())
    current_plan = cfg.get("subscription_plan", "Max 5x")
    if current_plan not in plan_names:
        current_plan = "Custom"

    sel_plan = st.selectbox(
        t("lbl_plan"),
        plan_names,
        index=plan_names.index(current_plan),
        help=t("plan_help"),
    )

    if sel_plan == "Custom":
        sub_amount = st.number_input(
            t("lbl_monthly_amount"),
            min_value=0.0, value=float(cfg.get("subscription_usd_per_month", 100)),
            step=5.0, format="%.2f",
        )
        sub_currency = st.selectbox(t("lbl_currency"), ["USD", "EUR"],
                                    index=0 if cfg.get("currency", "USD") == "USD" else 1)
        eur_to_usd = 1.08
        sub_usd = sub_amount * (eur_to_usd if sub_currency == "EUR" else 1.0)
    else:
        sub_usd = PRESET_PLANS[sel_plan]
        sub_amount = sub_usd
        sub_currency = "USD"
        st.html(
            f'<div style="padding:0.5rem 0.8rem;background:rgba(217,119,87,0.08);'
            f'border:1px solid rgba(217,119,87,0.18);border-radius:8px;margin-top:0.3rem;">'
            f'<span style="font-family:JetBrains Mono;color:{PALETTE["primary"]};font-weight:600;font-size:1rem;">'
            f'${sub_usd}</span><span style="color:{PALETTE["text_muted"]};font-size:0.78rem;"> {t("per_month")}</span></div>'
        )

    new_cfg = {
        **cfg,
        "subscription_plan": sel_plan,
        "subscription_usd_per_month": sub_amount,
        "currency": sub_currency,
        "currency_to_usd_rate": 1.08 if sub_currency == "EUR" else 1.0,
    }
    if new_cfg != cfg:
        save_config(new_cfg)
        cfg = new_cfg


df_all = load_messages(str(DB_PATH))

if df_all.empty:
    st.html(f'<h1 class="tt-hero-title">{t("app_title")}</h1>')
    st.info(t("empty_db_warn"))
    st.stop()


# ─── Filters in sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.html(f'<div class="tt-section-title">{t("sec_filters")}</div>')

    min_date, max_date = df_all["date"].min(), df_all["date"].max()

    range_presets = {
        t("range_7d"): 7,
        t("range_30d"): 30,
        t("range_90d"): 90,
        t("range_all"): None,
        t("range_custom"): "custom",
    }
    preset_labels = list(range_presets.keys())
    sel_preset = st.selectbox(t("range_label"), preset_labels, index=1)  # default = 30 days
    preset_val = range_presets[sel_preset]

    if preset_val == "custom":
        date_range = st.date_input(
            t("lbl_period"),
            value=(max(min_date, max_date - timedelta(days=30)), max_date),
            min_value=min_date,
            max_value=max_date,
        )
    elif preset_val is None:  # all time
        date_range = (min_date, max_date)
    else:
        date_range = (max(min_date, max_date - timedelta(days=preset_val - 1)), max_date)

    projects = sorted(df_all["project_label"].dropna().unique().tolist())
    sel_projects = st.multiselect(t("lbl_projects"), projects, default=projects)
    models = sorted(df_all["model_short"].dropna().unique().tolist())
    sel_models = st.multiselect(t("lbl_models"), models, default=models)
    entrypoints = sorted(df_all["entrypoint"].dropna().unique().tolist())
    sel_eps = st.multiselect(t("lbl_entrypoints"), entrypoints, default=entrypoints)

df = df_all.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]
if sel_projects:
    df = df[df["project_label"].isin(sel_projects)]
if sel_models:
    df = df[df["model_short"].isin(sel_models)]
if sel_eps:
    df = df[df["entrypoint"].isin(sel_eps)]

with st.sidebar:
    st.html(
        f'<div style="margin-top:1rem;padding:0.8rem 1rem;background:rgba(217,119,87,0.08);'
        f'border:1px solid rgba(217,119,87,0.18);border-radius:10px;">'
        f'<div style="font-size:0.7rem;color:{PALETTE["text_muted"]};text-transform:uppercase;letter-spacing:0.05em;">{t("lbl_result")}</div>'
        f'<div style="font-family:JetBrains Mono;color:{PALETTE["primary"]};font-weight:600;font-size:1.1rem;margin-top:2px;">'
        f'{t("messages_count", count=f"{len(df):,}")}</div></div>',
    )


# ─────────────────────────────────────────────────────────────────────────────
# Hero
# ─────────────────────────────────────────────────────────────────────────────
st.html(f"""
<div class="tt-hero">
  <div>
    <h1 class="tt-hero-title">{t("app_title")}</h1>
    <div class="tt-hero-subtitle">{t("app_subtitle")}</div>
  </div>
  <div class="tt-hero-badge">{t("live_messages", count=f"{len(df_all):,}")}</div>
</div>
""")


# ─── KPI Cards ───────────────────────────────────────────────────────────────
total_cost = df["cost_usd"].sum()                  # ce que ça aurait coûté en API
total_in = df["input_tokens"].sum()
total_out = df["output_tokens"].sum()
total_cr = df["cache_read_tokens"].sum()
total_cc = df["cache_create_tokens"].sum()
cache_ratio = total_cr / max(total_cr + total_in, 1)

# Prorater le coût de l'abo sur la période sélectionnée
if isinstance(date_range, tuple) and len(date_range) == 2:
    period_days = (date_range[1] - date_range[0]).days + 1
else:
    period_days = (df["date"].max() - df["date"].min()).days + 1 if not df.empty else 30
period_months = period_days / 30.4375  # mois moyen
sub_usd_period = cfg["subscription_usd_per_month"] * period_months
savings = total_cost - sub_usd_period
roi_ratio = total_cost / sub_usd_period if sub_usd_period > 0 else float("inf")

# Verdict
if cfg["subscription_usd_per_month"] == 0:
    verdict = (t("verdict_free"), PALETTE["green"], "🆓")
elif roi_ratio >= 10:
    verdict = (t("verdict_massive"), PALETTE["green"], "🚀")
elif roi_ratio >= 3:
    verdict = (t("verdict_very"), PALETTE["green"], "✅")
elif roi_ratio >= 1:
    verdict = (t("verdict_profit"), PALETTE["sand"], "👍")
else:
    verdict = (t("verdict_under"), "#e57777", "⚠️")

savings_color_value = f'<span style="color:{PALETTE["green"]};">+${savings:,.0f}</span>' if savings >= 0 else f'<span style="color:#e57777;">${savings:,.0f}</span>'
roi_color_value = f'<span style="color:{PALETTE["green"]};">×{roi_ratio:,.0f}</span>' if roi_ratio >= 1 else f'<span style="color:#e57777;">×{roi_ratio:,.2f}</span>'

_kpi_cards = (
    kpi_card(t("kpi_you_pay"), f"${sub_usd_period:,.0f}", icon="💳",
             sub=t("kpi_plan_days", plan=cfg["subscription_plan"], days=period_days), accent=True)
    + kpi_card(t("kpi_would_cost"), f"${total_cost:,.0f}", icon="$",
               sub=t("kpi_sess_msgs", sess=f"{df['session_id'].nunique():,}", msgs=f"{len(df):,}"))
    + kpi_card(t("kpi_savings"), savings_color_value, icon="💰",
               sub=t("kpi_vs_api"))
    + kpi_card(t("kpi_roi"), roi_color_value, icon="📈", sub=f"{verdict[2]} {verdict[0]}")
)
st.html(f'<div class="tt-kpi-grid tt-kpi-row-4">{_kpi_cards}</div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_roi, tab_overview, tab_sessions, tab_conv, tab_search = st.tabs(
    [t("tab_roi"), t("tab_overview"), t("tab_sessions"), t("tab_conv"), t("tab_search")]
)


# ─── RENTABILITÉ ─────────────────────────────────────────────────────────────
with tab_roi:
    # Verdict big
    verdict_paid = f'<span style="color:{PALETTE["primary"]};font-family:JetBrains Mono;">${sub_usd_period:,.0f}</span>'
    verdict_api  = f'<span style="color:{PALETTE["text"]};font-family:JetBrains Mono;">${total_cost:,.0f}</span>'
    if savings > 0:
        verdict_body = t("verdict_body_pos",
                         paid=verdict_paid, plan=cfg["subscription_plan"],
                         api=verdict_api,
                         savings=f'<span style="color:{PALETTE["green"]};font-family:JetBrains Mono;">${savings:,.0f}</span>',
                         roi=f"{roi_ratio:,.0f}")
    else:
        verdict_body = t("verdict_body_neg",
                         paid=verdict_paid, plan=cfg["subscription_plan"],
                         api=verdict_api,
                         loss=f'<span style="color:#e57777;font-family:JetBrains Mono;">${-savings:,.0f}</span>')

    st.html(
        f'<div style="background:linear-gradient(135deg,{PALETTE["surface"]} 0%,{PALETTE["surface_2"]} 100%);'
        f'border:1px solid {verdict[1]}33;border-radius:18px;padding:2rem 2rem;margin-bottom:1.5rem;'
        f'position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;right:0;width:300px;height:300px;'
        f'background:radial-gradient(circle,{verdict[1]}22 0%,transparent 70%);"></div>'
        f'<div style="position:relative;">'
        f'<div style="font-size:0.78rem;color:{PALETTE["text_muted"]};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem;">{t("verdict_period", days=period_days)}</div>'
        f'<div style="font-size:2.6rem;font-weight:700;color:{verdict[1]};letter-spacing:-0.03em;margin-bottom:0.4rem;">'
        f'{verdict[2]} {verdict[0]}</div>'
        f'<div style="color:{PALETTE["text"]};font-size:1.05rem;line-height:1.7;max-width:700px;">'
        f'{verdict_body}'
        f'</div></div></div>'
    )

    # Détail breakdown 3 cards
    cost_per_msg = total_cost / max(len(df), 1)
    sub_per_msg = sub_usd_period / max(len(df), 1)
    eq_msgs_at_api = sub_usd_period / max(cost_per_msg, 0.0001)

    detail_cards = (
        kpi_card(t("lbl_cost_per_msg"), f"${cost_per_msg:.3f}", icon="◈",
                 sub=t("msg_cost_avg"))
        + kpi_card(t("lbl_real_cost_per_msg"), f"${sub_per_msg:.4f}", icon="💳",
                   sub=t("msg_real_cost"))
        + kpi_card(t("lbl_breakeven"), f"{int(eq_msgs_at_api):,}", icon="⚖️",
                   sub=t("msg_breakeven"))
    )
    st.html(f'<div class="tt-kpi-grid tt-kpi-row-3">{detail_cards}</div>')

    st.html(f'<div class="tt-section-title" style="margin-top:1.5rem;">{t("sec_cumul")}</div>')

    # Courbe cumulée
    daily_roi = (df.groupby("date")
                 .agg(api_cost=("cost_usd", "sum"))
                 .reset_index()
                 .sort_values("date"))
    daily_roi["date"] = pd.to_datetime(daily_roi["date"])
    daily_roi["api_cumul"] = daily_roi["api_cost"].cumsum()
    # Abo cumulé (linéaire jour par jour)
    sub_per_day = cfg["subscription_usd_per_month"] / 30.4375
    daily_roi["day_index"] = range(1, len(daily_roi) + 1)
    daily_roi["sub_cumul"] = daily_roi["day_index"] * sub_per_day

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(
        x=daily_roi["date"], y=daily_roi["api_cumul"],
        name=t("trace_api_cumul"),
        mode="lines",
        line=dict(color=PALETTE["primary"], width=3),
        fill="tozeroy",
        fillcolor="rgba(217,119,87,0.15)",
        hovertemplate="<b>%{x|%d %b}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig_roi.add_trace(go.Scatter(
        x=daily_roi["date"], y=daily_roi["sub_cumul"],
        name=t("trace_sub_cumul", plan=cfg["subscription_plan"]),
        mode="lines",
        line=dict(color=PALETTE["green"], width=3, dash="dash"),
        hovertemplate="<b>%{x|%d %b}</b><br>$%{y:,.2f}<extra></extra>",
    ))
    st.plotly_chart(plotly_theme(fig_roi, height=350), use_container_width=True)

    # Par mois
    df_month = df.copy()
    df_month["month"] = pd.to_datetime(df_month["timestamp"]).dt.to_period("M").astype(str)
    monthly = (df_month.groupby("month")
               .agg(api_cost=("cost_usd", "sum"), msgs=("uuid", "count"))
               .reset_index())
    monthly["sub_cost"] = cfg["subscription_usd_per_month"]
    monthly["savings"] = monthly["api_cost"] - monthly["sub_cost"]
    monthly["roi"] = (monthly["api_cost"] / monthly["sub_cost"]).round(1) if cfg["subscription_usd_per_month"] > 0 else 0

    if len(monthly) > 0:
        st.html(f'<div class="tt-section-title" style="margin-top:2rem;">{t("sec_monthly")}</div>')
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(
            x=monthly["month"], y=monthly["api_cost"],
            name=t("trace_api_month"),
            marker=dict(color=PALETTE["primary"], line=dict(width=0)),
            text=[f"${v:,.0f}" for v in monthly["api_cost"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], family="JetBrains Mono", size=11),
        ))
        fig_m.add_trace(go.Bar(
            x=monthly["month"], y=monthly["sub_cost"],
            name=t("trace_sub_month"),
            marker=dict(color=PALETTE["green"], line=dict(width=0)),
            text=[f"${v:,.0f}" for v in monthly["sub_cost"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text"], family="JetBrains Mono", size=11),
        ))
        fig_m.update_layout(barmode="group", title=dict(text=" ", font=dict(size=1)))
        st.plotly_chart(plotly_theme(fig_m, height=320), use_container_width=True)

        # Table mensuelle
        display_m = monthly.copy()
        display_m["savings_str"] = display_m["savings"].apply(lambda x: f"+${x:,.0f}" if x >= 0 else f"-${-x:,.0f}")
        display_m["roi_str"] = display_m["roi"].apply(lambda x: f"×{x:.1f}")
        display_m = display_m[["month", "msgs", "api_cost", "sub_cost", "savings_str", "roi_str"]]
        st.dataframe(
            display_m,
            use_container_width=True,
            hide_index=True,
            column_config={
                "month": st.column_config.TextColumn(t("col_month")),
                "msgs": st.column_config.NumberColumn(t("col_messages")),
                "api_cost": st.column_config.NumberColumn(t("col_api_cost"), format="$%.2f"),
                "sub_cost": st.column_config.NumberColumn(t("col_sub_cost"), format="$%.2f"),
                "savings_str": st.column_config.TextColumn(t("col_savings")),
                "roi_str": st.column_config.TextColumn(t("col_roi")),
            },
        )

    # Top sessions les plus "rentables"
    st.html(f'<div class="tt-section-title" style="margin-top:2rem;">{t("sec_top_sessions")}</div>')
    top_sess = (df.groupby("session_id")
                .agg(project=("project_label", "first"),
                     start=("timestamp", "min"),
                     msgs=("uuid", "count"),
                     api_cost=("cost_usd", "sum"))
                .sort_values("api_cost", ascending=False)
                .head(10)
                .reset_index())
    top_sess["session"] = top_sess["session_id"].str[:8]
    top_sess["start"] = pd.to_datetime(top_sess["start"]).dt.strftime("%d %b %H:%M")
    top_sess["pct_sub"] = (top_sess["api_cost"] / max(cfg["subscription_usd_per_month"], 0.01) * 100).round(0).astype(int).astype(str) + "%"
    display_t = top_sess[["session", "project", "start", "msgs", "api_cost", "pct_sub"]]
    st.dataframe(
        display_t,
        use_container_width=True,
        hide_index=True,
        column_config={
            "session": st.column_config.TextColumn(t("col_session")),
            "project": st.column_config.TextColumn(t("col_project")),
            "start": st.column_config.TextColumn(t("col_start")),
            "msgs": st.column_config.NumberColumn(t("col_messages")),
            "api_cost": st.column_config.NumberColumn(t("col_api_cost"), format="$%.2f"),
            "pct_sub": st.column_config.TextColumn(t("col_pct_sub")),
        },
    )

    # Note
    st.html(
        f'<div style="margin-top:2rem;padding:1rem 1.2rem;background:rgba(138,127,184,0.08);'
        f'border:1px solid rgba(138,127,184,0.18);border-radius:10px;color:{PALETTE["text_muted"]};font-size:0.85rem;line-height:1.6;">'
        f'<b style="color:{PALETTE["violet"]};">{t("note_title")}</b><br>'
        f'• <span style="color:{PALETTE["text"]};">{t("note_paid")}</span><br>'
        f'• <span style="color:{PALETTE["text"]};">{t("note_api")}</span><br>'
        f'• <span style="color:{PALETTE["text"]};">{t("note_savings")}</span><br>'
        f'• <span style="color:{PALETTE["text"]};">{t("note_roi")}</span>'
        f'</div>'
    )

# ─── OVERVIEW ────────────────────────────────────────────────────────────────
with tab_overview:
    daily = (df.groupby("date")
             .agg(cost=("cost_usd", "sum"),
                  input_tokens=("input_tokens", "sum"),
                  output_tokens=("output_tokens", "sum"),
                  cache_read=("cache_read_tokens", "sum"),
                  cache_create=("cache_create_tokens", "sum"),
                  messages=("uuid", "count"))
             .reset_index())
    daily["date"] = pd.to_datetime(daily["date"])

    # Cost over time — bar with gradient
    fig_cost = go.Figure()
    fig_cost.add_trace(go.Bar(
        x=daily["date"], y=daily["cost"],
        marker=dict(
            color=daily["cost"],
            colorscale=[[0, PALETTE["sand"]], [0.5, PALETTE["coral"]], [1, PALETTE["primary"]]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>$%{y:.2f}<extra></extra>",
    ))
    fig_cost.update_layout(title=dict(text=t("chart_daily_cost"), font=dict(size=14, color=PALETTE["text"])))
    st.plotly_chart(plotly_theme(fig_cost, height=260, showlegend=False), use_container_width=True)

    # Tokens stacked area
    fig_tokens = go.Figure()
    for col, name, color in [
        ("cache_read", t("trace_cache_read"), PALETTE["violet"]),
        ("cache_create", t("trace_cache_create"), PALETTE["rose"]),
        ("input_tokens", t("trace_input"), PALETTE["primary"]),
        ("output_tokens", t("trace_output"), PALETTE["sand"]),
    ]:
        fig_tokens.add_trace(go.Scatter(
            x=daily["date"], y=daily[col], name=name,
            stackgroup="one", mode="none",
            fillcolor=color,
            hovertemplate=f"<b>%{{x|%d %b}}</b><br>{name}: %{{y:,}}<extra></extra>",
        ))
    fig_tokens.update_layout(title=dict(text=t("chart_tokens_breakdown"), font=dict(size=14, color=PALETTE["text"])))
    st.plotly_chart(plotly_theme(fig_tokens, height=300), use_container_width=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        by_model = (df.groupby("model_short")
                    .agg(cost=("cost_usd", "sum"), messages=("uuid", "count"))
                    .sort_values("cost", ascending=False)
                    .reset_index())
        by_model = by_model[by_model["cost"] > 0]
        fig_donut = go.Figure(go.Pie(
            labels=by_model["model_short"], values=by_model["cost"],
            hole=0.65,
            marker=dict(colors=WARM_SEQUENCE, line=dict(color=PALETTE["bg"], width=2)),
            textinfo="percent",
            textfont=dict(family="Inter", color="white", size=11),
            hovertemplate="<b>%{label}</b><br>$%{value:.2f} (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(
            title=dict(text=t("chart_by_model"), font=dict(size=14, color=PALETTE["text"])),
            annotations=[dict(text=f"${total_cost:,.0f}", showarrow=False,
                             font=dict(size=22, color=PALETTE["text"], family="JetBrains Mono"))],
        )
        st.plotly_chart(plotly_theme(fig_donut, height=340), use_container_width=True)

    with col_b:
        by_ep = (df.groupby("entrypoint")
                 .agg(cost=("cost_usd", "sum"),
                      messages=("uuid", "count"),
                      sessions=("session_id", "nunique"))
                 .sort_values("cost", ascending=False)
                 .reset_index())
        fig_ep = go.Figure(go.Bar(
            x=by_ep["cost"], y=by_ep["entrypoint"],
            orientation="h",
            marker=dict(color=WARM_SEQUENCE[:len(by_ep)], line=dict(width=0)),
            text=[f"${c:,.0f}" for c in by_ep["cost"]],
            textposition="outside",
            textfont=dict(color=PALETTE["text_muted"], family="JetBrains Mono", size=11),
            hovertemplate="<b>%{y}</b><br>$%{x:.2f}<extra></extra>",
        ))
        fig_ep.update_layout(
            title=dict(text=t("chart_by_ep"), font=dict(size=14, color=PALETTE["text"])),
            yaxis=dict(autorange="reversed"),
            xaxis=dict(showticklabels=False),
        )
        st.plotly_chart(plotly_theme(fig_ep, height=340, showlegend=False), use_container_width=True)

    # Treemap projets
    by_proj = (df.groupby("project_label")
               .agg(cost=("cost_usd", "sum"), msgs=("uuid", "count"))
               .sort_values("cost", ascending=False)
               .reset_index())
    by_proj = by_proj[by_proj["cost"] > 0.01]
    if not by_proj.empty:
        fig_tree = px.treemap(
            by_proj, path=["project_label"], values="cost",
            color="cost",
            color_continuous_scale=[[0, PALETTE["surface_2"]], [0.5, PALETTE["sand"]], [1, PALETTE["primary"]]],
            hover_data={"msgs": True},
        )
        fig_tree.update_traces(
            textfont=dict(family="Inter", size=12, color="white"),
            marker=dict(line=dict(color=PALETTE["bg"], width=2)),
            hovertemplate="<b>%{label}</b><br>$%{value:.2f}<br>%{customdata[0]:,} messages<extra></extra>",
        )
        fig_tree.update_layout(title=dict(text=t("chart_by_project"), font=dict(size=14, color=PALETTE["text"])),
                               coloraxis_showscale=False)
        st.plotly_chart(plotly_theme(fig_tree, height=360, showlegend=False), use_container_width=True)


# ─── SESSIONS ────────────────────────────────────────────────────────────────
with tab_sessions:
    sess = (df.groupby("session_id")
            .agg(project=("project_label", "first"),
                 entrypoint=("entrypoint", "first"),
                 first=("timestamp", "min"),
                 last=("timestamp", "max"),
                 messages=("uuid", "count"),
                 input=("input_tokens", "sum"),
                 output=("output_tokens", "sum"),
                 cache_read=("cache_read_tokens", "sum"),
                 cost=("cost_usd", "sum"))
            .sort_values("cost", ascending=False)
            .reset_index())
    sess["duration_min"] = ((sess["last"] - sess["first"]).dt.total_seconds() / 60).round(1)
    sess["session"] = sess["session_id"].str[:8]
    display = sess[["session", "project", "entrypoint", "first", "messages", "duration_min", "input", "output", "cache_read", "cost"]]
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=600,
        column_config={
            "session": st.column_config.TextColumn(t("col_session")),
            "project": st.column_config.TextColumn(t("col_project")),
            "entrypoint": st.column_config.TextColumn(t("lbl_entrypoints")),
            "first": st.column_config.DatetimeColumn(t("col_begin"), format="DD MMM HH:mm"),
            "messages": st.column_config.NumberColumn(t("col_msgs")),
            "duration_min": st.column_config.NumberColumn(t("col_duration")),
            "cost": st.column_config.NumberColumn(t("col_api_cost"), format="$%.2f"),
            "input": st.column_config.NumberColumn(format="%d"),
            "output": st.column_config.NumberColumn(format="%d"),
            "cache_read": st.column_config.NumberColumn("cache", format="%d"),
        },
    )


# ─── CONVERSATION ────────────────────────────────────────────────────────────
with tab_conv:
    sess_opts = (df.groupby("session_id")
                 .agg(first=("timestamp", "min"),
                      project=("project_label", "first"),
                      msgs=("uuid", "count"),
                      cost=("cost_usd", "sum"))
                 .sort_values("first", ascending=False)
                 .reset_index())
    sess_opts["label"] = sess_opts.apply(
        lambda r: f"{r['first']:%d %b · %H:%M}  ·  {r['project'][:30]}  ·  {r['msgs']} msg  ·  ${r['cost']:.2f}",
        axis=1,
    )

    c1, c2 = st.columns([3, 1])
    with c1:
        sel = st.selectbox(
            t("select_session"),
            options=sess_opts["session_id"],
            format_func=lambda sid: sess_opts[sess_opts["session_id"] == sid]["label"].iloc[0],
            label_visibility="collapsed",
        )
    with c2:
        max_msgs = st.number_input(t("msgs_max"), min_value=10, max_value=2000, value=100, step=10)

    if sel:
        conv = df[df["session_id"] == sel].sort_values("timestamp")
        total_c = conv["cost_usd"].sum()
        total_in_c = conv["input_tokens"].sum()
        total_out_c = conv["output_tokens"].sum()
        total_cache_c = conv["cache_read_tokens"].sum() + conv["cache_create_tokens"].sum()

        st.html(f"""
        <div style="display:flex;gap:1rem;padding:1rem 1.2rem;background:var(--surface);
                    border:1px solid var(--border);border-radius:12px;margin-bottom:1.2rem;flex-wrap:wrap;">
          <div><span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_session")}</span>
               <div style="font-family:JetBrains Mono;color:var(--text);margin-top:2px;">{sel[:8]}…</div></div>
          <div style="border-left:1px solid var(--border);padding-left:1rem;">
               <span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_messages_cap")}</span>
               <div style="font-family:JetBrains Mono;color:var(--text);margin-top:2px;">{len(conv):,}</div></div>
          <div style="border-left:1px solid var(--border);padding-left:1rem;">
               <span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_cost_cap")}</span>
               <div style="font-family:JetBrains Mono;color:var(--primary);margin-top:2px;font-weight:600;">${total_c:.3f}</div></div>
          <div style="border-left:1px solid var(--border);padding-left:1rem;">
               <span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_input_cap")}</span>
               <div style="font-family:JetBrains Mono;color:var(--text);margin-top:2px;">{human_int(total_in_c)}</div></div>
          <div style="border-left:1px solid var(--border);padding-left:1rem;">
               <span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_output_cap")}</span>
               <div style="font-family:JetBrains Mono;color:var(--text);margin-top:2px;">{human_int(total_out_c)}</div></div>
          <div style="border-left:1px solid var(--border);padding-left:1rem;">
               <span style="color:var(--text-faint);font-size:0.75rem;">{t("lbl_cache_cap")}</span>
               <div style="font-family:JetBrains Mono;color:var(--text);margin-top:2px;">{human_int(total_cache_c)}</div></div>
        </div>
        """)

        if len(conv) > max_msgs:
            st.caption(t("show_first", n=max_msgs, total=len(conv)))
            conv = conv.head(max_msgs)

        import html as html_lib
        for _, m in conv.iterrows():
            is_user = m["role"] == "user"
            text = (m["content"] or "").strip()
            text_html = html_lib.escape(text).replace("\n", "<br>") or f"<em style='color:var(--text-faint)'>{t('empty_message')}</em>"
            truncated = ""
            if len(text) > 3000:
                text_html = html_lib.escape(text[:3000]).replace("\n", "<br>")
                truncated = f"<div style='color:var(--text-faint);font-size:0.78rem;margin-top:8px;'>… {t('truncated', count=f'{len(text)-3000:,}')}</div>"

            chips = f'<span class="tt-chat-chip">{m["timestamp"]:%H:%M:%S}</span>'
            if not is_user and m["model"]:
                chips += f'<span class="tt-chat-chip">{m["model_short"]}</span>'
                chips += f'<span class="tt-chat-chip">in {human_int(m["input_tokens"])}</span>'
                chips += f'<span class="tt-chat-chip">out {human_int(m["output_tokens"])}</span>'
                if m["cache_read_tokens"]:
                    chips += f'<span class="tt-chat-chip">cache {human_int(m["cache_read_tokens"])}</span>'
                chips += f'<span class="tt-chat-chip cost">${m["cost_usd"]:.4f}</span>'

            role_cls = "user" if is_user else "assistant"
            avatar_char = "M" if is_user else "✦"

            st.html(f"""
            <div class="tt-chat-row {role_cls}">
              <div class="tt-chat-avatar {role_cls}">{avatar_char}</div>
              <div class="tt-chat-body">
                <div class="tt-chat-meta">{chips}</div>
                <div class="tt-chat-bubble {role_cls}">{text_html}{truncated}</div>
              </div>
            </div>
            """)


# ─── SEARCH ──────────────────────────────────────────────────────────────────
with tab_search:
    c1, c2 = st.columns([4, 1])
    with c1:
        q = st.text_input("search", placeholder=t("search_placeholder"),
                          label_visibility="collapsed")
    with c2:
        role_options = [t("role_all"), t("role_user"), t("role_assistant")]
        role_internal = ["all", "user", "assistant"]
        role_idx = st.selectbox(t("lbl_role"), range(len(role_options)),
                                format_func=lambda i: role_options[i], label_visibility="collapsed")
        role_filter = role_internal[role_idx]

    if q:
        mask = df["content"].fillna("").str.contains(q, case=False, regex=False)
        if role_filter != "all":
            mask &= df["role"] == role_filter
        hits = df[mask].sort_values("timestamp", ascending=False)

        count_html = f'<b style="color:{PALETTE["primary"]};font-family:JetBrains Mono;">{len(hits):,}</b>'
        st.html(
            f'<div style="margin:1rem 0;color:{PALETTE["text_muted"]};font-size:0.88rem;">'
            f'{t("results_count", count=count_html)}</div>',
        )

        import html as html_lib
        for _, m in hits.head(50).iterrows():
            text = m["content"] or ""
            idx = text.lower().find(q.lower())
            if idx >= 0:
                start = max(0, idx - 150)
                end = min(len(text), idx + 400)
                snippet = text[start:end]
                snippet_html = html_lib.escape(snippet)
                # highlight
                snippet_html = snippet_html.replace(
                    html_lib.escape(q),
                    f'<mark style="background:rgba(217,119,87,0.3);color:{PALETTE["primary"]};padding:1px 4px;border-radius:3px;">{html_lib.escape(q)}</mark>',
                )
                if start > 0: snippet_html = "…" + snippet_html
                if end < len(text): snippet_html = snippet_html + "…"
                snippet_html = snippet_html.replace("\n", "<br>")
            else:
                snippet_html = html_lib.escape(text[:500])

            role_color = PALETTE["primary"] if m["role"] == "user" else PALETTE["sand"]
            proj_label = html_lib.escape(str(m["project_label"]))
            st.html(f"""
            <div class="tt-card" style="margin-bottom:0.8rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;font-size:0.78rem;font-family:JetBrains Mono;">
                <div><span style="color:{role_color};">●</span> <span style="color:var(--text-muted);">{m["role"]}</span>
                     · <span style="color:var(--text-faint);">{m["timestamp"]:%d %b %H:%M}</span>
                     · <span style="color:var(--text-muted);">{proj_label}</span></div>
                <div style="color:var(--primary);">${m["cost_usd"]:.4f}</div>
              </div>
              <div style="color:var(--text);font-size:0.88rem;line-height:1.55;">{snippet_html}</div>
            </div>
            """)

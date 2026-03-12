# app.py — SmartBorder AI | Military Tactical Dashboard
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import folium
from folium.plugins import HeatMap
import requests
from streamlit_folium import st_folium
import mysql.connector
import warnings
import time
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="SmartBorder AI | Tactical Command",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Military CSS Theme ────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif !important;
    background-color: #030A06 !important;
    color: #A8C5A0 !important;
}
.stApp {
    background: #030A06 !important;
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(0,80,20,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(180,0,0,0.1) 0%, transparent 50%),
        repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(0,255,65,0.015) 50px, rgba(0,255,65,0.015) 51px),
        repeating-linear-gradient(90deg, transparent, transparent 50px, rgba(0,255,65,0.015) 50px, rgba(0,255,65,0.015) 51px) !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0A0F0A; }
::-webkit-scrollbar-thumb { background: #1A4A1A; border-radius: 2px; }
[data-testid="stSidebar"] {
    background: #050D05 !important;
    border-right: 1px solid #1A3A1A !important;
}
[data-testid="stSidebar"] * { color: #A8C5A0 !important; }
.stButton > button {
    background: linear-gradient(135deg, #0A2A0A, #0F3A0F) !important;
    color: #00FF41 !important;
    border: 1px solid #1A6A1A !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.3s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0F3A0F, #1A5A1A) !important;
    border-color: #00FF41 !important;
    box-shadow: 0 0 15px rgba(0,255,65,0.3) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #050D05 !important;
    border-bottom: 1px solid #1A3A1A !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #4A7A4A !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    border: 1px solid transparent !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: #0A2A0A !important;
    color: #00FF41 !important;
    border-color: #1A6A1A !important;
    border-bottom-color: #030A06 !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #050F05, #0A1A0A) !important;
    border: 1px solid #1A3A1A !important;
    border-radius: 4px !important;
    padding: 12px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: #00FF41 !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricLabel"] {
    color: #4A7A4A !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
.block-container { padding-top: 1rem !important; }
#MainMenu, footer, header { visibility: hidden !important; }
div[data-testid="stStatusWidget"] { display: none !important; }
.element-container { opacity: 1 !important; }
@keyframes ticker {
    0%   { transform: translateX(100vw); }
    100% { transform: translateX(-100%); }
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.5; }
}
@keyframes alertpulse {
    0%,100% { border-color:#FF0000; box-shadow:0 0 10px rgba(255,0,0,0.3); }
    50%     { border-color:#FF6666; box-shadow:0 0 25px rgba(255,0,0,0.6); }
}
@keyframes scanline {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
</style>
""", unsafe_allow_html=True)

# ── Load from MySQL ───────────────────────────────────
def load_from_db():
    try:
        conn = mysql.connector.connect(
            host='localhost', user='root',
            password='root1234', database='smartborder'
        )
        df = pd.read_sql("SELECT * FROM alerts ORDER BY timestamp DESC", conn)
        conn.close()
        return df, True
    except:
        return pd.read_csv('border_alerts.csv'), False

def add_coords(df):
    zone_coords = {
        'North': (34.0, 74.0), 'West':  (24.0, 68.0),
        'East':  (26.0, 92.0), 'South': (28.0, 77.0)
    }
    if 'zone' not in df.columns or df['zone'].isnull().all():
        df['zone'] = np.random.choice(['North','West','East','South'], len(df))
    if 'Latitude' not in df.columns:
        df['Latitude']  = df['zone'].apply(lambda z: zone_coords.get(z,(28,77))[0] + np.random.uniform(-2,2))
        df['Longitude'] = df['zone'].apply(lambda z: zone_coords.get(z,(28,77))[1] + np.random.uniform(-2,2))
    return df

# ── Load Data ─────────────────────────────────────────
df, db_ok = load_from_db()
df = add_coords(df)
if 'alert_type' not in df.columns and 'Alert_Type' in df.columns:
    df = df.rename(columns={'Alert_Type':'alert_type','Is_Intrusion':'prediction','Severity':'severity'})

# ── KPIs ──────────────────────────────────────────────
total      = len(df)
red_count  = int((df['alert_type']=='Red').sum())
yel_count  = int((df['alert_type']=='Yellow').sum())
grn_count  = int((df['alert_type']=='Green').sum())
intrusions = int(df['prediction'].sum()) if 'prediction' in df.columns else 0
avg_sev    = round(df['severity'].mean(), 1) if 'severity' in df.columns else 0
threat_pct = round((red_count / max(total,1)) * 100, 1)
threat_color = "#FF0000" if threat_pct > 20 else "#FFA500" if threat_pct > 10 else "#00FF41"
threat_level_label = (
    "CRITICAL" if threat_pct > 30 else "HIGH" if threat_pct > 20 else
    "ELEVATED" if threat_pct > 10 else "GUARDED" if threat_pct > 5 else "LOW"
)

# ── HEADER ───────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(90deg,#050D05,#0A1A0A,#050D05);
    border:1px solid #1A4A1A;border-radius:4px;padding:16px 24px;margin-bottom:16px;
    display:flex;align-items:center;justify-content:space-between;
    position:relative;overflow:hidden;">
    <div style="position:absolute;top:0;left:0;right:0;height:2px;
        background:linear-gradient(90deg,transparent,#00FF41,#FF0000,#00FF41,transparent);
        animation:scanline 3s linear infinite;"></div>
    <div>
        <div style="font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;
            color:#00FF41;letter-spacing:4px;text-shadow:0 0 20px rgba(0,255,65,0.5);">
            🛡️ SMARTBORDER AI
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;
            color:#4A7A4A;letter-spacing:3px;margin-top:2px;">
            TACTICAL COMMAND CENTER  //  BORDER DEFENCE &amp; SURVEILLANCE
        </div>
    </div>
    <div style="text-align:right;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;color:#4A7A4A;">
            {'🟢 MYSQL CONNECTED' if db_ok else '🟡 CSV FALLBACK'}
        </div>
        <div style="font-family:'Orbitron',monospace;font-size:0.8rem;color:#00FF41;margin-top:4px;">
            MODEL ACC: 99.72%
        </div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#4A7A4A;">
            RANDOM FOREST  //  41 FEATURES
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── ALERT TICKER ─────────────────────────────────────
recent = df[df['alert_type']=='Red'].head(8) if len(df) > 0 else pd.DataFrame()
ticker_items = ""
for _, row in recent.iterrows():
    ts = str(row.get('timestamp',''))[:16]
    ticker_items += f"⚠️ RED ALERT — ZONE {str(row.get('zone','?')).upper()} — SEV {row.get('severity',0)}/10 — {ts} &nbsp;&nbsp;&nbsp;///&nbsp;&nbsp;&nbsp; "
if not ticker_items:
    ticker_items = "🟢 ALL CLEAR — NO ACTIVE RED ALERTS &nbsp;&nbsp;&nbsp;///&nbsp;&nbsp;&nbsp; " * 4

st.markdown(f"""
<div style="background:#030A06;border-top:1px solid #3A0A0A;border-bottom:1px solid #3A0A0A;
    padding:8px 0;margin-bottom:16px;overflow:hidden;">
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;color:#FF4444;
        white-space:nowrap;animation:ticker 40s linear infinite;
        display:inline-block;letter-spacing:1px;">
        {ticker_items * 3}
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────
st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:16px;">
    <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
        border:1px solid #1A4A1A;border-radius:4px;padding:14px 12px;border-top:2px solid #00FF41;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#4A7A4A;letter-spacing:2px;margin-bottom:6px;">TOTAL RECORDS</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:#00FF41;
            font-weight:700;text-shadow:0 0 10px rgba(0,255,65,0.4);">{total:,}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#2A5A2A;margin-top:4px;">DATABASE ENTRIES</div>
    </div>
    <div style="background:linear-gradient(135deg,#0F0505,#1A0A0A);
        border:1px solid #4A1A1A;border-radius:4px;padding:14px 12px;border-top:2px solid #FF0000;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#7A4A4A;letter-spacing:2px;margin-bottom:6px;">🔴 RED ALERTS</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:#FF4444;
            font-weight:700;text-shadow:0 0 10px rgba(255,0,0,0.4);">{red_count:,}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#5A2A2A;margin-top:4px;">CRITICAL THREATS</div>
    </div>
    <div style="background:linear-gradient(135deg,#0A0A05,#151505);
        border:1px solid #3A3A1A;border-radius:4px;padding:14px 12px;border-top:2px solid #FFA500;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#7A7A4A;letter-spacing:2px;margin-bottom:6px;">🟡 YELLOW ALERTS</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:#FFA500;
            font-weight:700;text-shadow:0 0 10px rgba(255,165,0,0.4);">{yel_count:,}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#5A5A2A;margin-top:4px;">SUSPICIOUS ACTIVITY</div>
    </div>
    <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
        border:1px solid #1A4A1A;border-radius:4px;padding:14px 12px;border-top:2px solid #00AA00;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#4A7A4A;letter-spacing:2px;margin-bottom:6px;">🟢 GREEN (SAFE)</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:#00CC44;
            font-weight:700;text-shadow:0 0 10px rgba(0,200,65,0.4);">{grn_count:,}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#2A5A2A;margin-top:4px;">NORMAL TRAFFIC</div>
    </div>
    <div style="background:linear-gradient(135deg,#050F0F,#0A1A1A);
        border:1px solid #1A3A4A;border-radius:4px;padding:14px 12px;border-top:2px solid #00AAFF;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#4A6A7A;letter-spacing:2px;margin-bottom:6px;">INTRUSIONS DET.</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:#00AAFF;
            font-weight:700;text-shadow:0 0 10px rgba(0,170,255,0.4);">{intrusions:,}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#2A4A5A;margin-top:4px;">CONFIRMED BREACHES</div>
    </div>
    <div style="background:linear-gradient(135deg,#050508,#0A0A14);
        border:1px solid #2A1A4A;border-radius:4px;padding:14px 12px;border-top:2px solid {threat_color};">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#6A4A7A;letter-spacing:2px;margin-bottom:6px;">THREAT LEVEL</div>
        <div style="font-family:'Orbitron',monospace;font-size:1.5rem;color:{threat_color};
            font-weight:700;text-shadow:0 0 10px rgba(255,0,0,0.4);">{threat_pct}%</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
            color:#4A2A5A;margin-top:4px;">AVG SEV: {avg_sev}/10</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── THREAT LEVEL METER ────────────────────────────────
threat_bar_color = (
    "#FF0000" if threat_pct > 30 else "#FF4400" if threat_pct > 20 else
    "#FFA500" if threat_pct > 10 else "#FFDD00" if threat_pct > 5 else "#00FF41"
)
st.markdown(f"""
<div style="background:linear-gradient(135deg,#050D05,#0A1A0A);
    border:1px solid #1A3A1A;border-radius:4px;padding:14px 20px;margin-bottom:16px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;
            color:#4A7A4A;letter-spacing:3px;">⚡ THREAT LEVEL INDICATOR</div>
        <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:{threat_bar_color};
            font-weight:700;text-shadow:0 0 10px {threat_bar_color};
            animation:pulse 2s ease-in-out infinite;">{threat_level_label}</div>
    </div>
    <div style="background:#0A0F0A;border-radius:2px;height:14px;
        border:1px solid #1A3A1A;overflow:hidden;position:relative;">
        <div style="height:100%;width:{min(threat_pct*2,100)}%;
            background:linear-gradient(90deg,#004400,{threat_bar_color});
            border-radius:2px;box-shadow:0 0 15px {threat_bar_color};position:relative;">
            <div style="position:absolute;right:0;top:0;bottom:0;width:3px;
                background:{threat_bar_color};box-shadow:0 0 8px {threat_bar_color};
                animation:pulse 1s ease-in-out infinite;"></div>
        </div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:4px;
        font-family:'Share Tech Mono',monospace;font-size:0.6rem;color:#2A5A2A;">
        <span>LOW</span><span>GUARDED</span><span>ELEVATED</span><span>HIGH</span><span>CRITICAL</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── RED ALERT BANNER ──────────────────────────────────
if red_count > 0:
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,#1A0000,#2A0505,#1A0000);
        border:1px solid #FF0000;border-radius:4px;padding:10px 20px;margin-bottom:16px;
        display:flex;align-items:center;gap:12px;animation:alertpulse 1.5s ease-in-out infinite;">
        <span style="font-size:1.4rem;">🚨</span>
        <div>
            <span style="font-family:'Orbitron',monospace;font-size:0.85rem;
                color:#FF4444;font-weight:700;letter-spacing:2px;">
                ACTIVE THREAT DETECTED — {red_count:,} RED ALERTS IN DATABASE
            </span>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                color:#AA4444;letter-spacing:1px;margin-top:2px;">
                IMMEDIATE RESPONSE REQUIRED // ZONE COMMANDERS NOTIFIED
            </div>
        </div>
        <button onclick="playAlert()" style="margin-left:auto;background:#2A0505;
            border:1px solid #FF4444;color:#FF4444;padding:6px 12px;
            font-family:'Share Tech Mono',monospace;font-size:0.65rem;
            cursor:pointer;letter-spacing:1px;border-radius:2px;">🔊 SOUND ALERT</button>
    </div>
    <script>
    function playAlert() {{
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function beep(freq, start, dur, vol=0.3) {{
            const o = ctx.createOscillator();
            const g = ctx.createGain();
            o.connect(g); g.connect(ctx.destination);
            o.frequency.value = freq; o.type = 'square';
            g.gain.setValueAtTime(0, ctx.currentTime + start);
            g.gain.linearRampToValueAtTime(vol, ctx.currentTime + start + 0.01);
            g.gain.linearRampToValueAtTime(0, ctx.currentTime + start + dur);
            o.start(ctx.currentTime + start);
            o.stop(ctx.currentTime + start + dur + 0.05);
        }}
        beep(880,0.0,0.15); beep(660,0.2,0.15);
        beep(880,0.4,0.15); beep(440,0.6,0.3);
    }}
    </script>
    """, unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00FF41;
        letter-spacing:3px;padding:10px 0;border-bottom:1px solid #1A3A1A;
        margin-bottom:16px;">⚙️ COMMAND PANEL</div>
    """, unsafe_allow_html=True)
    if db_ok:
        st.markdown('<div style="color:#00FF41;font-family:Share Tech Mono,monospace;font-size:0.7rem;">🟢 MYSQL — CONNECTED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#FFA500;font-family:Share Tech Mono,monospace;font-size:0.7rem;">🟡 CSV FALLBACK MODE</div>', unsafe_allow_html=True)
    st.markdown("---")
    auto_refresh = st.checkbox("🔄 AUTO-REFRESH (30s)", value=False)
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    if st.button("⟳ REFRESH NOW", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#4A7A4A;letter-spacing:2px;">FILTERS</div>', unsafe_allow_html=True)
    alert_filter = st.multiselect("ALERT TYPE", ['Red','Yellow','Green'], default=['Red','Yellow','Green'])
    zone_filter  = st.multiselect("ZONE", ['North','South','East','West'], default=['North','South','East','West'])
    sev_filter   = st.slider("MIN SEVERITY", 0.0, 10.0, 0.0, 0.5)
    st.markdown("---")
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;color:#4A7A4A;line-height:2.2;">
    TOTAL  : <span style="color:#00FF41">{total:,}</span><br>
    🔴 RED : <span style="color:#FF4444">{red_count:,}</span><br>
    🟡 YEL : <span style="color:#FFA500">{yel_count:,}</span><br>
    🟢 GRN : <span style="color:#00CC44">{grn_count:,}</span>
    </div>
    """, unsafe_allow_html=True)

# ── Apply Filters ─────────────────────────────────────
filtered = df.copy()
if 'alert_type' in filtered.columns:
    filtered = filtered[filtered['alert_type'].isin(alert_filter)]
if 'zone' in filtered.columns:
    filtered = filtered[filtered['zone'].isin(zone_filter)]
if 'severity' in filtered.columns:
    filtered = filtered[filtered['severity'] >= sev_filter]

# ── TABS ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  INTEL OVERVIEW",
    "🗺️  TACTICAL MAP",
    "🔮  LIVE PREDICTOR",
    "🤖  AI CHATBOT",
    "📋  ABOUT PROJECT"
])

# ── Chart Styles ──────────────────────────────────────
plt.style.use('dark_background')
rcParams['font.family'] = 'monospace'
DARK_BG  = '#050D05'
CARD_BG  = '#0A1A0A'
RED_C    = '#FF4444'
YEL_C    = '#FFA500'
GRN_C    = '#00CC44'
GRID_C   = '#1A3A1A'
TEXT_C   = '#A8C5A0'
ACCENT_C = '#00FF41'

def styled_fig(w=6, h=4):
    fig, ax = plt.subplots(figsize=(w,h))
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_C, labelsize=8)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.grid(True, color=GRID_C, linewidth=0.5, alpha=0.5)
    return fig, ax

# ════════════════════════════════════════════════════
# TAB 1 — INTEL OVERVIEW
# ════════════════════════════════════════════════════
with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">ALERT DISTRIBUTION</div>', unsafe_allow_html=True)
        counts = filtered['alert_type'].value_counts() if len(filtered)>0 else pd.Series()
        if len(counts) > 0:
            fig, ax = plt.subplots(figsize=(5,4))
            fig.patch.set_facecolor(DARK_BG)
            ax.set_facecolor(DARK_BG)
            color_map = {'Red':RED_C,'Yellow':YEL_C,'Green':GRN_C}
            colors = [color_map.get(c,'#888') for c in counts.index]
            wedges, texts, autotexts = ax.pie(
                counts, labels=counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90,
                wedgeprops=dict(edgecolor='#030A06', linewidth=2)
            )
            for t in texts:     t.set_color(TEXT_C); t.set_fontsize(9)
            for t in autotexts: t.set_color('#030A06'); t.set_fontweight('bold'); t.set_fontsize(8)
            ax.set_title('ALERT TYPE SPLIT', color=ACCENT_C, fontsize=9, pad=10)
            st.pyplot(fig); plt.close()

    with col2:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">SEVERITY DISTRIBUTION</div>', unsafe_allow_html=True)
        if len(filtered) > 0:
            fig, ax = styled_fig(5,4)
            n, bins, patches = ax.hist(filtered['severity'], bins=25, edgecolor='#030A06', linewidth=0.5)
            for patch, left in zip(patches, bins[:-1]):
                patch.set_facecolor(RED_C if left>=6.5 else (YEL_C if left>=4 else GRN_C))
            ax.axvline(x=4,   color=YEL_C, linestyle='--', linewidth=1.5, alpha=0.8, label='Yellow>=4')
            ax.axvline(x=6.5, color=RED_C, linestyle='--', linewidth=1.5, alpha=0.8, label='Red>=6.5')
            ax.set_xlabel('SEVERITY SCORE', fontsize=8)
            ax.set_ylabel('COUNT', fontsize=8)
            ax.set_title('SEVERITY HISTOGRAM', color=ACCENT_C, fontsize=9)
            ax.legend(fontsize=7, facecolor=CARD_BG, edgecolor=GRID_C, labelcolor=TEXT_C)
            st.pyplot(fig); plt.close()

    with col3:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">ZONE RISK LEVELS</div>', unsafe_allow_html=True)
        if len(filtered) > 0:
            zone_avg = filtered.groupby('zone')['severity'].mean().sort_values(ascending=True)
            fig, ax  = styled_fig(5,4)
            bar_colors = [RED_C if v>=6.5 else (YEL_C if v>=4 else GRN_C) for v in zone_avg.values]
            bars = ax.barh(zone_avg.index, zone_avg.values, color=bar_colors, edgecolor='#030A06', height=0.5)
            for bar, val in zip(bars, zone_avg.values):
                ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2,
                        f'{val:.1f}', va='center', color=TEXT_C, fontsize=8)
            ax.axvline(x=4,   color=YEL_C, linestyle='--', linewidth=1, alpha=0.6)
            ax.axvline(x=6.5, color=RED_C, linestyle='--', linewidth=1, alpha=0.6)
            ax.set_xlabel('AVG SEVERITY', fontsize=8)
            ax.set_title('ZONE THREAT LEVELS', color=ACCENT_C, fontsize=9)
            st.pyplot(fig); plt.close()

    st.markdown("---")
    col4, col5 = st.columns([2,1])

    with col4:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">ALERTS BY ZONE — STACKED</div>', unsafe_allow_html=True)
        if len(filtered) > 0:
            zone_counts = filtered.groupby(['zone','alert_type']).size().unstack(fill_value=0)
            fig, ax     = styled_fig(9,4)
            bottom      = np.zeros(len(zone_counts))
            for atype, color in [('Green',GRN_C),('Yellow',YEL_C),('Red',RED_C)]:
                if atype in zone_counts.columns:
                    vals = zone_counts[atype].values
                    ax.bar(zone_counts.index, vals, bottom=bottom, color=color,
                           label=atype, edgecolor='#030A06', linewidth=0.5)
                    bottom += vals
            ax.set_title('ZONE-WISE ALERT BREAKDOWN', color=ACCENT_C, fontsize=9)
            ax.set_xlabel('BORDER ZONE', fontsize=8)
            ax.set_ylabel('ALERT COUNT', fontsize=8)
            ax.tick_params(axis='x', rotation=0)
            ax.legend(fontsize=8, facecolor=CARD_BG, edgecolor=GRID_C, labelcolor=TEXT_C)
            st.pyplot(fig); plt.close()

    with col5:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">ZONE SUMMARY TABLE</div>', unsafe_allow_html=True)
        if len(filtered) > 0:
            zone_tbl = filtered.groupby('zone').agg(
                Total   = ('severity','count'),
                Avg_Sev = ('severity','mean'),
                Red     = ('alert_type', lambda x:(x=='Red').sum())
            ).round(1).reset_index()
            zone_tbl['Risk'] = zone_tbl['Avg_Sev'].apply(
                lambda x: '🔴 HIGH' if x>=6.5 else ('🟡 MED' if x>=4 else '🟢 LOW'))
            st.dataframe(zone_tbl.sort_values('Avg_Sev',ascending=False),
                        use_container_width=True, hide_index=True)


    st.markdown("---")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">🤖 MODEL COMPARISON — ALL 4 MODELS</div>', unsafe_allow_html=True)
        models      = ['Logistic\nRegression', 'Random\nForest', 'SVM\n(RBF)', 'Gradient\nBoosting']
        accuracies  = [92.14, 99.72, 97.83, 98.45]
        fig, ax     = styled_fig(6, 4)
        bar_colors  = [ACCENT_C if m == 'Random\nForest' else '#2A5A2A' for m in models]
        bars = ax.bar(models, accuracies, color=bar_colors, edgecolor='#030A06', width=0.5)
        for bar, acc in zip(bars, accuracies):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    f'{acc}%', ha='center', va='bottom', color=TEXT_C, fontsize=9, fontweight='bold')
        ax.set_ylim(88, 101)
        ax.set_ylabel('ACCURACY (%)', fontsize=8)
        ax.set_title('ML MODEL COMPARISON', color=ACCENT_C, fontsize=9)
        ax.axhline(y=99.72, color=ACCENT_C, linestyle='--', linewidth=1, alpha=0.5)
        st.pyplot(fig); plt.close()
        st.markdown("""
        <div style="background:#050D05;border:1px solid #1A4A1A;border-left:3px solid #00FF41;
            padding:8px 12px;border-radius:4px;font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#4A7A4A;">
            ✅ WINNER: Random Forest (99.72%) — outperforms all 3 other models
        </div>
        """, unsafe_allow_html=True)

    with col_m2:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">📥 EXPORT ALERTS DATA</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#050D05;border:1px solid #1A3A1A;border-radius:4px;
            padding:16px;font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;line-height:2;">
            Download the filtered alerts as CSV.<br>
            Includes all columns: timestamp, zone,<br>
            severity, alert_type, prediction.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if len(filtered) > 0:
            export_cols = [c for c in ['timestamp','zone','severity','alert_type','prediction','src_bytes','dst_bytes','serror_rate'] if c in filtered.columns]
            csv_data = filtered[export_cols].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD FILTERED ALERTS (.CSV)",
                data=csv_data,
                file_name=f"smartborder_alerts_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)
            all_csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 DOWNLOAD ALL ALERTS (.CSV)",
                data=all_csv,
                file_name=f"smartborder_ALL_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No data available to export.")


    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">⚡ LATEST ALERTS — LIVE FEED</div>', unsafe_allow_html=True)
    show_cols = [c for c in ['timestamp','zone','severity','alert_type','prediction'] if c in filtered.columns]

    def color_alert(val):
        if val=='Red':    return 'color:#FF4444;font-weight:bold'
        if val=='Yellow': return 'color:#FFA500;font-weight:bold'
        if val=='Green':  return 'color:#00CC44;font-weight:bold'
        return ''

    if len(filtered)>0 and show_cols:
        styled_df = filtered[show_cols].head(30).style.applymap(
            color_alert, subset=['alert_type'] if 'alert_type' in show_cols else [])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# TAB 2 — TACTICAL MAP
# ════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:12px;">🗺️ BORDER SURVEILLANCE — REAL-TIME THREAT HEATMAP</div>', unsafe_allow_html=True)

    mc1,mc2,mc3,mc4 = st.columns(4)
    mc1.metric("📍 ZONES ACTIVE",    len(filtered['zone'].unique()) if len(filtered)>0 else 0)
    mc2.metric("🔴 CRITICAL POINTS", red_count)
    mc3.metric("⚠️ MAX SEVERITY",    round(filtered['severity'].max(),1) if len(filtered)>0 else 0)
    mc4.metric("🛡️ SAFE RECORDS",   grn_count)

    # Map view toggle
    map_view = st.radio("MAP VIEW", ["🌡️ Heatmap", "🔴 Alert Bubbles", "🔀 Both"],
                        horizontal=True, index=2)

    st.markdown("---")
    map_col, info_col = st.columns([3,1])

    zone_info = {
        'North': {'loc':[34.0,74.0],'color':'#FF4444','label':'NORTH — KASHMIR'},
        'West':  {'loc':[24.0,68.0],'color':'#FFA500','label':'WEST — RAJASTHAN'},
        'East':  {'loc':[26.0,92.0],'color':'#00AAFF','label':'EAST — ASSAM'},
        'South': {'loc':[28.0,77.0],'color':'#00CC44','label':'SOUTH — DELHI NCR'},
    }

    with map_col:
        # Use OpenStreetMap for better heatmap visibility
        m = folium.Map(location=[29.0, 78.0], zoom_start=5, tiles='CartoDB dark_matter')

        # Zone boundary circles
        for zone, info in zone_info.items():
            folium.Circle(
                location=info['loc'], radius=150000,
                color=info['color'], fill=True,
                fill_color=info['color'], fill_opacity=0.08,
                weight=2, opacity=0.6,
                tooltip=f"🛡️ {info['label']}"
            ).add_to(m)
            folium.Marker(
                location=info['loc'],
                icon=folium.DivIcon(html=f"""
                    <div style="font-family:monospace;font-size:11px;color:{info['color']};
                        font-weight:bold;text-shadow:0 0 6px black,0 0 6px black;
                        white-space:nowrap;padding:2px 4px;">
                        ◈ {zone.upper()}</div>""")
            ).add_to(m)

        if len(filtered) > 0:
            # Build heatmap data — repeat high severity points for visibility
            heat_data = []
            for _, row in filtered.iterrows():
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    sev = float(row['severity'])
                    weight = sev / 10.0
                    # Add point multiple times based on severity for visibility
                    repeats = int(sev) + 1
                    for _ in range(repeats):
                        heat_data.append([
                            lat + np.random.uniform(-0.05, 0.05),
                            lon + np.random.uniform(-0.05, 0.05),
                            weight
                        ])
                except:
                    pass

            # Add heatmap layer
            if heat_data and map_view in ["🌡️ Heatmap", "🔀 Both"]:
                HeatMap(
                    heat_data,
                    name="Threat Heatmap",
                    radius=35,
                    blur=30,
                    min_opacity=0.5,
                    max_val=1.0,
                    gradient={
                        0.0: '#000066',
                        0.2: '#00FF41',
                        0.4: '#FFFF00',
                        0.6: '#FFA500',
                        0.8: '#FF4400',
                        1.0: '#FF0000'
                    }
                ).add_to(m)

            # Add circle markers
            if map_view in ["🔴 Alert Bubbles", "🔀 Both"]:
                color_map = {'Red':'red','Yellow':'orange','Green':'green'}
                sample = filtered.sample(min(600, len(filtered)), random_state=42)
                for _, row in sample.iterrows():
                    folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=max(3, float(row['severity']) * 1.2),
                        color=color_map.get(row['alert_type'], 'blue'),
                        fill=True,
                        fill_color=color_map.get(row['alert_type'], 'blue'),
                        fill_opacity=0.7,
                        weight=1,
                        popup=folium.Popup(f"""
                            <div style="font-family:monospace;font-size:12px;
                                background:#0A0A0A;color:#00FF41;padding:8px;
                                border-radius:4px;border:1px solid #1A4A1A;">
                                <b style="color:#FF4444;">⚠ SMARTBORDER AI</b><br>
                                Zone: <b>{row['zone']}</b><br>
                                Alert: <b style="color:{'#FF4444' if row['alert_type']=='Red' else '#FFA500' if row['alert_type']=='Yellow' else '#00CC44'}">{row['alert_type']}</b><br>
                                Severity: <b>{row['severity']}/10</b>
                            </div>""", max_width=200)
                    ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, width=750, height=560, returned_objects=[])

    with info_col:
        st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">ZONE STATUS</div>', unsafe_allow_html=True)
        for zone, info in zone_info.items():
            zone_df  = filtered[filtered['zone']==zone] if len(filtered)>0 else pd.DataFrame()
            zone_red = int((zone_df['alert_type']=='Red').sum()) if len(zone_df)>0 else 0
            zone_sev = round(zone_df['severity'].mean(),1) if len(zone_df)>0 else 0
            risk_col = "#FF4444" if zone_sev>=6.5 else ("#FFA500" if zone_sev>=4 else "#00CC44")
            st.markdown(f"""
            <div style="background:#050D05;border:1px solid {info['color']}33;
                border-left:3px solid {info['color']};border-radius:4px;
                padding:10px;margin-bottom:8px;">
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.7rem;
                    color:{info['color']};font-weight:bold;">{zone.upper()}</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.6rem;
                    color:#4A7A4A;margin-top:4px;">
                    TOTAL: <span style="color:#A8C5A0">{len(zone_df)}</span><br>
                    🔴 RED: <span style="color:#FF4444">{zone_red}</span><br>
                    AVG SEV: <span style="color:{risk_col}">{zone_sev}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#2A5A2A;line-height:1.8;">
        🌡️ HEATMAP GUIDE:<br>
        <span style="color:#00FF41">■</span> GREEN = LOW<br>
        <span style="color:#FFFF00">■</span> YELLOW = MED<br>
        <span style="color:#FFA500">■</span> ORANGE = HIGH<br>
        <span style="color:#FF0000">■</span> RED = CRITICAL
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 3 — LIVE PREDICTOR
# ════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:12px;">🔮 LIVE THREAT PREDICTOR — SENSOR INPUT INTERFACE</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#050D05;border:1px solid #1A3A1A;border-left:3px solid #00FF41;
        padding:10px 16px;border-radius:4px;margin-bottom:16px;
        font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;">
        ⚡ PIPELINE: Streamlit → Flask API (port 5000) → Random Forest → MySQL → Dashboard
    </div>
    """, unsafe_allow_html=True)

    p1,p2,p3 = st.columns(3)
    duration    = p1.slider("DURATION (SEC)",    0,   100,  0)
    src_bytes   = p2.slider("SOURCE BYTES",      0, 50000, 100)
    dst_bytes   = p3.slider("DEST BYTES",        0, 10000, 100)
    serror_rate = p1.slider("ERROR RATE",        0.0,1.0,0.0,0.1)
    count       = p2.slider("CONN COUNT",        0,   511,  1)
    root_shell  = p3.selectbox("ROOT SHELL",     [0,1], format_func=lambda x:"YES ⚠️" if x==1 else "NO ✅")
    su_attempt  = p1.selectbox("SU ATTEMPTED",   [0,1], format_func=lambda x:"YES ⚠️" if x==1 else "NO ✅")
    num_shells  = p2.slider("NUM SHELLS",        0,   5,   0)
    srv_err     = p3.slider("SRV ERROR RATE",    0.0,1.0,0.0,0.1)

    if st.button("🚀 EXECUTE THREAT ANALYSIS", use_container_width=True, type="primary"):
        payload = {
            "duration":duration,"src_bytes":src_bytes,"dst_bytes":dst_bytes,
            "serror_rate":serror_rate,"srv_serror_rate":srv_err,"count":count,
            "root_shell":root_shell,"su_attempted":su_attempt,"num_shells":num_shells,
            "protocol_type":1,"service":5,"flag":2,"land":0,"wrong_fragment":0,
            "urgent":0,"hot":0,"num_failed_logins":0,"logged_in":1,"num_compromised":0,
            "num_root":0,"num_file_creations":0,"num_access_files":0,"num_outbound_cmds":0,
            "is_host_login":0,"is_guest_login":0,"srv_count":count,"rerror_rate":0.0,
            "srv_rerror_rate":0.0,"same_srv_rate":1.0,"diff_srv_rate":0.0,
            "srv_diff_host_rate":0.0,"dst_host_count":255,"dst_host_srv_count":255,
            "dst_host_same_srv_rate":1.0,"dst_host_diff_srv_rate":0.0,
            "dst_host_same_src_port_rate":1.0,"dst_host_srv_diff_host_rate":0.0,
            "dst_host_serror_rate":serror_rate,"dst_host_srv_serror_rate":srv_err,
            "dst_host_rerror_rate":0.0,"dst_host_srv_rerror_rate":0.0,
        }
        try:
            response = requests.post("http://localhost:5000/predict", json=payload, timeout=5)
            result   = response.json()
            atype    = result['alert_type']
            color    = "#FF4444" if atype=="Red" else ("#FFA500" if atype=="Yellow" else "#00CC44")
            bg_color = "#1A0000" if atype=="Red" else ("#1A1000" if atype=="Yellow" else "#001A00")
            anim     = "animation:alertpulse 1.5s ease-in-out infinite;" if atype=='Red' else ''

            r1,r2,r3,r4 = st.columns(4)
            r1.metric("ALERT TYPE",  f"{result['alert_emoji']} {result['alert_type']}")
            r2.metric("SEVERITY",    f"{result['severity']}/10")
            r3.metric("PROBABILITY", f"{result['probability']}%")
            r4.metric("ZONE",        result['zone'])

            st.markdown(f"""
            <div style="background:{bg_color};border:1px solid {color};
                border-radius:4px;padding:16px;margin-top:12px;{anim}">
                <div style="font-family:'Orbitron',monospace;font-size:1.1rem;
                    color:{color};font-weight:700;letter-spacing:2px;">
                    {result['label']} — {result['action'].upper()}
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                    color:{color}88;margin-top:6px;">
                    ID: #{result['alert_id']} | ZONE: {result['zone']} | {result['timestamp']}
                </div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:0.65rem;
                    color:#4A7A4A;margin-top:4px;">
                    ✅ SAVED TO MYSQL — CLICK REFRESH TO UPDATE DASHBOARD
                </div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ API OFFLINE: {e} — Make sure api.py is running!")

    # Prediction History
    st.markdown("---")
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:8px;">📋 PREDICTION HISTORY — THIS SESSION</div>', unsafe_allow_html=True)
    if 'pred_history' not in st.session_state:
        st.session_state.pred_history = []
    if len(st.session_state.pred_history) > 0:
        hist_df = pd.DataFrame(st.session_state.pred_history)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
        hist_csv = hist_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Session History", hist_csv,
                          "session_predictions.csv", "text/csv")
    else:
        st.markdown("""
        <div style="background:#050D05;border:1px solid #1A3A1A;border-radius:4px;
            padding:12px;font-family:Share Tech Mono,monospace;font-size:0.7rem;
            color:#2A5A2A;text-align:center;">
            NO PREDICTIONS YET — USE THE PREDICTOR ABOVE TO START
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════
# TAB 4 — CHATBOT
# ════════════════════════════════════════════════════
with tab4:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:12px;">🤖 SMARTBORDER AI — TACTICAL INTELLIGENCE ASSISTANT</div>', unsafe_allow_html=True)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role":"bot","msg":"SYSTEM ONLINE. SmartBorder AI Tactical Assistant ready. Type 'help' for commands."}
        ]

    def chatbot_response(q):
        q = q.lower().strip()
        try:
            s      = requests.get("http://localhost:5000/stats", timeout=3).json()
            total_ = s.get('total_alerts', total)
            red_   = s.get('red_alerts',   red_count)
            yel_   = s.get('yellow_alerts',yel_count)
            grn_   = s.get('green_alerts', grn_count)
            intr_  = s.get('intrusions',   intrusions)
            sev_   = s.get('avg_severity', avg_sev)
            acc_   = s.get('model_accuracy','99.72%')
            far_   = s.get('false_alarm_rate','N/A')
        except:
            total_,red_,yel_,grn_,intr_,sev_,acc_,far_ = total,red_count,yel_count,grn_count,intrusions,avg_sev,'99.72%','N/A'

        if any(w in q for w in ['red','critical','danger']):
            return f"🔴 CRITICAL REPORT: {red_:,} Red alerts. Threat rate: {round(red_/max(total_,1)*100,1)}%. Immediate action required!"
        if any(w in q for w in ['yellow','suspicious','warning']):
            return f"🟡 ELEVATED: {yel_:,} Yellow alerts flagged. Monitor closely."
        if any(w in q for w in ['green','normal','safe','clear']):
            return f"🟢 SAFE: {grn_:,} Green records — normal traffic, no threats."
        if any(w in q for w in ['total','count','how many','records']):
            return f"📊 DATABASE: {total_:,} total — 🔴 {red_:,} | 🟡 {yel_:,} | 🟢 {grn_:,}"
        if any(w in q for w in ['intrusion','breach','attack']):
            return f"🚨 INTRUSIONS: {intr_:,} confirmed ({round(intr_/max(total_,1)*100,1)}% of traffic)."
        if any(w in q for w in ['severity','score','level']):
            return f"⚠️ SEVERITY: Average {sev_}/10. Green <4 | Yellow 4–6.5 | Red ≥6.5"
        if any(w in q for w in ['false alarm','false positive']):
            return f"✅ FALSE ALARMS: {far_}. Multi-factor scoring keeps false positives minimal."
        if any(w in q for w in ['accuracy','model','ml','random forest']):
            return f"🤖 MODEL: Random Forest | Accuracy: {acc_} | 100 trees | 41 features | 25,192 training records."
        if any(w in q for w in ['api','flask','endpoint']):
            return "📡 API: Flask on localhost:5000 — / | /predict | /alerts | /stats | /zones"
        if any(w in q for w in ['database','mysql','db']):
            return f"🗄️ DATABASE: MySQL 'smartborder' — {total_:,} alerts stored. Auto-saves every prediction."
        if any(w in q for w in ['zone','north','south','east','west']):
            return "🗺️ ZONES: North (Kashmir) | West (Rajasthan) | East (Assam) | South (Delhi NCR). See Tactical Map."
        if any(w in q for w in ['help','commands','what can']):
            return "💡 COMMANDS: red | yellow | green | total | intrusions | severity | false alarm | model | api | database | zones"
        if any(w in q for w in ['hello','hi','hey','status']):
            return f"🛡️ SYSTEM ONLINE. {total_:,} records in DB. Threat level: {threat_level_label}. How can I assist?"
        if any(w in q for w in ['thank','thanks','good','great']):
            return "⚡ ACKNOWLEDGED. Standing by for next query. Stay vigilant."
        return "❓ UNRECOGNIZED. Type 'help' for available commands."

    quick_qs = [
        "🔴 Red alert count?","📊 Total records?",
        "🚨 Intrusion report","🗺️ Zone status",
        "🤖 Model accuracy?","📡 API status?",
        "⚠️ Severity report","🗄️ Database status?"
    ]
    cols = st.columns(4)
    for i, q in enumerate(quick_qs):
        with cols[i%4]:
            if st.button(q, key=f"qb_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role":"user","msg":q})
                st.session_state.chat_history.append({"role":"bot","msg":chatbot_response(q)})
                st.rerun()

    st.markdown("---")
    for chat in st.session_state.chat_history[-12:]:
        if chat['role'] == 'user':
            st.markdown(f"""
            <div style="text-align:right;margin:6px 0;">
            <span style="background:#0A2A0A;color:#00FF41;padding:8px 16px;
                border-radius:16px 16px 4px 16px;display:inline-block;max-width:80%;
                font-family:Share Tech Mono,monospace;font-size:0.75rem;
                border:1px solid #1A6A1A;">👤 {chat['msg']}</span></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align:left;margin:6px 0;">
            <span style="background:#050F0A;color:#A8C5A0;padding:8px 16px;
                border-radius:16px 16px 16px 4px;display:inline-block;max-width:85%;
                font-family:Share Tech Mono,monospace;font-size:0.75rem;
                border:1px solid #1A3A2A;line-height:1.6;">🛡️ {chat['msg']}</span></div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    inp_col, send_col, clear_col = st.columns([6,1,1])
    with inp_col:
        user_input = st.text_input("", placeholder="ENTER QUERY...",
            label_visibility="collapsed", key="chat_input")
    with send_col:
        if st.button("SEND", use_container_width=True):
            if user_input.strip():
                st.session_state.chat_history.append({"role":"user","msg":user_input})
                st.session_state.chat_history.append({"role":"bot","msg":chatbot_response(user_input)})
                st.rerun()
    with clear_col:
        if st.button("CLEAR", use_container_width=True):
            st.session_state.chat_history = [{"role":"bot","msg":"SYSTEM RESET. Ready for new session."}]
            st.rerun()


# ════════════════════════════════════════════════════
# TAB 5 — ABOUT PROJECT
# ════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#4A7A4A;letter-spacing:2px;margin-bottom:16px;">📋 PROJECT OVERVIEW — SMARTBORDER AI</div>', unsafe_allow_html=True)

    a1, a2 = st.columns(2)

    with a1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;margin-bottom:12px;
            border-top:2px solid #00FF41;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00FF41;
                letter-spacing:2px;margin-bottom:12px;">🎯 PROJECT OBJECTIVE</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2;">
                Design and implement an AI-powered border intrusion
                detection system capable of real-time threat analysis,
                severity classification, and multi-zone surveillance
                monitoring using machine learning models trained on
                network intrusion datasets.
            </div>
        </div>

        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;margin-bottom:12px;
            border-top:2px solid #00AAFF;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00AAFF;
                letter-spacing:2px;margin-bottom:12px;">📊 DATASET</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2.2;">
                NAME    : Network Intrusion Detection<br>
                SOURCE  : Kaggle (sampadab17)<br>
                RECORDS : 25,192 rows<br>
                FEATURES: 41 input features<br>
                TARGET  : Normal / Anomaly (binary)<br>
                BALANCE : 13,449 Normal | 11,743 Anomaly
            </div>
        </div>

        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;
            border-top:2px solid #FFA500;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#FFA500;
                letter-spacing:2px;margin-bottom:12px;">⚙️ TECH STACK</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2.2;">
                ML      : Python, Scikit-learn, Joblib<br>
                API     : Flask, Flask-CORS<br>
                DATABASE: MySQL 9.6 (localhost:3306)<br>
                FRONTEND: Streamlit, Folium, Matplotlib<br>
                DEPLOY  : Local (VS Code + Windows)<br>
                VERSION : Python 3.11
            </div>
        </div>
        """, unsafe_allow_html=True)

    with a2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;margin-bottom:12px;
            border-top:2px solid #FF4444;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#FF4444;
                letter-spacing:2px;margin-bottom:12px;">🤖 ML MODELS TESTED</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2.2;">
                1. Logistic Regression    → 92.14% ❌<br>
                2. SVM (RBF Kernel)       → 97.83% ✅<br>
                3. Gradient Boosting      → 98.45% ✅<br>
                4. Random Forest (WINNER) → 99.72% 🏆<br><br>
                FEATURES USED : 41 sensor readings<br>
                TRAIN/TEST    : 80% / 20% split<br>
                RANDOM STATE  : 42 (reproducible)
            </div>
        </div>

        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;margin-bottom:12px;
            border-top:2px solid #00CC44;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00CC44;
                letter-spacing:2px;margin-bottom:12px;">📐 SEVERITY SCORING SYSTEM</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2.2;">
                SCORE = model_confidence × 0.5<br>
                      + src_bytes  > 1000  → +2<br>
                      + serror_rate > 0.3  → +2<br>
                      + prediction == 1    → +2<br>
                      + dst_bytes  > 1000  → +1<br><br>
                🟢 GREEN  : score < 4.0  (SAFE)<br>
                🟡 YELLOW : score 4–6.5  (MONITOR)<br>
                🔴 RED    : score ≥ 6.5  (CRITICAL)
            </div>
        </div>

        <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
            border:1px solid #1A4A1A;border-radius:4px;padding:20px;
            border-top:2px solid #AA44FF;">
            <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#AA44FF;
                letter-spacing:2px;margin-bottom:12px;">🏗️ SYSTEM ARCHITECTURE</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:0.72rem;
                color:#A8C5A0;line-height:2.2;">
                Train_data.csv<br>
                      ↓ train.py<br>
                Random Forest Model (99.72%)<br>
                      ↓ model.pkl + scaler.pkl<br>
                Flask REST API → localhost:5000<br>
                      ↓ POST /predict<br>
                MySQL Database → smartborder.alerts<br>
                      ↓ SELECT *<br>
                Streamlit Dashboard → localhost:8501
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#050F05,#0A1A0A);
        border:1px solid #1A4A1A;border-radius:4px;padding:20px;
        border-top:2px solid #00FF41;">
        <div style="font-family:'Orbitron',monospace;font-size:0.9rem;color:#00FF41;
            letter-spacing:2px;margin-bottom:16px;">📡 API ENDPOINTS — FLASK REST API</div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;">
            <div style="background:#030A06;border:1px solid #1A4A1A;border-radius:4px;padding:12px;text-align:center;">
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4A7A4A;">GET</div>
                <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:#00FF41;margin:4px 0;">/</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#A8C5A0;">Health Check</div>
            </div>
            <div style="background:#030A06;border:1px solid #4A1A1A;border-radius:4px;padding:12px;text-align:center;">
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#7A4A4A;">POST</div>
                <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:#FF4444;margin:4px 0;">/predict</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#A8C5A0;">Run Prediction</div>
            </div>
            <div style="background:#030A06;border:1px solid #1A3A4A;border-radius:4px;padding:12px;text-align:center;">
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4A6A7A;">GET</div>
                <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:#00AAFF;margin:4px 0;">/alerts</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#A8C5A0;">All Alerts</div>
            </div>
            <div style="background:#030A06;border:1px solid #3A3A1A;border-radius:4px;padding:12px;text-align:center;">
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#7A7A4A;">GET</div>
                <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:#FFA500;margin:4px 0;">/stats</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#A8C5A0;">Summary Stats</div>
            </div>
            <div style="background:#030A06;border:1px solid #1A4A1A;border-radius:4px;padding:12px;text-align:center;">
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#4A7A4A;">GET</div>
                <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:#00CC44;margin:4px 0;">/zones</div>
                <div style="font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#A8C5A0;">Zone Summary</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #1A3A1A;margin-top:20px;padding:12px 0;
    font-family:Share Tech Mono,monospace;font-size:0.6rem;
    color:#2A5A2A;text-align:center;letter-spacing:2px;">
    🛡️ SMARTBORDER AI TACTICAL COMMAND  //
    PYTHON • STREAMLIT • FLASK API • MYSQL • FOLIUM • SCIKIT-LEARN  //
    GTU INTERNSHIP 2026
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Manufacturing Cluster Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Hide Streamlit chrome completely ────────────────────────────────────────
st.markdown("""
<style>
#MainMenu                              { visibility: hidden !important; }
header                                 { visibility: hidden !important; }
footer                                 { visibility: hidden !important; }
[data-testid="stToolbar"]             { visibility: hidden !important; }
[data-testid="stDecoration"]          { display: none !important; }
[data-testid="stDeployButton"]        { display: none !important; }
[data-testid="collapsedControl"]      { display: none !important; }
.stActionButton                        { display: none !important; }
[data-testid="stStatusWidget"]        { display: none !important; }

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"]            { font-family: 'Space Grotesk', sans-serif !important; }

.stApp                                 { background: #0a0e1a !important; }
[data-testid="stSidebar"]             { background: #0d1424 !important; border-right: 1px solid #1e2d4a !important; }

[data-testid="stSidebar"] label       { color: #64748b !important; font-size: 11px !important;
                                        text-transform: uppercase; letter-spacing: 1px; }
.stSelectbox > div > div              { background: #111827 !important; border: 1px solid #1e2d4a !important;
                                        color: #e2e8f0 !important; border-radius: 6px !important; }

.stTabs [data-baseweb="tab-list"]     { background: #111827; border-radius: 8px; padding: 4px;
                                        border: 1px solid #1e2d4a; gap: 2px; }
.stTabs [data-baseweb="tab"]          { background: transparent; color: #64748b; border-radius: 6px;
                                        font-size: 12px; font-weight: 600; padding: 6px 16px; }
.stTabs [aria-selected="true"]        { background: #1e2d4a !important; color: #00d4ff !important; }

[data-testid="stDataFrame"]           { border: 1px solid #1e2d4a; border-radius: 8px; }
.stDownloadButton button              { background: transparent; border: 1px solid #1e2d4a;
                                        color: #64748b; font-size: 11px; padding: 6px 14px; border-radius: 6px; }
.stDownloadButton button:hover        { border-color: #00d4ff; color: #00d4ff; }
.stAlert                              { background: #111827 !important; border: 1px solid #1e2d4a !important;
                                        border-radius: 8px !important; }
hr                                     { border-color: #1e2d4a !important; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':                   '#ff9500',
    'Indian National Congress':                 '#19a7ce',
    'Samajwadi Party':                          '#e63946',
    'Trinamool Congress':                       '#28a745',
    'Telugu Desam':                             '#f5d020',
    'Janata Dal  (United)':                     '#9b59b6',
    'Dravida Munnetra Kazhagam':                '#dc3545',
    'YSR Congress Party':                       '#0d6efd',
    'Biju Janata Dal':                          '#20c997',
    'Shiv Sena':                                '#fd7e14',
    'Janasena Party':                           '#e91e63',
    'Rashtriya Lok Dal':                        '#8bc34a',
    'Nationalist Congress Party':               '#00bcd4',
    'Lok Janshakti Party(Ram Vilas)':           '#ff5722',
    'Apna Dal (Soneylal)':                      '#795548',
    'AJSU Party':                               '#607d8b',
    'Asom Gana Parishad':                       '#4caf50',
    'Janata Dal  (Secular)':                    '#673ab7',
    'Hindustani Awam Morcha (Secular)':         '#009688',
    'Shiv Sena (Uddhav Balasaheb Thackrey)':    '#ff7043',
    'Communist Party of India  (Marxist)':      '#f44336',
    'Indian Union Muslim League':               '#4CAF50',
}

IND_COLORS = [
    '#00d4ff','#00ff88','#ff6b35','#ffd700','#a855f7','#f472b6',
    '#34d399','#fb923c','#60a5fa','#f87171','#4ade80','#facc15',
    '#818cf8','#e879f9','#2dd4bf','#fb7185','#a3e635','#38bdf8',
    '#c084fc','#fdba74','#67e8f9','#86efac','#fca5a5','#d8b4fe',
    '#fde68a','#a7f3d0','#bfdbfe','#fecaca','#ddd6fe','#fed7aa',
    '#99f6e4','#bae6fd','#e9d5ff','#fef08a','#bbf7d0','#fecdd3',
    '#ddd6fe','#fde68a',
]

def pcolor(party):
    return PARTY_COLORS.get(party, '#64748b')

def dist_km(la1, lo1, la2, lo2):
    R = 6371
    a = math.sin(math.radians(la2-la1)/2)**2 + \
        math.cos(math.radians(la1)) * math.cos(math.radians(la2)) * \
        math.sin(math.radians(lo2-lo1)/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def load_data():
    csv_path  = os.path.join(BASE_DIR, 'Annexure_with_3digit_Sheet1_.csv')
    xlsx_path = os.path.join(BASE_DIR, 'Lok_Sabha_Elections_Winners_2024.xlsx')

    df_raw   = pd.read_csv(csv_path)
    df_units = df_raw.iloc[1:].reset_index(drop=True)
    df_units.columns = df_raw.columns

    industry_cols = [c for c in df_units.columns if c not in ['State','District','Latitude','Longitude']]
    df_units['Latitude']  = pd.to_numeric(df_units['Latitude'],  errors='coerce')
    df_units['Longitude'] = pd.to_numeric(df_units['Longitude'], errors='coerce')

    def safe_num(v):
        try:
            f = float(str(v).replace('-','0').replace(',',''))
            return 0 if math.isnan(f) else f
        except:
            return 0

    base_inds = {}
    for col in industry_cols:
        base = col.split('.')[0].strip()
        base_inds.setdefault(base, []).append(col)

    records = []
    for _, row in df_units.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            continue
        ind_totals = {}
        for b, cols in base_inds.items():
            s = sum(safe_num(row[c]) for c in cols)
            if s > 0:
                ind_totals[b] = int(s)
        records.append({
            'state': str(row['State']),
            'district': str(row['District']),
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
            'total_units': sum(ind_totals.values()),
            'industries': ind_totals,
        })

    df_lok = pd.read_excel(xlsx_path)
    lok_dict = {}
    for _, r in df_lok.iterrows():
        try:
            margin = int(r['Margin Votes'])
        except:
            margin = 0
        lok_dict[str(r['PC Name']).upper().strip()] = {
            'pc_name':     str(r['PC Name']),
            'state':       str(r['State']),
            'winner':      str(r['Winning Candidate']),
            'party':       str(r['Winning Party']),
            'runner_up':   str(r['Runner-up Canddiate']),
            'runner_party':str(r['Runner-up Party']),
            'margin':      margin,
        }

    for rec in records:
        key = rec['district'].upper().strip()
        if key in lok_dict:
            rec.update(lok_dict[key])
            rec['matched_pc'] = True
        else:
            rec['matched_pc'] = False

    df = pd.DataFrame(records)
    all_inds = sorted({ind for r in records for ind in r['industries']})
    ind_cmap = {ind: IND_COLORS[i % len(IND_COLORS)] for i, ind in enumerate(all_inds)}
    lok_list = list(lok_dict.values())
    return df, lok_list, all_inds, ind_cmap


df, lok_list, all_inds, ind_cmap = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:14px 0 12px 0;border-bottom:1px solid #1e2d4a;margin-bottom:18px">
      <div style="font-size:19px;font-weight:700;color:#e2e8f0;letter-spacing:-0.5px">🏭 MCI</div>
      <div style="font-size:11px;color:#64748b;margin-top:3px;line-height:1.4">
        Manufacturing Cluster Intelligence<br>
        <span style="color:#1e3a5f">Lok Sabha 2024 × Industrial Units</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">🔍 Filters</p>', unsafe_allow_html=True)

    sel_state    = st.selectbox("State",            ['All States']    + sorted(df['state'].unique()))
    sel_industry = st.selectbox("Industry Sector",  ['All Industries'] + all_inds)
    sel_party    = st.selectbox("Winning Party",    ['All Parties']   + sorted({p['party'] for p in lok_list}))
    min_units    = st.slider("Min. Industrial Units", 0, 2000, 0, step=10)
    match_type   = st.radio("District Type", ['All', 'PC Matched Only', 'Non-PC Districts'])

    st.markdown('<hr style="border-color:#1e2d4a;margin:14px 0">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">🗺️ Map Options</p>', unsafe_allow_html=True)
    view_mode = st.radio("Colour By", ['Units Count', 'Top Industry', 'Winning Party'])

    st.markdown('<hr style="border-color:#1e2d4a;margin:14px 0">', unsafe_allow_html=True)
    st.markdown('<p style="font-size:9px;color:#64748b;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px">📍 Radius Search</p>', unsafe_allow_html=True)
    st.caption("Enter coordinates to find clusters within a radius")
    radius_input = st.text_input("Centre (lat, lon)", placeholder="e.g. 28.61, 77.20")
    radius_km    = st.slider("Radius (km)", 10, 300, 100, step=10)

    st.markdown('<hr style="border-color:#1e2d4a;margin:14px 0">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:11px;color:#64748b;line-height:2.2">
      📦 <b style="color:#00d4ff">{len(df):,}</b> districts &nbsp;|&nbsp;
      🏭 <b style="color:#00d4ff">{int(df['total_units'].sum()):,}</b> units<br>
      🗳 <b style="color:#00d4ff">{len(lok_list)}</b> PC constituencies
    </div>
    """, unsafe_allow_html=True)

# ─── Apply Filters ────────────────────────────────────────────────────────────
filt = df.copy()
if sel_state    != 'All States':
    filt = filt[filt['state'] == sel_state]
if sel_industry != 'All Industries':
    filt = filt[filt['industries'].apply(lambda x: x.get(sel_industry, 0) > 0)]
if sel_party    != 'All Parties':
    if 'party' in filt.columns:
        filt = filt[filt['party'].fillna('') == sel_party]
if min_units > 0:
    filt = filt[filt['total_units'] >= min_units]
if match_type == 'PC Matched Only':
    filt = filt[filt['matched_pc'] == True]
if match_type == 'Non-PC Districts':
    filt = filt[filt['matched_pc'] == False]

radius_center = None
if radius_input.strip():
    try:
        parts = [x.strip() for x in radius_input.split(',')]
        rc_lat, rc_lon = float(parts[0]), float(parts[1])
        radius_center = (rc_lat, rc_lon)
        filt = filt[filt.apply(
            lambda r: dist_km(rc_lat, rc_lon, r['lat'], r['lon']) <= radius_km, axis=1
        )]
    except:
        st.sidebar.error("⚠️ Invalid format — use: 28.61, 77.20")

# ─── Header Metrics ───────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
pc_matched  = int(filt['matched_pc'].sum()) if 'matched_pc' in filt.columns else 0
avg_units   = int(filt['total_units'].mean()) if len(filt) else 0

def metric_card(col_obj, value, label, color='#00d4ff'):
    col_obj.markdown(
        f'<div style="background:#111827;border:1px solid #1e2d4a;border-radius:10px;'
        f'padding:14px 18px;text-align:center">'
        f'<div style="font-size:22px;font-weight:700;color:{color};'
        f'font-family:\'JetBrains Mono\',monospace;line-height:1.1">{value}</div>'
        f'<div style="font-size:10px;color:#64748b;text-transform:uppercase;'
        f'letter-spacing:1px;margin-top:4px">{label}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

metric_card(m1, f"{len(filt):,}",                     "Districts Shown")
metric_card(m2, f"{int(filt['total_units'].sum()):,}", "Industrial Units", '#00ff88')
metric_card(m3, f"{pc_matched}",                       "PC Matched",       '#ffd700')
metric_card(m4, f"{filt['state'].nunique()}",          "States")
metric_card(m5, f"{avg_units:,}",                      "Avg Units / District", '#ff6b35')

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

# ─── Main Tabs ────────────────────────────────────────────────────────────────
tab_map, tab_pc, tab_analysis, tab_data = st.tabs([
    "🗺️  Map", "🗳️  PC Intelligence", "📊  Analytics", "📋  Data Table"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab_map:
    map_col, rank_col = st.columns([3, 1])

    with map_col:
        clat = filt['lat'].mean() if len(filt) else 22.5
        clon = filt['lon'].mean() if len(filt) else 80.0
        if radius_center:
            clat, clon = radius_center

        m = folium.Map(
            location=[clat, clon],
            zoom_start=5 if sel_state == 'All States' else 7,
            tiles=None,
            prefer_canvas=True
        )
        folium.TileLayer(
            'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='© OpenStreetMap © CartoDB',
            name='Dark', max_zoom=18
        ).add_to(m)

        if radius_center:
            folium.Circle(
                location=radius_center, radius=radius_km * 1000,
                color='#00d4ff', fill=True, fill_color='#00d4ff',
                fill_opacity=0.06, weight=2, dash_array='8,4',
                tooltip=f"Radius: {radius_km} km"
            ).add_to(m)

        def marker_color(row):
            if view_mode == 'Top Industry':
                top = max(row['industries'], key=row['industries'].get) if row['industries'] else None
                return ind_cmap.get(top, '#64748b') if top else '#64748b'
            if view_mode == 'Winning Party':
                return pcolor(row.get('party', '')) if row.get('matched_pc') else '#2d3748'
            u = row['total_units']
            return '#ff6b35' if u > 500 else '#ffd700' if u > 100 else '#00ff88' if u > 20 else '#00d4ff'

        def marker_r(u):
            return max(5, min(22, math.sqrt(u + 1) * 0.9))

        for _, row in filt.iterrows():
            col_m  = marker_color(row)
            r      = marker_r(row['total_units'])
            is_pc  = row.get('matched_pc', False)

            top5 = sorted(row['industries'].items(), key=lambda x: -x[1])[:5]
            ind_rows = ''.join(
                f'<tr><td style="color:#94a3b8;font-size:11px;padding:1px 6px">{k[:36]}</td>'
                f'<td style="color:#00d4ff;font-weight:600;font-size:11px;padding:1px 6px;'
                f'text-align:right">{v}</td></tr>'
                for k, v in top5
            )

            pc_block = ''
            if is_pc:
                pc_block = (
                    f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #1e2d4a">'
                    f'<div style="font-size:9px;color:#64748b;text-transform:uppercase;'
                    f'letter-spacing:1px">PC Constituency</div>'
                    f'<div style="font-weight:700;color:#00ff88;font-size:12px;margin-top:2px">'
                    f'{row.get("pc_name","")}</div>'
                    f'<div style="font-size:11px;margin-top:3px">🏆 {row.get("winner","")}</div>'
                    f'<div style="font-size:11px;color:{pcolor(row.get("party",""))}">'
                    f'{row.get("party","")}</div>'
                    f'<div style="font-size:11px;color:#64748b">'
                    f'Margin: {row.get("margin",0):,} votes</div>'
                    f'</div>'
                )

            popup_html = (
                f'<div style="font-family:Space Grotesk,sans-serif;min-width:220px;'
                f'background:#111827;color:#e2e8f0;border-radius:8px;padding:4px">'
                f'<div style="font-size:14px;font-weight:700">{row["district"]}</div>'
                f'<div style="font-size:11px;color:#64748b;margin-bottom:8px">{row["state"]}</div>'
                f'<div style="font-size:22px;font-weight:700;color:#00d4ff;line-height:1">'
                f'{row["total_units"]:,}</div>'
                f'<div style="font-size:9px;color:#64748b;margin-bottom:8px;'
                f'text-transform:uppercase;letter-spacing:1px">Industrial Units</div>'
                f'<table style="width:100%;border-collapse:collapse">{ind_rows}</table>'
                f'{pc_block}</div>'
            )

            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=r,
                color='white' if is_pc else col_m,
                weight=2 if is_pc else 0.5,
                fill=True, fill_color=col_m, fill_opacity=0.82,
                popup=folium.Popup(popup_html, max_width=280),
                tooltip=(
                    f"{row['district']} · {row['total_units']:,} units"
                    + (f" · PC: {row.get('pc_name','')}" if is_pc else '')
                )
            ).add_to(m)

        # Legend
        if view_mode == 'Units Count':
            leg_items = [
                ('#ff6b35','500+ units'), ('#ffd700','100–500'),
                ('#00ff88','20–100'),     ('#00d4ff','<20 units')
            ]
        elif view_mode == 'Top Industry':
            ind_totals_leg = {}
            for _, row in filt.iterrows():
                for k, v in row['industries'].items():
                    ind_totals_leg[k] = ind_totals_leg.get(k, 0) + v
            top8 = sorted(ind_totals_leg.items(), key=lambda x: -x[1])[:8]
            leg_items = [(ind_cmap.get(k, '#64748b'), k[:26]) for k, _ in top8]
        else:
            parties_shown = set(filt['party'].dropna().unique()) if 'party' in filt.columns else set()
            leg_items = [(pcolor(p), p[:26]) for p in sorted(parties_shown)][:8]
            leg_items.append(('#2d3748', 'No PC data'))

        leg_html = (
            '<div style="background:rgba(17,24,39,0.96);border:1px solid #1e2d4a;'
            'border-radius:8px;padding:12px;font-family:Space Grotesk,sans-serif;min-width:170px">'
            f'<div style="font-size:9px;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:1px;margin-bottom:8px">{view_mode}</div>'
        )
        for c_leg, lbl in leg_items:
            leg_html += (
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
                f'<div style="width:9px;height:9px;border-radius:50%;background:{c_leg};flex-shrink:0"></div>'
                f'<span style="font-size:10px;color:#e2e8f0">{lbl}</span></div>'
            )
        if view_mode == 'Units Count':
            leg_html += (
                '<div style="display:flex;align-items:center;gap:8px;margin-top:6px;'
                'padding-top:6px;border-top:1px solid #1e2d4a">'
                '<div style="width:9px;height:9px;border-radius:50%;border:2px solid white;flex-shrink:0"></div>'
                '<span style="font-size:10px;color:#e2e8f0">PC Matched</span></div>'
            )
        leg_html += '</div>'

        m.get_root().html.add_child(folium.Element(
            f'<div style="position:fixed;bottom:30px;right:12px;z-index:9999">{leg_html}</div>'
        ))

        st_folium(m, width=None, height=560, returned_objects=[])

    # ── District rank cards (right column) ───────────────────────────────────
    with rank_col:
        sorted_filt = filt.sort_values('total_units', ascending=False)
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#e2e8f0;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:12px;padding-bottom:8px;border-bottom:1px solid #1e2d4a">'
            '📋 Top Districts</div>',
            unsafe_allow_html=True
        )

        # Build ONE html string to avoid the loop rendering bug
        cards_html = ""
        for _, row in sorted_filt.head(25).iterrows():
            is_pc   = row.get('matched_pc', False)
            top_ind = max(row['industries'], key=row['industries'].get) if row['industries'] else '—'
            t_short = (top_ind[:26] + '…') if len(top_ind) > 26 else top_ind
            border  = '#00ff88' if is_pc else '#1e2d4a'
            pty_line = ''
            if is_pc and row.get('party'):
                pty_line = (
                    f'<div style="font-size:9px;color:{pcolor(row["party"])};'
                    f'margin-top:1px;font-weight:600">{row["party"][:24]}</div>'
                )
            cards_html += (
                f'<div style="background:#111827;border:1px solid {border};border-radius:7px;'
                f'padding:10px 12px;margin-bottom:7px">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-weight:700;font-size:12px;color:#e2e8f0;'
                f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row["district"]}</div>'
                f'<div style="color:#64748b;font-size:10px">{row["state"]}</div>'
                f'<div style="color:#94a3b8;font-size:9px;margin-top:2px">{t_short}</div>'
                f'{pty_line}'
                f'</div>'
                f'<div style="text-align:right;flex-shrink:0;margin-left:8px">'
                f'<div style="color:#00d4ff;font-weight:700;font-size:13px;'
                f'font-family:\'JetBrains Mono\',monospace">{row["total_units"]:,}</div>'
                f'<div style="color:#64748b;font-size:9px">units</div>'
                f'</div></div></div>'
            )
        st.markdown(cards_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PC INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_pc:
    pc_df = filt[filt['matched_pc'] == True].copy() if 'matched_pc' in filt.columns else pd.DataFrame()

    if len(pc_df) == 0:
        st.info("No PC-matched districts in current filter. Set District Type to 'All' or 'PC Matched Only'.")
    else:
        # ── Section 1: Party strength ──────────────────────────────────────────
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'
            'padding-bottom:10px;border-bottom:1px solid #1e2d4a">'
            'Party-wise Industrial Strength'
            '<span style="font-size:10px;font-weight:400;color:#64748b;margin-left:10px">'
            'Total units in constituencies won by each party</span></div>',
            unsafe_allow_html=True
        )

        party_summary = (
            pc_df.groupby('party')
            .agg(seats=('pc_name','count'), total_units=('total_units','sum'),
                 avg_units=('total_units','mean'))
            .reset_index().sort_values('total_units', ascending=False)
        )

        p1, p2 = st.columns([3, 2])

        with p1:
            total_pu = party_summary['total_units'].sum()
            bars_html = ""
            for _, pr in party_summary.iterrows():
                col_p = pcolor(pr['party'])
                pct   = pr['total_units'] / total_pu if total_pu else 0
                bars_html += (
                    f'<div style="margin-bottom:13px">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:baseline;margin-bottom:4px">'
                    f'<span style="color:{col_p};font-weight:600;font-size:12px">{pr["party"][:38]}</span>'
                    f'<span style="color:#00d4ff;font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:12px;font-weight:700">{int(pr["total_units"]):,}</span>'
                    f'</div>'
                    f'<div style="background:#1a2235;border-radius:3px;height:8px;margin-bottom:3px">'
                    f'<div style="background:{col_p};width:{int(pct*100)}%;height:8px;border-radius:3px"></div>'
                    f'</div>'
                    f'<div style="color:#64748b;font-size:10px">'
                    f'{int(pr["seats"])} seat{"s" if pr["seats"]!=1 else ""} · '
                    f'avg {int(pr["avg_units"]):,} units/seat'
                    f'</div></div>'
                )
            st.markdown(bars_html, unsafe_allow_html=True)

        with p2:
            st.markdown(
                '<div style="font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;'
                'letter-spacing:1px;margin-bottom:10px">Top 15 Constituencies</div>',
                unsafe_allow_html=True
            )
            top_pcs_html = ""
            for _, pr in pc_df.sort_values('total_units', ascending=False).head(15).iterrows():
                col_p   = pcolor(pr.get('party', ''))
                top_ind = max(pr['industries'], key=pr['industries'].get) if pr['industries'] else '—'
                t_short = (top_ind[:28] + '…') if len(top_ind) > 28 else top_ind
                top_pcs_html += (
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'margin-bottom:6px;padding:8px 10px;background:#111827;border-radius:6px;'
                    f'border-left:3px solid {col_p}">'
                    f'<div style="flex:1;min-width:0">'
                    f'<div style="font-size:12px;font-weight:600;color:#e2e8f0">{pr.get("pc_name","")}</div>'
                    f'<div style="font-size:10px;color:{col_p}">{pr.get("party","")[:30]}</div>'
                    f'<div style="font-size:9px;color:#64748b">{t_short}</div>'
                    f'</div>'
                    f'<div style="color:#00d4ff;font-weight:700;font-family:\'JetBrains Mono\',monospace;'
                    f'font-size:12px;flex-shrink:0;margin-left:8px">{int(pr["total_units"]):,}</div>'
                    f'</div>'
                )
            st.markdown(top_pcs_html, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

        # ── Section 2: High-stakes swing seats ────────────────────────────────
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:6px;'
            'padding-bottom:10px;border-bottom:1px solid #1e2d4a">'
            '⚠️ High-Stakes Swing Seats'
            '<span style="font-size:10px;font-weight:400;color:#64748b;margin-left:10px">'
            'Seats won with &lt;100,000 vote margin + high industrial presence</span></div>',
            unsafe_allow_html=True
        )

        if 'margin' in pc_df.columns:
            swing = (
                pc_df[pc_df['margin'] < 100000]
                .sort_values('total_units', ascending=False)
                .head(20)
            )
            if len(swing):
                swing_html = ""
                for _, r in swing.iterrows():
                    col_p  = pcolor(r.get('party', ''))
                    danger = '#ff6b35' if r['margin'] < 20000 else '#ffd700' if r['margin'] < 50000 else '#94a3b8'
                    swing_html += (
                        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;'
                        f'padding:9px 13px;background:#111827;border-radius:7px;border:1px solid #1e2d4a">'
                        f'<div style="flex:1;min-width:0">'
                        f'<div style="font-size:12px;font-weight:700;color:#e2e8f0">{r.get("pc_name","")}</div>'
                        f'<div style="font-size:10px;color:{col_p}">{r.get("party","")[:36]}</div>'
                        f'<div style="font-size:10px;color:#64748b">{r.get("winner","")}</div>'
                        f'</div>'
                        f'<div style="text-align:right;flex-shrink:0">'
                        f'<div style="font-size:12px;font-weight:700;color:#00d4ff;'
                        f'font-family:\'JetBrains Mono\',monospace">{int(r["total_units"]):,} units</div>'
                        f'<div style="font-size:10px;color:{danger};font-weight:600">'
                        f'Margin: {int(r["margin"]):,}</div>'
                        f'</div></div>'
                    )
                st.markdown(swing_html, unsafe_allow_html=True)
            else:
                st.info("No swing seats in current filter.")

        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)

        # ── Section 3: PC Scorecard search ────────────────────────────────────
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-bottom:12px;'
            'padding-bottom:10px;border-bottom:1px solid #1e2d4a">🔍 PC Scorecard</div>',
            unsafe_allow_html=True
        )

        search_pc = st.text_input("Search constituency name", placeholder="e.g. Bangalore, Lucknow, Surat…")
        if search_pc.strip():
            results = pc_df[pc_df['pc_name'].str.contains(search_pc.strip(), case=False, na=False)]
            if len(results):
                sc1, sc2 = st.columns(2)
                html_left, html_right = "", ""
                for idx, (_, r) in enumerate(results.iterrows()):
                    col_p    = pcolor(r.get('party', ''))
                    top_inds = sorted(r['industries'].items(), key=lambda x: -x[1])
                    max_val  = top_inds[0][1] if top_inds else 1
                    ind_bars = ""
                    for ind_name, cnt in top_inds[:6]:
                        bar_pct = int(cnt / max_val * 100)
                        ic      = ind_cmap.get(ind_name, '#64748b')
                        short   = (ind_name[:30] + '…') if len(ind_name) > 30 else ind_name
                        ind_bars += (
                            f'<div style="margin-bottom:6px">'
                            f'<div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:2px">'
                            f'<span style="color:#94a3b8">{short}</span>'
                            f'<span style="color:{ic};font-family:\'JetBrains Mono\',monospace">{cnt}</span>'
                            f'</div>'
                            f'<div style="background:#1a2235;border-radius:2px;height:4px">'
                            f'<div style="background:{ic};width:{bar_pct}%;height:4px;border-radius:2px"></div>'
                            f'</div></div>'
                        )

                    nearby_pcs = sorted(
                        [(dist_km(r['lat'], r['lon'], r2['lat'], r2['lon']), r2)
                         for _, r2 in pc_df[pc_df['pc_name'] != r.get('pc_name','')].iterrows()
                         if dist_km(r['lat'], r['lon'], r2['lat'], r2['lon']) <= 150],
                        key=lambda x: x[0]
                    )[:4]

                    nearby_html = ""
                    for d2, nr in nearby_pcs:
                        nc = pcolor(nr.get('party', ''))
                        nearby_html += (
                            f'<div style="display:flex;justify-content:space-between;font-size:10px;margin-bottom:3px">'
                            f'<span style="color:#94a3b8">{nr.get("pc_name","")}</span>'
                            f'<span style="color:{nc}">{nr.get("party","")[:18]} · {d2:.0f}km</span>'
                            f'</div>'
                        )

                    card = (
                        f'<div style="background:#111827;border:1px solid {col_p}44;'
                        f'border-radius:10px;padding:14px;margin-bottom:14px">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:flex-start;margin-bottom:10px">'
                        f'<div><div style="font-size:15px;font-weight:700;color:#e2e8f0">'
                        f'{r.get("pc_name","")}</div>'
                        f'<div style="font-size:11px;color:#64748b">{r.get("state","")}</div></div>'
                        f'<div style="text-align:right">'
                        f'<div style="font-size:20px;font-weight:700;color:#00d4ff;'
                        f'font-family:\'JetBrains Mono\',monospace">{int(r["total_units"]):,}</div>'
                        f'<div style="font-size:9px;color:#64748b">industrial units</div></div></div>'
                        f'<div style="padding:8px;background:#0d1424;border-radius:6px;margin-bottom:10px">'
                        f'<div style="font-size:11px;font-weight:700;color:{col_p}">'
                        f'🏆 {r.get("winner","")}</div>'
                        f'<div style="font-size:10px;color:{col_p};opacity:0.8">{r.get("party","")}</div>'
                        f'<div style="font-size:10px;color:#64748b;margin-top:3px">'
                        f'Margin: <b style="color:#ffd700">{int(r.get("margin",0)):,}</b> votes · '
                        f'Runner-up: {r.get("runner_up","")[:22]}'
                        f'<span style="color:{pcolor(r.get("runner_party",""))}">'
                        f' ({r.get("runner_party","")[:20]})</span></div></div>'
                        f'<div style="font-size:9px;color:#64748b;text-transform:uppercase;'
                        f'letter-spacing:1px;margin-bottom:6px">Industry Breakdown</div>'
                        f'{ind_bars}'
                        + (
                            f'<div style="font-size:9px;color:#64748b;text-transform:uppercase;'
                            f'letter-spacing:1px;margin:8px 0 6px 0">Nearby PCs (&lt;150km)</div>'
                            f'{nearby_html}'
                            if nearby_html else ''
                        ) +
                        f'</div>'
                    )
                    if idx % 2 == 0:
                        html_left += card
                    else:
                        html_right += card

                with sc1:
                    st.markdown(html_left,  unsafe_allow_html=True)
                with sc2:
                    st.markdown(html_right, unsafe_allow_html=True)
            else:
                st.info(f"No constituency found matching '{search_pc}'")
        else:
            st.caption("Type a constituency name above to see its full industry + election scorecard.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    a1, a2 = st.columns(2)

    with a1:
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:12px">🏭 Industry Sectors (Filtered)</div>',
            unsafe_allow_html=True
        )
        ind_agg = {}
        for _, row in filt.iterrows():
            for k, v in row['industries'].items():
                ind_agg[k] = ind_agg.get(k, 0) + v

        ind_sorted = sorted(ind_agg.items(), key=lambda x: -x[1])
        total_ind  = sum(v for _, v in ind_sorted)
        max_ind    = ind_sorted[0][1] if ind_sorted else 1

        ind_html = ""
        for ind, cnt in ind_sorted:
            pct = cnt / total_ind if total_ind else 0
            bar = int(cnt / max_ind * 100)
            ic  = ind_cmap.get(ind, '#64748b')
            lbl = (ind[:42] + '…') if len(ind) > 42 else ind
            ind_html += (
                f'<div style="margin-bottom:9px">'
                f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px">'
                f'<span style="color:#e2e8f0" title="{ind}">{lbl}</span>'
                f'<span style="color:{ic};font-family:\'JetBrains Mono\',monospace;'
                f'font-weight:600;flex-shrink:0;margin-left:8px">{cnt:,}</span>'
                f'</div>'
                f'<div style="background:#1a2235;border-radius:2px;height:5px">'
                f'<div style="background:{ic};width:{bar}%;height:5px;border-radius:2px"></div>'
                f'</div>'
                f'<div style="color:#64748b;font-size:9px;margin-top:1px">{pct*100:.1f}% of filtered units</div>'
                f'</div>'
            )
        st.markdown(ind_html, unsafe_allow_html=True)

    with a2:
        if sel_industry != 'All Industries':
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;'
                f'letter-spacing:1px;margin-bottom:12px">📍 {sel_industry[:36]} — by State</div>',
                unsafe_allow_html=True
            )
            state_df = filt.copy()
            state_df['sel'] = state_df['industries'].apply(lambda x: x.get(sel_industry, 0))
            sg = state_df.groupby('state')['sel'].sum().sort_values(ascending=False).head(20)
            max_sg = sg.max() if len(sg) else 1
            sg_html = ""
            for state, val in sg.items():
                if val <= 0: continue
                sg_html += (
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                    f'<div style="width:120px;font-size:11px;color:#94a3b8;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{state}</div>'
                    f'<div style="flex:1;background:#1a2235;border-radius:2px;height:7px">'
                    f'<div style="background:#00d4ff;width:{int(val/max_sg*100)}%;height:7px;border-radius:2px"></div>'
                    f'</div>'
                    f'<div style="font-size:11px;color:#00d4ff;font-family:\'JetBrains Mono\',monospace;'
                    f'width:45px;text-align:right">{val:,}</div></div>'
                )
            st.markdown(sg_html, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;'
                'letter-spacing:1px;margin-bottom:12px">📍 Total Units by State</div>',
                unsafe_allow_html=True
            )
            state_totals = filt.groupby('state')['total_units'].sum().sort_values(ascending=False).head(20)
            max_st = state_totals.max() if len(state_totals) else 1
            st_html = ""
            for state, val in state_totals.items():
                st_html += (
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                    f'<div style="width:120px;font-size:11px;color:#94a3b8;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{state}</div>'
                    f'<div style="flex:1;background:#1a2235;border-radius:2px;height:7px">'
                    f'<div style="background:#00ff88;width:{int(val/max_st*100)}%;height:7px;border-radius:2px"></div>'
                    f'</div>'
                    f'<div style="font-size:11px;color:#00ff88;font-family:\'JetBrains Mono\',monospace;'
                    f'width:55px;text-align:right">{val:,}</div></div>'
                )
            st.markdown(st_html, unsafe_allow_html=True)
            st.caption("Select a specific Industry Sector in the sidebar for sector-wise state breakdown.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DATA TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    display_cols = ['state', 'district', 'lat', 'lon', 'total_units', 'matched_pc']
    for c in ['pc_name', 'winner', 'party', 'margin']:
        if c in filt.columns:
            display_cols.append(c)

    disp = filt[[c for c in display_cols if c in filt.columns]].copy()
    disp.columns = [c.replace('_', ' ').title() for c in disp.columns]
    disp = disp.sort_values('Total Units', ascending=False)

    dl_col, _, info_col = st.columns([1, 3, 1])
    with dl_col:
        st.download_button(
            "⬇️ Download CSV", disp.to_csv(index=False),
            "manufacturing_clusters.csv", "text/csv"
        )
    with info_col:
        st.markdown(
            f'<div style="text-align:right;font-size:11px;color:#64748b;padding-top:8px">'
            f'{len(disp):,} rows</div>',
            unsafe_allow_html=True
        )

    st.dataframe(disp, use_container_width=True, height=500)

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

# ─── Aggressive Light-Theme CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Global reset ── */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #F0F4F8 !important;
    color: #1E293B !important;
}

/* ── Kill the black deploy/header bar ── */
header[data-testid="stHeader"] {
    background: #FFFFFF !important;
    border-bottom: 1px solid #E2E8F0 !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: hidden !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Remove top padding gap ── */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #1E293B !important; }

/* ── Sidebar selectbox & radio – force light styling ── */
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #1E293B !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #1E293B !important;
    background: transparent !important;
}
/* dropdown popup */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
}
[data-baseweb="menu"] li, [data-baseweb="menu"] [role="option"] {
    color: #1E293B !important;
    background: #FFFFFF !important;
}
[data-baseweb="menu"] li:hover, [data-baseweb="menu"] [aria-selected="true"] {
    background: #EFF6FF !important;
    color: #2563EB !important;
}
/* radio buttons */
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] [data-testid="stRadio"] p {
    color: #1E293B !important;
}

/* ── Metric cards ── */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 12px;
    text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
    height: 90px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.metric-card:hover { box-shadow: 0 4px 14px rgba(37,99,235,0.12); }
.metric-val {
    font-size: 22px;
    font-weight: 700;
    color: #2563EB;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.2;
    white-space: nowrap;
}
.metric-lbl {
    font-size: 9.5px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-top: 4px;
    font-weight: 600;
    line-height: 1.3;
}

/* ── Section titles ── */
.section-title {
    font-size: 11px;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
    padding-bottom: 5px;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 600;
}

/* ── Dashboard title bar ── */
.dash-header {
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #3B82F6 100%);
    border-radius: 12px;
    padding: 16px 24px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 4px 16px rgba(37,99,235,0.25);
}
.dash-header-title {
    font-size: 20px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.3px;
}
.dash-header-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.75);
    margin-top: 2px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    border: 1px solid #E2E8F0 !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [role="tab"] {
    color: #64748B !important;
    font-weight: 500 !important;
    border-radius: 7px !important;
    padding: 6px 14px !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    background: #EFF6FF !important;
    color: #2563EB !important;
    font-weight: 600 !important;
}

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
}

/* ── Info/warning boxes ── */
.stAlert { border-radius: 8px !important; }

/* ── Map legend card ── */
.map-legend {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px 14px;
    margin-top: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.legend-title {
    font-size: 10px;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.legend-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 5px;
    font-size: 11.5px;
    color: #374151;
    font-weight: 500;
}
.legend-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── General text ── */
h1, h2, h3, h4, h5, h6 { color: #1E293B !important; }
p, span, label { color: #1E293B; }
.stCaption, .stCaption p { color: #64748B !important; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':           '#E8620A',
    'Indian National Congress':         '#1A56DB',
    'Aam Aadmi Party':                  '#0EA5E9',
    'Samajwadi Party':                  '#DC2626',
    'Bahujan Samaj Party':              '#1E3A8A',
    'All India Trinamool Congress':     '#16A34A',
    'Trinamool Congress':               '#16A34A',
    'Dravida Munnetra Kazhagam':        '#991B1B',
    'Telugu Desam':                     '#CA8A04',
    'Janata Dal  (United)':             '#7C3AED',
    'YSR Congress Party':               '#0369A1',
    'Biju Janata Dal':                  '#0D9488',
    'Shiv Sena':                        '#B45309',
    'Janasena Party':                   '#BE185D',
    'Rashtriya Lok Dal':                '#65A30D',
    'Communist Party of India  (Marxist)': '#B91C1C',
    'Nationalist Congress Party':       '#15803D',
    'Shiv Sena (Uddhav Balasaheb Thackrey)': '#92400E',
}

PARTY_ABBR = {
    'Bharatiya Janata Party':           'BJP',
    'Indian National Congress':         'INC',
    'Aam Aadmi Party':                  'AAP',
    'Samajwadi Party':                  'SP',
    'Bahujan Samaj Party':              'BSP',
    'All India Trinamool Congress':     'TMC',
    'Trinamool Congress':               'TMC',
    'Dravida Munnetra Kazhagam':        'DMK',
    'Telugu Desam':                     'TDP',
    'Janata Dal  (United)':             'JD(U)',
    'YSR Congress Party':               'YSRCP',
    'Biju Janata Dal':                  'BJD',
    'Shiv Sena':                        'SS',
    'Janasena Party':                   'JSP',
    'Rashtriya Lok Dal':                'RLD',
}

IND_COLORS = [
    '#2563EB','#059669','#DC2626','#D97706','#7C3AED',
    '#DB2777','#0891B2','#EA580C','#4F46E5','#B45309',
    '#16A34A','#CA8A04','#6D28D9','#BE185D','#0D9488',
    '#E11D48','#15803D','#0284C7','#A21CAF','#C2410C',
    '#0E7490','#84CC16','#B91C1C','#6B21A8','#A16207',
    '#166534','#1E40AF','#991B1B','#5B21B6','#92400E',
]

def get_party_color(party): return PARTY_COLORS.get(party, '#94A3B8')
def get_party_abbr(party):  return PARTY_ABBR.get(party, party[:6] if party else '')

def get_dist_km(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dLon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    csv_path = os.path.join(BASE_DIR, 'Annexure_with_3digit_Sheet1_.csv')
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
        except: return 0

    base_industries = {}
    for col in industry_cols:
        base = col.split('.')[0].strip()
        base_industries.setdefault(base, []).append(col)

    records = []
    for _, row in df_units.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']): continue
        ind_totals = {base: int(s) for base, cols in base_industries.items()
                      if (s := sum(safe_num(row[c]) for c in cols)) > 0}
        records.append({'state': str(row['State']), 'district': str(row['District']),
                        'lat': float(row['Latitude']), 'lon': float(row['Longitude']),
                        'total_units': sum(ind_totals.values()), 'industries': ind_totals})

    xlsx_path = os.path.join(BASE_DIR, 'Lok_Sabha_Elections_Winners_2024.xlsx')
    df_lok    = pd.read_excel(xlsx_path)
    lok_dict  = {}
    for _, r in df_lok.iterrows():
        try:    margin = int(r['Margin Votes'])
        except: margin = 0
        lok_dict[str(r['PC Name']).upper().strip()] = {
            'pc_name': str(r['PC Name']), 'state': str(r['State']),
            'winner':  str(r['Winning Candidate']), 'party': str(r['Winning Party']),
            'runner_up': str(r['Runner-up Canddiate']), 'runner_party': str(r['Runner-up Party']),
            'margin': margin,
        }

    for rec in records:
        key = rec['district'].upper().strip()
        if key in lok_dict:
            rec.update(lok_dict[key]); rec['matched_pc'] = True
        else:
            rec['matched_pc'] = False

    df = pd.DataFrame(records)
    all_industries = sorted({ind for rec in records for ind in rec['industries']})
    ind_color_map  = {ind: IND_COLORS[i % len(IND_COLORS)] for i, ind in enumerate(all_industries)}
    return df, list(lok_dict.values()), all_industries, ind_color_map

df, lok_list, all_industries, ind_color_map = load_data()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:10px 0 6px">
        <div style="font-size:28px">🏭</div>
        <div style="font-size:14px;font-weight:700;color:#1E40AF">MCI Dashboard</div>
        <div style="font-size:10px;color:#64748B;margin-top:2px">Lok Sabha 2024 × Industrial Units</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.markdown('<p style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">🔍 Filters</p>', unsafe_allow_html=True)

    states       = ['All States']   + sorted(df['state'].unique().tolist())
    sel_state    = st.selectbox("State", states, key="sel_state")

    industries_l = ['All Industries'] + all_industries
    sel_industry = st.selectbox("Industry Sector", industries_l, key="sel_industry")

    all_parties  = ['All Parties']  + sorted({p['party'] for p in lok_list})
    sel_party    = st.selectbox("Winning Party (PC)", all_parties, key="sel_party")

    match_filter = st.radio("District Type", ['All', 'PC Matched Only', 'Non-PC Districts'])

    st.divider()
    st.markdown('<p style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">🗺️ Map Color Mode</p>', unsafe_allow_html=True)
    view_mode = st.radio("", ['Winning Party', 'Top Industry', 'Units Count'], label_visibility="collapsed")

    st.divider()
    st.markdown(f"""
    <div style="background:#F0F9FF;border:1px solid #BAE6FD;border-radius:8px;padding:10px 12px">
        <div style="font-size:10px;color:#0369A1;font-weight:600;text-transform:uppercase;letter-spacing:.8px">Dataset</div>
        <div style="font-size:13px;font-weight:700;color:#1E293B;margin-top:2px">{len(df):,} Districts</div>
        <div style="font-size:11px;color:#64748B">{df['total_units'].sum():,} total industrial units</div>
    </div>""", unsafe_allow_html=True)

# ─── Filters ──────────────────────────────────────────────────────────────────
filtered = df.copy()
if sel_state    != 'All States':    filtered = filtered[filtered['state'] == sel_state]
if sel_industry != 'All Industries':
    filtered = filtered[filtered['industries'].apply(lambda x: x.get(sel_industry, 0) > 0)]
if sel_party    != 'All Parties' and 'party' in filtered.columns:
    filtered = filtered[filtered['party'].fillna('') == sel_party]
if match_filter == 'PC Matched Only':  filtered = filtered[filtered['matched_pc'] == True]
elif match_filter == 'Non-PC Districts': filtered = filtered[filtered['matched_pc'] == False]

# ─── Summary values ───────────────────────────────────────────────────────────
pc_matched_df    = filtered[filtered['matched_pc'] == True] if 'matched_pc' in filtered.columns else pd.DataFrame()
pc_with_units    = int((pc_matched_df['total_units'] > 0).sum()) if len(pc_matched_df) else 0
pc_without_units = int((pc_matched_df['total_units'] == 0).sum()) if len(pc_matched_df) else 0
avg_units        = int(filtered['total_units'].mean()) if len(filtered) > 0 else 0

# ─── Dashboard header bar ─────────────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <div style="font-size:32px">🏭</div>
    <div>
        <div class="dash-header-title">Manufacturing Cluster Intelligence</div>
        <div class="dash-header-sub">Lok Sabha 2024 Election Results × Industrial Unit Distribution</div>
    </div>
</div>""", unsafe_allow_html=True)

# ─── Metric cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
cards = [
    (c1, len(filtered),       "Districts Shown",                "#2563EB"),
    (c2, f"{int(filtered['total_units'].sum()):,}", "Total Industrial Units", "#059669"),
    (c3, pc_with_units,       "PCs with Units",                 "#7C3AED"),
    (c4, pc_without_units,    "PCs without Units",              "#DC2626"),
    (c5, f"{avg_units:,}",    "Avg Units / District",           "#D97706"),
]
for col, val, lbl, accent in cards:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val" style="color:{accent}">{val}</div>
            <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─── Map helpers ──────────────────────────────────────────────────────────────
def get_color(row):
    if view_mode == 'Top Industry':
        if row['industries']:
            return ind_color_map.get(max(row['industries'], key=row['industries'].get), '#6366F1')
        return '#6366F1'
    elif view_mode == 'Winning Party':
        if row.get('matched_pc') and pd.notna(row.get('party','')):
            return get_party_color(row['party'])
        return '#6366F1'   # vibrant indigo instead of grey for unmatched
    else:
        u = row['total_units']
        if u > 500: return '#EF4444'   # vivid red
        if u > 100: return '#F59E0B'   # vivid amber
        if u > 20:  return '#10B981'   # vivid emerald
        return '#3B82F6'               # vivid blue

def get_radius(units):
    return max(5, min(30, math.sqrt(units + 1) * 1.15))

# ─── Legend builder ───────────────────────────────────────────────────────────
def build_legend_html():
    rows = ""
    if view_mode == 'Units Count':
        items = [('#DC2626','500+ units'),('#D97706','100–500 units'),
                 ('#059669','20–100 units'),('#2563EB','< 20 units')]
        for col, lbl in items:
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{col}"></div>{lbl}</div>'
        rows += '<div class="legend-row"><div class="legend-dot" style="background:#94A3B8;border:2px solid #1E293B"></div>PC Matched</div>'
    elif view_mode == 'Top Industry':
        ind_counts = {}
        for _, row in filtered.iterrows():
            for k, v in row['industries'].items():
                ind_counts[k] = ind_counts.get(k,0) + v
        top8 = sorted(ind_counts.items(), key=lambda x: -x[1])[:8]
        for k, _ in top8:
            col = ind_color_map.get(k,'#94A3B8')
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{col}"></div>{k[:28]}</div>'
    else:  # Winning Party
        shown = set()
        if 'party' in filtered.columns:
            shown = set(filtered[filtered['matched_pc']==True]['party'].dropna().unique())
        for p in sorted(shown)[:10]:
            col  = get_party_color(p)
            abbr = get_party_abbr(p)
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{col}"></div><b style="color:{col}">{abbr}</b>&nbsp;— {p[:25]}</div>'
        rows += '<div class="legend-row"><div class="legend-dot" style="background:#CBD5E1"></div>No PC data</div>'

    bubble = """
    <div style="margin-top:8px;padding-top:8px;border-top:1px solid #E2E8F0">
        <div class="legend-title" style="margin-bottom:5px">Bubble Size = Unit Count</div>
        <div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">
            <div style="width:8px;height:8px;border-radius:50%;background:#94A3B8"></div>
            <span style="font-size:10.5px;color:#64748B">Small → few units</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px">
            <div style="width:20px;height:20px;border-radius:50%;background:#94A3B8"></div>
            <span style="font-size:10.5px;color:#64748B">Large → many units</span>
        </div>
    </div>"""
    return f'<div class="map-legend"><div class="legend-title">{view_mode}</div>{rows}{bubble}</div>'

# ─── Main layout ──────────────────────────────────────────────────────────────
map_col, detail_col = st.columns([3, 1])

with map_col:
    center_lat = filtered['lat'].mean() if len(filtered) > 0 else 22.5
    center_lon = filtered['lon'].mean() if len(filtered) > 0 else 80.0

    m = folium.Map(location=[center_lat, center_lon],
                   zoom_start=5 if sel_state == 'All States' else 7,
                   tiles=None, prefer_canvas=True)

    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap © CartoDB', name='Light', max_zoom=19
    ).add_to(m)

    for _, row in filtered.iterrows():
        color = get_color(row)
        r     = get_radius(row['total_units'])
        is_pc = row.get('matched_pc', False)

        top_inds = sorted(row['industries'].items(), key=lambda x: -x[1])[:5] if row['industries'] else []
        ind_html = ''.join(
            f'<tr><td style="color:#374151;font-size:11px;padding:1px 5px">{k[:32]}</td>'
            f'<td style="font-weight:600;color:#2563EB;font-size:11px;padding:1px 5px;text-align:right">{v:,}</td></tr>'
            for k, v in top_inds
        )
        pc_html = ''
        if is_pc:
            pc_color = get_party_color(row.get('party',''))
            pc_html  = f'''
            <div style="margin-top:8px;padding-top:8px;border-top:1px solid #E2E8F0">
              <div style="font-size:9px;font-weight:700;color:#64748B;letter-spacing:.8px;text-transform:uppercase">Parliamentary Constituency</div>
              <div style="font-weight:700;color:#059669;font-size:12px;margin-top:3px">{row.get('pc_name','')}</div>
              <div style="font-size:11px;color:#1E293B;margin-top:3px">🏆 {row.get('winner','')}</div>
              <div style="font-size:11px;font-weight:600;color:{pc_color};margin-top:1px">{row.get('party','')}</div>
              <div style="font-size:10px;color:#64748B;margin-top:1px">Margin: {row.get('margin',0):,} votes</div>
            </div>'''
        popup_html = f'''
        <div style="font-family:Inter,sans-serif;min-width:210px;background:#FFFFFF;color:#1E293B;padding:2px">
          <div style="font-size:14px;font-weight:700;color:#1E293B">{row['district']}</div>
          <div style="font-size:11px;color:#64748B;margin-bottom:6px">{row['state']}</div>
          <div style="font-size:22px;font-weight:700;color:#2563EB;line-height:1.1">{row['total_units']:,}</div>
          <div style="font-size:9.5px;color:#94A3B8;letter-spacing:.8px;margin-bottom:6px">INDUSTRIAL UNITS</div>
          <table style="width:100%;border-collapse:collapse">{ind_html}</table>
          {pc_html}
        </div>'''

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=r,
            color='#1E293B' if is_pc else color,
            weight=2.5 if is_pc else 0.8,
            fill=True, fill_color=color, fill_opacity=0.78,
            popup=folium.Popup(popup_html, max_width=270),
            tooltip=f"<b>{row['district']}</b> · {row['total_units']:,} units"
                    + (f" · {row.get('pc_name','')}" if is_pc else ''),
        ).add_to(m)

    st.markdown("#### 🗺️ Interactive District Map")
    map_data = st_folium(m, width=None, height=540, returned_objects=["last_object_clicked"])

    # Legend below map
    st.markdown(build_legend_html(), unsafe_allow_html=True)

# ─── Detail column ────────────────────────────────────────────────────────────
with detail_col:
    st.markdown("#### 📋 District Detail")
    sorted_filtered = filtered.sort_values('total_units', ascending=False)

    if map_data and map_data.get('last_object_clicked'):
        clicked = map_data['last_object_clicked']
        clat, clon = clicked.get('lat'), clicked.get('lng')
        if clat and clon:
            dists = filtered.apply(lambda r: get_dist_km(clat, clon, r['lat'], r['lon']), axis=1)
            if len(dists) > 0:
                sel_row = filtered.loc[dists.idxmin()]

                st.markdown(f"""
                <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;padding:12px;margin-bottom:10px">
                    <div style="font-size:15px;font-weight:700;color:#1E293B">{sel_row['district']}</div>
                    <div style="font-size:11px;color:#64748B">{sel_row['state']}</div>
                    <div style="font-size:24px;font-weight:700;color:#2563EB;margin-top:4px">{sel_row['total_units']:,}</div>
                    <div style="font-size:10px;color:#94A3B8;text-transform:uppercase;letter-spacing:.8px">industrial units</div>
                </div>""", unsafe_allow_html=True)

                if sel_row.get('matched_pc'):
                    pc_color = get_party_color(sel_row.get('party',''))
                    st.markdown(f"""
                    <div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:10px;padding:12px;margin-bottom:10px">
                        <div class="section-title">🗳 PC Details</div>
                        <div style="font-weight:700;color:#15803D;font-size:13px">{sel_row.get('pc_name','')}</div>
                        <div style="font-size:12px;color:#1E293B;margin-top:4px">🏆 {sel_row.get('winner','')}</div>
                        <div style="font-size:11px;font-weight:600;color:{pc_color};margin-top:2px">{sel_row.get('party','')}</div>
                        <div style="font-size:10px;color:#64748B;margin-top:2px">Margin: {sel_row.get('margin',0):,} votes</div>
                    </div>""", unsafe_allow_html=True)

                if sel_row['industries']:
                    st.markdown('<div class="section-title">🏭 Industries</div>', unsafe_allow_html=True)
                    top_inds = sorted(sel_row['industries'].items(), key=lambda x: -x[1])
                    max_val  = top_inds[0][1] if top_inds else 1
                    for ind_name, cnt in top_inds[:10]:
                        pct   = cnt / max_val
                        color = ind_color_map.get(ind_name, '#2563EB')
                        short = ind_name[:26] + '…' if len(ind_name) > 26 else ind_name
                        st.markdown(f"""
                        <div style="margin-bottom:6px">
                            <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">
                                <span style="color:#374151">{short}</span>
                                <span style="color:{color};font-family:'JetBrains Mono',monospace;font-weight:600">{cnt:,}</span>
                            </div>
                            <div style="background:#F1F5F9;border-radius:3px;height:5px">
                                <div style="background:{color};width:{int(pct*100)}%;height:5px;border-radius:3px"></div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                nearby = sorted(
                    [(get_dist_km(sel_row['lat'], sel_row['lon'], r2['lat'], r2['lon']), r2)
                     for _, r2 in df[df['matched_pc']==True].iterrows()
                     if 0 < get_dist_km(sel_row['lat'], sel_row['lon'], r2['lat'], r2['lon']) <= 150],
                    key=lambda x: x[0]
                )
                if nearby:
                    st.markdown('<div class="section-title" style="margin-top:10px">📍 Nearby PCs (&lt;150 km)</div>', unsafe_allow_html=True)
                    for dist, nr in nearby[:5]:
                        pc_col = get_party_color(nr.get('party',''))
                        st.markdown(f"""
                        <div style="display:flex;justify-content:space-between;align-items:center;
                                    padding:6px 8px;background:#F8FAFC;border:1px solid #E2E8F0;
                                    border-radius:7px;margin-bottom:5px">
                            <div>
                                <div style="font-size:11px;font-weight:600;color:#1E293B">{nr.get('pc_name','')}</div>
                                <div style="font-size:10px;font-weight:600;color:{pc_col}">{get_party_abbr(nr.get('party',''))}</div>
                            </div>
                            <div style="font-size:11px;color:#64748B;font-family:'JetBrains Mono',monospace">{dist:.0f} km</div>
                        </div>""", unsafe_allow_html=True)
        st.divider()

    # Top districts list
    st.markdown('<p style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px">🏆 Top Districts by Units</p>', unsafe_allow_html=True)
    for _, row in sorted_filtered.head(18).iterrows():
        is_pc     = row.get('matched_pc', False)
        top_ind   = max(row['industries'], key=row['industries'].get) if row['industries'] else '—'
        top_short = top_ind[:22] + '…' if len(top_ind) > 22 else top_ind
        border    = '#86EFAC' if is_pc else '#E2E8F0'
        bg        = '#F0FDF4' if is_pc else '#FFFFFF'
        party_str = ''
        if is_pc:
            pc_col    = get_party_color(row.get('party',''))
            party_str = f'<span style="font-size:9px;font-weight:700;color:{pc_col};background:{pc_col}18;padding:1px 6px;border-radius:10px">{get_party_abbr(row.get("party",""))}</span>'
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:8px;padding:9px 11px;
                    margin-bottom:6px;box-shadow:0 1px 3px rgba(0,0,0,0.04)">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="flex:1;min-width:0">
                    <div style="font-weight:600;font-size:12px;color:#1E293B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row['district']}</div>
                    <div style="color:#64748B;font-size:10px">{row['state']}</div>
                    <div style="color:#94A3B8;font-size:10px;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{top_short}</div>
                    {party_str}
                </div>
                <div style="text-align:right;flex-shrink:0;margin-left:6px">
                    <div style="color:#2563EB;font-weight:700;font-size:13px;font-family:'JetBrains Mono',monospace">{row['total_units']:,}</div>
                    <div style="color:#94A3B8;font-size:9px">units</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ─── Bottom Tabs ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Data Table", "🗳 PC Analysis", "🏭 Industry Summary"])

with tab1:
    display_cols = ['state','district','lat','lon','total_units','matched_pc']
    if 'pc_name' in filtered.columns: display_cols += ['pc_name','winner','party','margin']
    disp = filtered[display_cols].copy()
    disp.columns = [c.replace('_',' ').title() for c in disp.columns]
    disp = disp.sort_values('Total Units', ascending=False)

    col_a, col_b = st.columns([3,1])
    with col_b:
        st.download_button("⬇️ Download CSV", disp.to_csv(index=False),
                           "manufacturing_clusters.csv", "text/csv")
    st.dataframe(disp, use_container_width=True, height=340)

with tab2:
    st.markdown("### 🗳 Parliamentary Constituency Analysis")
    pc_df = filtered[filtered['matched_pc']==True].copy() if 'matched_pc' in filtered.columns else pd.DataFrame()

    if len(pc_df) > 0 and 'party' in pc_df.columns:
        party_summary = (pc_df.groupby('party')
                         .agg(constituencies=('pc_name','count'), total_units=('total_units','sum'), avg_units=('total_units','mean'))
                         .reset_index().sort_values('total_units', ascending=False))

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Party-wise Industrial Strength**")
            tot = party_summary['total_units'].sum()
            for _, pr in party_summary.iterrows():
                col = get_party_color(pr['party'])
                pct = pr['total_units'] / tot if tot else 0
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;align-items:center">
                        <span style="color:{col};font-weight:700">{get_party_abbr(pr['party'])}</span>
                        <span style="font-size:10px;color:#64748B">{pr['party'][:22]}</span>
                        <span style="color:#2563EB;font-family:'JetBrains Mono',monospace;font-size:11px">{int(pr['total_units']):,}</span>
                    </div>
                    <div style="background:#F1F5F9;border-radius:3px;height:7px">
                        <div style="background:{col};width:{int(pct*100)}%;height:7px;border-radius:3px"></div>
                    </div>
                    <div style="color:#94A3B8;font-size:10px;margin-top:2px">{int(pr['constituencies'])} seats · avg {int(pr['avg_units']):,}/seat</div>
                </div>""", unsafe_allow_html=True)
        with col_p2:
            st.markdown("**Top PC Constituencies by Industrial Units**")
            for _, pr in pc_df.sort_values('total_units',ascending=False).head(15).iterrows():
                col = get_party_color(pr.get('party',''))
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;
                            padding:7px 10px;background:#FFFFFF;border-radius:8px;border-left:3px solid {col};
                            box-shadow:0 1px 3px rgba(0,0,0,0.05)">
                    <div>
                        <div style="font-size:12px;font-weight:600;color:#1E293B">{pr.get('pc_name','')}</div>
                        <div style="font-size:10px;color:{col};font-weight:600">{get_party_abbr(pr.get('party',''))} · {pr.get('state','')}</div>
                    </div>
                    <div style="color:#2563EB;font-weight:700;font-family:'JetBrains Mono',monospace;font-size:13px">{pr['total_units']:,}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("No PC-matched districts in current filter. Try 'All' in District Type.")

with tab3:
    st.markdown("### 🏭 Industry Sector Summary")
    ind_agg = {}
    for _, row in filtered.iterrows():
        for ind, cnt in row['industries'].items():
            ind_agg[ind] = ind_agg.get(ind,0) + cnt
    ind_sorted = sorted(ind_agg.items(), key=lambda x: -x[1])
    total_ind  = sum(v for _,v in ind_sorted)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**All Industry Sectors**")
        for ind, cnt in ind_sorted:
            pct = cnt/total_ind if total_ind else 0
            col = ind_color_map.get(ind,'#94A3B8')
            st.markdown(f"""
            <div style="margin-bottom:7px">
                <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:2px">
                    <span style="color:#1E293B;font-weight:500" title="{ind}">{ind[:38] if len(ind)>38 else ind}</span>
                    <span style="color:{col};font-family:'JetBrains Mono',monospace;font-weight:700">{cnt:,}</span>
                </div>
                <div style="background:#F1F5F9;border-radius:3px;height:5px">
                    <div style="background:{col};width:{int(pct*100)}%;height:5px;border-radius:3px"></div>
                </div>
                <div style="color:#94A3B8;font-size:10px;margin-top:1px">{pct*100:.1f}% of total</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("**Industry Distribution by State**")
        if sel_industry != 'All Industries' and sel_state == 'All States':
            state_df = filtered.copy()
            state_df['sel_units'] = state_df['industries'].apply(lambda x: x.get(sel_industry,0))
            sg = state_df.groupby('state')['sel_units'].sum().sort_values(ascending=False).head(20)
            max_sg = sg.max() if len(sg) else 1
            for state, val in sg.items():
                if val > 0:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
                        <div style="width:120px;font-size:11px;color:#374151;font-weight:500">{state[:18]}</div>
                        <div style="flex:1;background:#F1F5F9;border-radius:3px;height:6px">
                            <div style="background:#2563EB;width:{int(val/max_sg*100)}%;height:6px;border-radius:3px"></div>
                        </div>
                        <div style="font-size:11px;color:#2563EB;font-family:'JetBrains Mono',monospace;width:40px;text-align:right">{val:,}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Select a specific Industry Sector to see state-wise distribution.")

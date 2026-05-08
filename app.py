"""
╔══════════════════════════════════════════════════════════════════════╗
║     PC Industrial Unit Analysis — Streamlit App                     ║
║     Spatial join: industrial units × PC boundaries × election data  ║
╚══════════════════════════════════════════════════════════════════════╝

FILES NEEDED (place in same folder as this script):
  1. Annexure_with_Coordinates.xlsx   — 25,217 industrial units with lat/lon
  2. Lok_Sabha_Elections_Winners_2024.xlsx  — 2024 Lok Sabha winners
  3. india_pc_boundaries.geojson      — All-India PC polygon boundaries

INSTALL:
  pip install streamlit pandas geopandas shapely openpyxl folium streamlit-folium plotly

RUN:
  streamlit run pc_industrial_analysis_app.py
"""

import os, re, math
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PC Industrial Analysis",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html,body,[class*="css"],.stApp{font-family:'Inter',sans-serif!important;background:#F4F6F9!important;color:#1E293B!important;}
header[data-testid="stHeader"]{height:0!important;overflow:hidden!important;visibility:hidden!important;}
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"]{display:none!important;visibility:hidden!important;}
.block-container{padding-top:0!important;max-width:100%!important;}

section[data-testid="stSidebar"]{background:#FFFFFF!important;border-right:1px solid #E8ECF0!important;min-width:230px!important;max-width:230px!important;}
section[data-testid="stSidebar"] *{color:#1E293B!important;}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#F8FAFC!important;border:1px solid #E2E8F0!important;border-radius:8px!important;}
[data-baseweb="menu"]{background:#FFFFFF!important;border:1px solid #CBD5E1!important;}
[data-baseweb="menu"] li{color:#1E293B!important;background:#FFFFFF!important;}
[data-baseweb="menu"] li:hover{background:#EFF6FF!important;color:#1D4ED8!important;}

.top-bar{background:#FFFFFF;border-bottom:1px solid #E8ECF0;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.page-title{font-size:17px;font-weight:700;color:#1E293B;}

.stat-card{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:12px;padding:16px 18px;box-shadow:0 1px 4px rgba(0,0,0,.05);position:relative;overflow:visible;min-height:110px;display:flex;flex-direction:column;justify-content:space-between;gap:6px;}
.stat-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:4px 0 0 4px;}
.stat-card.blue::before{background:#1D4ED8;}
.stat-card.green::before{background:#059669;}
.stat-card.orange::before{background:#F59E0B;}
.stat-card.red::before{background:#EF4444;}
.stat-card.purple::before{background:#7C3AED;}
.stat-label{font-size:9px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:.8px;line-height:1.3;padding-right:28px;}
.stat-value{font-size:24px;font-weight:800;color:#1E293B;line-height:1;font-family:'JetBrains Mono',monospace;}
.stat-sub{font-size:10px;font-weight:600;margin-top:2px;line-height:1.4;white-space:normal;word-break:break-word;}
.stat-sub.up{color:#059669;} .stat-sub.warn{color:#F59E0B;} .stat-sub.danger{color:#EF4444;} .stat-sub.info{color:#1D4ED8;}
.stat-icon{position:absolute;top:12px;right:12px;font-size:18px;opacity:.15;}

.panel{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:12px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.05);}
.panel-title{font-size:14px;font-weight:700;color:#1E293B;margin-bottom:14px;}

.stTabs [data-baseweb="tab-list"]{background:#FFFFFF!important;border-radius:10px!important;border:1px solid #E2E8F0!important;padding:4px!important;}
.stTabs [role="tab"]{color:#64748B!important;font-weight:500!important;border-radius:7px!important;padding:6px 14px!important;font-size:13px!important;}
.stTabs [role="tab"][aria-selected="true"]{background:#EFF6FF!important;color:#1D4ED8!important;font-weight:600!important;}
[data-testid="stDataFrame"]{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':                '#F97316',
    'Indian National Congress':              '#2563EB',
    'Aam Aadmi Party':                       '#06B6D4',
    'Samajwadi Party':                       '#E11D48',
    'Bahujan Samaj Party':                   '#1E3A8A',
    'All India Trinamool Congress':          '#16A34A',
    'Trinamool Congress':                    '#16A34A',
    'Dravida Munnetra Kazhagam':             '#9F1239',
    'Telugu Desam':                          '#CA8A04',
    'Telugu Desam Party':                    '#CA8A04',
    'Janata Dal  (United)':                  '#7C3AED',
    'Janata Dal (United)':                   '#7C3AED',
    'Janata Dal  (Secular)':                 '#A855F7',
    'YSR Congress Party':                    '#0369A1',
    'Biju Janata Dal':                       '#4ADE80',
    'Shiv Sena':                             '#D97706',
    'Shiv Sena (Uddhav Balasaheb Thackeray)':'#F59E0B',
    'Janasena Party':                        '#EC4899',
    'Rashtriya Lok Dal':                     '#84CC16',
    'Communist Party of India  (Marxist)':   '#DC2626',
    'Nationalist Congress Party':            '#0D9488',
    'AJSU Party':                            '#0EA5E9',
    'Apna Dal (Soneylal)':                   '#F472B6',
    'Asom Gana Parishad':                    '#10B981',
    'Hindustani Awam Morcha':                '#6366F1',
    'Lok Janshakti Party(Ram Vilas)':        '#14B8A6',
    'Rashtriya Janata Dal':                  '#F43F5E',
    'Independent':                           '#94A3B8',
}
PARTY_ABBR = {
    'Bharatiya Janata Party':'BJP','Indian National Congress':'INC',
    'Aam Aadmi Party':'AAP','Samajwadi Party':'SP','Bahujan Samaj Party':'BSP',
    'All India Trinamool Congress':'TMC','Trinamool Congress':'TMC',
    'Dravida Munnetra Kazhagam':'DMK','Telugu Desam':'TDP','Telugu Desam Party':'TDP',
    'Janata Dal  (United)':'JD(U)','Janata Dal (United)':'JD(U)',
    'Janata Dal  (Secular)':'JD(S)','YSR Congress Party':'YSRCP',
    'Biju Janata Dal':'BJD','Shiv Sena':'SS',
    'Shiv Sena (Uddhav Balasaheb Thackeray)':'SS(UBT)',
    'Janasena Party':'JSP','Rashtriya Lok Dal':'RLD',
    'Communist Party of India  (Marxist)':'CPM','Nationalist Congress Party':'NCP',
    'AJSU Party':'AJSU','Apna Dal (Soneylal)':'Apna','Asom Gana Parishad':'AGP',
    'Hindustani Awam Morcha':'HAM','Lok Janshakti Party(Ram Vilas)':'LJP',
    'Rashtriya Janata Dal':'RJD','Independent':'IND',
}
_FALLBACK_COLORS = [
    '#6366F1','#0891B2','#65A30D','#B45309','#BE185D',
    '#0E7490','#4338CA','#15803D','#C2410C','#7E22CE',
]

def get_party_color(p):
    if not p or pd.isna(p): return '#94A3B8'
    return PARTY_COLORS.get(str(p), _FALLBACK_COLORS[abs(hash(str(p))) % len(_FALLBACK_COLORS)])

def get_party_abbr(p):
    if not p or pd.isna(p): return '—'
    return PARTY_ABBR.get(str(p), str(p)[:5])

def norm_nic(code):
    """Map 4-digit NIC code to human-readable sector."""
    try:
        c = int(float(str(code)))
    except:
        return 'Other'
    if 1000 <= c <= 1599:  return 'Food Products'
    if 1600 <= c <= 1799:  return 'Textiles & Apparel'
    if 1800 <= c <= 1999:  return 'Wood & Paper'
    if 2000 <= c <= 2199:  return 'Chemicals & Pharma'
    if 2200 <= c <= 2499:  return 'Rubber, Plastic & Non-Metallic'
    if 2500 <= c <= 2599:  return 'Fabricated Metal Products'
    if 2600 <= c <= 2799:  return 'Electronics & Machinery'
    if 2800 <= c <= 2999:  return 'Machinery & Equipment'
    if 3000 <= c <= 3399:  return 'Transport Equipment'
    if 3400 <= c <= 3999:  return 'Other Manufacturing'
    if 4000 <= c <= 4399:  return 'Electricity & Utilities'
    if 4500 <= c <= 4799:  return 'Construction'
    return 'Other'


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(version=1):
    """
    1. Read industrial units with coordinates.
    2. Read PC GeoJSON boundaries.
    3. Spatial join: assign each unit to a PC polygon.
    4. Merge election results onto PC-level summary.
    """

    # ── 1. Industrial units ──────────────────────────────────────────────
    units_path = os.path.join(BASE_DIR, 'Annexure_with_Coordinates.xlsx')
    units_df = pd.read_excel(units_path)

    # Normalise column names to safe snake_case
    units_df.columns = [c.strip() for c in units_df.columns]
    units_df = units_df.rename(columns={
        'State Name':    'state',
        'District Name': 'district',
        'Unit Name':     'unit_name',
        'NIC Code':      'nic_code',
        'Employees':     'employees',
        'Latitude':      'lat',
        'Longitude':     'lon',
        'Address':       'address',
        'Place':         'place',
    })
    units_df['lat'] = pd.to_numeric(units_df['lat'], errors='coerce')
    units_df['lon'] = pd.to_numeric(units_df['lon'], errors='coerce')
    units_df = units_df.dropna(subset=['lat', 'lon'])
    units_df['sector'] = units_df['nic_code'].apply(norm_nic)
    units_df['employees'] = pd.to_numeric(units_df['employees'], errors='coerce').fillna(0).astype(int)

    # ── 2. PC GeoJSON ────────────────────────────────────────────────────
    geojson_path = os.path.join(BASE_DIR, 'india_pc_boundaries.geojson')
    pc_gdf = gpd.read_file(geojson_path)
    pc_gdf = pc_gdf.to_crs('EPSG:4326')

    # ── Auto-detect PC name column ───────────────────────────────────────
    # Common column names across different GeoJSON sources
    PC_NAME_CANDIDATES = [
        'PC_NAME','pc_name','CONSTITUENCY','constituency',
        'CONST_NAME','const_name','NAME','name',
        'PC_No','pc_no','AC_NAME','ST_NAME'
    ]
    pc_name_col = None
    for c in PC_NAME_CANDIDATES:
        if c in pc_gdf.columns:
            pc_name_col = c
            break
    if pc_name_col is None:
        pc_name_col = pc_gdf.columns[0]   # fallback: first non-geometry col
        st.warning(f"⚠️ Could not auto-detect PC name column. Using: '{pc_name_col}'. "
                   f"Available columns: {[c for c in pc_gdf.columns if c != 'geometry']}")

    # ── Auto-detect state column in GeoJSON ─────────────────────────────
    STATE_CANDIDATES = ['ST_NAME','state','STATE','State','ST_NM']
    state_col = None
    for c in STATE_CANDIDATES:
        if c in pc_gdf.columns:
            state_col = c
            break

    pc_gdf = pc_gdf.rename(columns={pc_name_col: 'PC_NAME'})
    if state_col and state_col != 'PC_NAME':
        pc_gdf = pc_gdf.rename(columns={state_col: 'PC_STATE'})
    pc_gdf['PC_NAME'] = pc_gdf['PC_NAME'].astype(str).str.strip()

    # ── 3. Spatial join ──────────────────────────────────────────────────
    units_gdf = gpd.GeoDataFrame(
        units_df,
        geometry=gpd.points_from_xy(units_df['lon'], units_df['lat']),
        crs='EPSG:4326'
    )

    keep_cols = ['PC_NAME'] + (['PC_STATE'] if 'PC_STATE' in pc_gdf.columns else [])
    joined = gpd.sjoin(
        units_gdf,
        pc_gdf[keep_cols + ['geometry']],
        how='left',
        predicate='within'
    )
    joined = joined.drop(columns=['geometry', 'index_right'], errors='ignore')

    # ── 4. Election results ──────────────────────────────────────────────
    elec_path = os.path.join(BASE_DIR, 'Lok_Sabha_Elections_Winners_2024.xlsx')
    elec_df = pd.read_excel(elec_path)
    elec_df.columns = [c.strip() for c in elec_df.columns]
    elec_df = elec_df.rename(columns={
        'PC Name':              'PC_NAME',
        'Winning Candidate':    'winner',
        'Winning Party':        'party',
        'Runner-up Canddiate':  'runner_up',
        'Runner-up Party':      'runner_party',
        'Margin Votes':         'margin',
        'State':                'elec_state',
    })
    elec_df['PC_NAME_norm'] = elec_df['PC_NAME'].str.strip().str.upper()
    elec_df['margin'] = pd.to_numeric(elec_df['margin'], errors='coerce').fillna(0).astype(int)

    # Normalise PC_NAME in joined for merge
    joined['PC_NAME_norm'] = joined['PC_NAME'].str.strip().str.upper()

    # Merge election data onto units
    final = joined.merge(
        elec_df[['PC_NAME_norm', 'PC_NAME', 'winner', 'party', 'runner_up', 'runner_party', 'margin', 'elec_state']],
        on='PC_NAME_norm',
        how='left',
        suffixes=('', '_elec')
    )
    # Clean up duplicate PC_NAME columns
    if 'PC_NAME_elec' in final.columns:
        final['PC_NAME'] = final['PC_NAME'].fillna(final['PC_NAME_elec'])
        final = final.drop(columns=['PC_NAME_elec'])
    final = final.drop(columns=['PC_NAME_norm'], errors='ignore')

    # ── 5. PC-level summary ──────────────────────────────────────────────
    pc_summary = (
        final.groupby('PC_NAME', dropna=False)
        .agg(
            total_units   =('unit_name',  'count'),
            total_employees=('employees', 'sum'),
            state         =('state',      lambda x: x.mode()[0] if len(x) > 0 else ''),
            winner        =('winner',     'first'),
            party         =('party',      'first'),
            margin        =('margin',     'first'),
            runner_up     =('runner_up',  'first'),
            runner_party  =('runner_party','first'),
        )
        .reset_index()
    )

    # Top sector per PC
    sector_counts = (
        final.groupby(['PC_NAME', 'sector'])
        .size()
        .reset_index(name='cnt')
    )
    top_sector = (
        sector_counts.loc[sector_counts.groupby('PC_NAME')['cnt'].idxmax()]
        .rename(columns={'sector': 'top_sector', 'cnt': 'top_sector_cnt'})
    )
    pc_summary = pc_summary.merge(top_sector[['PC_NAME', 'top_sector', 'top_sector_cnt']], on='PC_NAME', how='left')

    return final, pc_summary, elec_df


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 16px 8px">
      <div style="font-size:15px;font-weight:800;color:#1D4ED8">🏭 PC Industrial</div>
      <div style="font-size:10px;color:#64748B;margin-top:2px">Unit × Constituency Analysis</div>
    </div>
    <div style="height:1px;background:#E8ECF0;margin:8px 0 12px"></div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading & running spatial join…"):
        final, pc_summary, elec_df = load_data(version=1)

    st.markdown('<p style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;padding:0 16px;margin-bottom:8px">Filters</p>', unsafe_allow_html=True)

    states = ['All States'] + sorted(final['state'].dropna().unique().tolist())
    sel_state = st.selectbox("State", states)

    sectors = ['All Sectors'] + sorted(final['sector'].dropna().unique().tolist())
    sel_sector = st.selectbox("Industry Sector", sectors)

    parties = ['All Parties'] + sorted(elec_df['party'].dropna().unique().tolist())
    sel_party = st.selectbox("Winning Party", parties)

    emp_min, emp_max = int(final['employees'].min()), int(final['employees'].max())
    sel_emp = st.slider("Min Employees per Unit", 0, min(emp_max, 5000), 0, step=50)

    margin_opt = st.radio("Seat Type", ['All Seats', 'Competitive (<50k margin)', 'Safe (≥50k margin)'])

    st.markdown('<div style="height:1px;background:#E8ECF0;margin:12px 0"></div>', unsafe_allow_html=True)
    map_mode = st.radio("Map Colour By", ['Winning Party', 'Industry Sector', 'Employee Count'])

    st.markdown("""
    <div style="margin:12px 16px 0;padding:10px 12px;background:#FFF7ED;border:1px solid #FED7AA;
    border-radius:8px;font-size:10px;color:#92400E;line-height:1.5">
    ⚠️ Election data covers <b>NDA seats (293)</b>. Opposition-won PCs show grey dots.
    </div>""", unsafe_allow_html=True)


# ── Filter units ─────────────────────────────────────────────────────────────
filt = final.copy()
if sel_state   != 'All States':  filt = filt[filt['state']    == sel_state]
if sel_sector  != 'All Sectors': filt = filt[filt['sector']   == sel_sector]
if sel_party   != 'All Parties': filt = filt[filt['party'].fillna('') == sel_party]
if sel_emp     >  0:             filt = filt[filt['employees'] >= sel_emp]
if margin_opt  == 'Competitive (<50k margin)':
    filt = filt[filt['margin'].fillna(999999) < 50000]
elif margin_opt == 'Safe (≥50k margin)':
    filt = filt[filt['margin'].fillna(0) >= 50000]

# Filter PC summary to match
pc_filt = pc_summary[pc_summary['PC_NAME'].isin(filt['PC_NAME'].dropna().unique())]

# ── KPIs ─────────────────────────────────────────────────────────────────────
total_units      = len(filt)
total_employees  = int(filt['employees'].sum())
pcs_covered      = filt['PC_NAME'].nunique()
dominant_party   = (filt['party'].value_counts().index[0]
                    if filt['party'].notna().any() else '—')
competitive_pcs  = int((pc_filt['margin'] < 50000).sum()) if len(pc_filt) else 0
top_pc_row       = pc_filt.loc[pc_filt['total_units'].idxmax()] if len(pc_filt) else None
top_pc_name      = top_pc_row['PC_NAME'] if top_pc_row is not None else '—'
top_pc_units     = int(top_pc_row['total_units']) if top_pc_row is not None else 0

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div class="page-title">🏭 Parliamentary Constituency — Industrial Unit Analysis</div>
  <div style="font-size:12px;color:#64748B;font-weight:500">Lok Sabha 2024 · Spatial Join</div>
</div>
<div style="height:14px"></div>""", unsafe_allow_html=True)

# ── KPI cards ─────────────────────────────────────────────────────────────────
def kpi(col, cls, icon, label, value, sub, sub_cls='up'):
    with col:
        st.markdown(f"""
        <div class="stat-card {cls}">
          <div class="stat-label">{label}</div>
          <div>
            <div class="stat-value">{value}</div>
            <div class="stat-sub {sub_cls}">{sub}</div>
          </div>
          <div class="stat-icon">{icon}</div>
        </div>""", unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
kpi(c1,'blue',  '🏭','Total Industrial Units',     f'{total_units:,}',    'Units in filtered view')
kpi(c2,'green', '👷','Total Employees',            f'{total_employees:,}','Across all matched units')
kpi(c3,'orange','🗺️','PCs Covered',               f'{pcs_covered}',      'Constituencies with ≥1 unit')
kpi(c4,'purple','⚔️','Competitive PCs',           f'{competitive_pcs}',  'Margin < 50,000 votes','warn')
kpi(c5,'red',   '🏆','Top PC by Units',           f'{top_pc_units:,}',   f'{top_pc_name[:24]}','danger')

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── COLOUR helpers ────────────────────────────────────────────────────────────
SECTOR_COLORS = {
    'Food Products':'#F97316','Textiles & Apparel':'#EC4899',
    'Wood & Paper':'#84CC16','Chemicals & Pharma':'#06B6D4',
    'Rubber, Plastic & Non-Metallic':'#8B5CF6',
    'Fabricated Metal Products':'#F59E0B',
    'Electronics & Machinery':'#3B82F6',
    'Machinery & Equipment':'#14B8A6',
    'Transport Equipment':'#E11D48',
    'Other Manufacturing':'#64748B',
    'Electricity & Utilities':'#FBBF24',
    'Construction':'#A16207','Other':'#94A3B8',
}

def unit_color(row):
    if map_mode == 'Winning Party':
        return get_party_color(row.get('party'))
    elif map_mode == 'Industry Sector':
        return SECTOR_COLORS.get(row.get('sector','Other'), '#94A3B8')
    else:
        emp = row.get('employees', 0)
        if emp >= 1000: return '#EF4444'
        if emp >= 200:  return '#F59E0B'
        if emp >= 50:   return '#22C55E'
        return '#3B82F6'

def unit_radius(emp):
    return max(3, min(14, math.sqrt(max(emp, 1)) * 0.6))


# ── Main layout ───────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    # ── MAP ──────────────────────────────────────────────────────────────
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="font-size:14px;font-weight:700;color:#1E293B">🗺️ Industrial Units inside Parliamentary Constituencies</div>
    </div>""", unsafe_allow_html=True)

    map_lat = filt['lat'].mean() if len(filt) else 22.5
    map_lon = filt['lon'].mean() if len(filt) else 80.0
    zoom    = 5 if sel_state == 'All States' else 7

    m = folium.Map(location=[map_lat, map_lon], zoom_start=zoom,
                   tiles=None, prefer_canvas=True)
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap © CartoDB', max_zoom=19
    ).add_to(m)

    # Plot each unit (cap at 5000 dots for performance)
    sample = filt.sample(min(len(filt), 5000), random_state=42) if len(filt) > 5000 else filt

    for _, row in sample.iterrows():
        color  = unit_color(row)
        radius = unit_radius(row['employees'])
        is_nda = pd.notna(row.get('party'))

        pc_block = ''
        if is_nda:
            pc_c = get_party_color(row.get('party'))
            pc_block = (
                f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #E2E8F0">'
                f'<div style="font-size:9px;font-weight:700;color:#64748B;text-transform:uppercase">PC</div>'
                f'<div style="font-weight:700;color:#059669;font-size:12px">{str(row.get("PC_NAME",""))}</div>'
                f'<div style="font-size:11px;font-weight:600;color:{pc_c}">{str(row.get("party",""))}</div>'
                f'<div style="font-size:10px;color:#1E293B">🏆 {str(row.get("winner",""))}</div>'
                f'<div style="font-size:10px;color:#64748B">Margin: {int(row.get("margin",0)):,}</div>'
                f'</div>'
            )

        popup_html = (
            f'<div style="font-family:Inter,sans-serif;min-width:220px;padding:4px">'
            f'<div style="font-size:14px;font-weight:700;color:#1E293B">{str(row.get("unit_name",""))}</div>'
            f'<div style="font-size:11px;color:#64748B;margin-bottom:4px">{str(row.get("address",""))}</div>'
            f'<table style="width:100%;border-collapse:collapse">'
            f'<tr><td style="font-size:11px;color:#64748B">District</td>'
            f'<td style="font-size:11px;font-weight:600;color:#1E293B;text-align:right">{str(row.get("district",""))}</td></tr>'
            f'<tr><td style="font-size:11px;color:#64748B">Sector</td>'
            f'<td style="font-size:11px;font-weight:600;color:#1E293B;text-align:right">{str(row.get("sector",""))}</td></tr>'
            f'<tr><td style="font-size:11px;color:#64748B">Employees</td>'
            f'<td style="font-size:11px;font-weight:600;color:#1D4ED8;text-align:right">{int(row.get("employees",0)):,}</td></tr>'
            f'</table>'
            f'{pc_block}'
            f'</div>'
        )

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius, color='#1E293B' if is_nda else '#94A3B8',
            weight=1.0, fill=True, fill_color=color, fill_opacity=0.80,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f'<b>{str(row.get("unit_name",""))[:30]}</b> · {int(row.get("employees",0)):,} emp'
        ).add_to(m)

    if len(filt) > 5000:
        st.caption(f"⚡ Showing 5,000 of {len(filt):,} units for performance. Apply filters to see all.")

    map_data = st_folium(m, width=None, height=500, returned_objects=["last_object_clicked"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ── LEGEND ────────────────────────────────────────────────────────────
    st.markdown('<div style="background:#FFFFFF;border:1px solid #E8ECF0;border-radius:8px;padding:12px 14px;margin-top:8px">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">{map_mode}</div>', unsafe_allow_html=True)

    if map_mode == 'Winning Party':
        active_parties = filt['party'].dropna().value_counts().head(10).index.tolist()
        cols_leg = st.columns(min(5, len(active_parties)))
        for i, p in enumerate(active_parties):
            c = get_party_color(p)
            with cols_leg[i % 5]:
                st.markdown(f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px"><div style="width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0"></div><span style="font-size:11px;color:#374151;font-weight:600">{get_party_abbr(p)}</span></div>', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:6px;margin-top:4px"><div style="width:10px;height:10px;border-radius:50%;background:#94A3B8"></div><span style="font-size:11px;color:#94A3B8">Opposition / No data</span></div>', unsafe_allow_html=True)

    elif map_mode == 'Industry Sector':
        active_sectors = filt['sector'].value_counts().head(8).index.tolist()
        cols_leg = st.columns(min(4, len(active_sectors)))
        for i, s in enumerate(active_sectors):
            c = SECTOR_COLORS.get(s, '#94A3B8')
            with cols_leg[i % 4]:
                st.markdown(f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px"><div style="width:10px;height:10px;border-radius:50%;background:{c}"></div><span style="font-size:10px;color:#374151">{s[:22]}</span></div>', unsafe_allow_html=True)

    else:
        for color, label in [('#EF4444','1000+ employees'),('#F59E0B','200–999'),('#22C55E','50–199'),('#3B82F6','<50')]:
            st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px"><div style="width:10px;height:10px;border-radius:50%;background:{color}"></div><span style="font-size:11px;color:#374151">{label}</span></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── PC GRID — top PCs by unit count ──────────────────────────────────
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">'
        '<div style="font-size:14px;font-weight:700;color:#1E293B">📋 Top Constituencies by Industrial Units</div>'
        '<div style="font-size:11px;color:#94A3B8">Top 18 PCs</div>'
        '</div>', unsafe_allow_html=True
    )
    top18_pc = pc_filt.sort_values('total_units', ascending=False).head(18).reset_index(drop=True)
    for row_start in range(0, len(top18_pc), 3):
        chunk = top18_pc.iloc[row_start:row_start+3]
        cols  = st.columns(3)
        for ci, (_, row) in enumerate(chunk.iterrows()):
            pc_c  = get_party_color(row.get('party'))
            abbr  = get_party_abbr(row.get('party'))
            has_p = pd.notna(row.get('party'))
            bg    = '#F0FDF4' if has_p else '#FFFFFF'
            bdr   = '#22C55E' if has_p else '#E8ECF0'
            party_tag = (
                f'<span style="font-size:9px;font-weight:700;color:{pc_c};background:{pc_c}22;'
                f'padding:2px 7px;border-radius:10px">{abbr}</span>'
            ) if has_p else ''
            with cols[ci]:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {bdr};border-left:3px solid {bdr};'
                    f'border-radius:10px;padding:11px 13px;margin-bottom:8px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                    f'<div style="flex:1;min-width:0">'
                    f'<div style="font-weight:700;font-size:12px;color:#1E293B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{str(row["PC_NAME"])}</div>'
                    f'<div style="color:#64748B;font-size:10px">{str(row.get("state",""))}</div>'
                    f'</div>'
                    f'<div style="text-align:right;margin-left:8px">'
                    f'<div style="color:#1D4ED8;font-weight:800;font-size:15px;font-family:JetBrains Mono,monospace">{int(row["total_units"]):,}</div>'
                    f'<div style="color:#94A3B8;font-size:9px">units</div>'
                    f'</div></div>'
                    f'<div style="margin-top:6px;padding-top:6px;border-top:1px solid #F1F5F9;'
                    f'display:flex;align-items:center;justify-content:space-between;gap:6px">'
                    f'<div style="color:#94A3B8;font-size:10px;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'
                    f'{str(row.get("top_sector",""))}</div>'
                    f'{party_tag}'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
    st.markdown('</div>', unsafe_allow_html=True)


with right:
    # ── Party dominance table ─────────────────────────────────────────────
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🗳️ Party — Industrial Dominance</div>', unsafe_allow_html=True)

    party_grp = (
        pc_filt[pc_filt['party'].notna()]
        .groupby('party')
        .agg(pcs=('PC_NAME','count'), units=('total_units','sum'), emp=('total_employees','sum'))
        .reset_index()
        .sort_values('units', ascending=False)
    )
    total_u = party_grp['units'].sum() or 1
    for _, pr in party_grp.head(10).iterrows():
        c   = get_party_color(pr['party'])
        pct = pr['units'] / total_u
        st.markdown(
            f'<div style="margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;align-items:center">'
            f'<span style="color:{c};font-weight:700">{get_party_abbr(pr["party"])}</span>'
            f'<span style="font-size:10px;color:#64748B">{str(pr["party"])[:18]}</span>'
            f'<span style="color:#1D4ED8;font-family:JetBrains Mono,monospace;font-size:11px">{int(pr["units"]):,}</span>'
            f'</div>'
            f'<div style="background:#F1F5F9;border-radius:3px;height:6px">'
            f'<div style="background:{c};width:{int(pct*100)}%;height:6px;border-radius:3px"></div>'
            f'</div>'
            f'<div style="color:#94A3B8;font-size:10px;margin-top:2px">'
            f'{int(pr["pcs"])} PCs · {int(pr["emp"]):,} employees</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Dormant / Vulnerable analysis ─────────────────────────────────────
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">⚔️ Dormant Political Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:11px;color:#64748B;margin-bottom:12px">PCs with high industrial weight but thin winning margins — politically vulnerable seats</div>', unsafe_allow_html=True)

    dormant = (
        pc_filt[pc_filt['margin'].notna() & pc_filt['party'].notna()]
        .copy()
    )
    dormant['vulnerability'] = dormant['total_units'] / (dormant['margin'].replace(0, 1))
    dormant = dormant.sort_values('vulnerability', ascending=False).head(8)

    for _, row in dormant.iterrows():
        pc_c = get_party_color(row.get('party'))
        margin_val = int(row.get('margin', 0))
        units_val  = int(row.get('total_units', 0))
        vuln_score = round(float(row.get('vulnerability', 0)), 1)
        bar_pct = min(100, int(min(margin_val, 100000) / 1000))
        margin_color = '#EF4444' if margin_val < 20000 else '#F59E0B' if margin_val < 50000 else '#22C55E'
        st.markdown(
            f'<div style="margin-bottom:10px;padding:9px 11px;background:#FAFAFA;border-radius:8px;border-left:3px solid {pc_c}">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="font-size:12px;font-weight:600;color:#1E293B">{str(row["PC_NAME"])}</div>'
            f'<span style="font-size:9px;font-weight:700;color:{pc_c};background:{pc_c}22;padding:2px 6px;border-radius:8px">{get_party_abbr(row.get("party"))}</span>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;font-size:10px;color:#64748B;margin-top:3px">'
            f'<span>🏭 {units_val:,} units</span>'
            f'<span style="color:{margin_color};font-weight:600">Margin: {margin_val:,}</span>'
            f'</div>'
            f'<div style="margin-top:5px;background:#F1F5F9;border-radius:3px;height:4px">'
            f'<div style="background:{margin_color};width:{bar_pct}%;height:4px;border-radius:3px"></div>'
            f'</div>'
            f'<div style="font-size:9px;color:#94A3B8;margin-top:2px">Vulnerability score: {vuln_score}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Clicked unit detail ───────────────────────────────────────────────
    if map_data and map_data.get('last_object_clicked'):
        clicked = map_data['last_object_clicked']
        clat2, clon2 = clicked.get('lat'), clicked.get('lng')
        if clat2 and clon2:
            dists = filt.apply(lambda r: math.sqrt((r['lat']-clat2)**2 + (r['lon']-clon2)**2), axis=1)
            sel   = filt.loc[dists.idxmin()]
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            pc_c = get_party_color(sel.get('party'))
            st.markdown(
                f'<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:12px;margin-bottom:10px">'
                f'<div style="font-size:14px;font-weight:700;color:#1E293B">{str(sel.get("unit_name",""))}</div>'
                f'<div style="font-size:11px;color:#64748B">{str(sel.get("district",""))} · {str(sel.get("state",""))}</div>'
                f'<div style="font-size:11px;color:#64748B;margin-top:2px">{str(sel.get("address",""))}</div>'
                f'<div style="display:flex;gap:16px;margin-top:8px">'
                f'<div><div style="font-size:20px;font-weight:800;color:#1D4ED8;font-family:JetBrains Mono,monospace">{int(sel.get("employees",0)):,}</div>'
                f'<div style="font-size:9px;color:#94A3B8;text-transform:uppercase">Employees</div></div>'
                f'<div><div style="font-size:13px;font-weight:700;color:#059669;margin-top:4px">{str(sel.get("sector",""))}</div>'
                f'<div style="font-size:9px;color:#94A3B8;text-transform:uppercase">Sector</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            if pd.notna(sel.get('party')):
                st.markdown(
                    f'<div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:12px">'
                    f'<div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;margin-bottom:6px">🗳 PC Details</div>'
                    f'<div style="font-weight:700;color:#15803D">{str(sel.get("PC_NAME",""))}</div>'
                    f'<div style="font-size:11px;font-weight:600;color:{pc_c};margin-top:4px">{str(sel.get("party",""))}</div>'
                    f'<div style="font-size:11px;color:#1E293B;margin-top:2px">🏆 {str(sel.get("winner",""))}</div>'
                    f'<div style="font-size:10px;color:#64748B;margin-top:2px">Margin: {int(sel.get("margin",0)):,} votes</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)


# ── Bottom tabs ───────────────────────────────────────────────────────────────
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Units Data Table",
    "🗳️ PC × Party Deep Dive",
    "🏭 Sector Analysis",
    "⚔️ Dormant Seat Report"
])

# ── Tab 1: raw data ───────────────────────────────────────────────────────────
with tab1:
    show_cols = ['state','district','unit_name','sector','employees','lat','lon','PC_NAME','party','winner','margin']
    show_cols = [c for c in show_cols if c in filt.columns]
    disp = filt[show_cols].sort_values('employees', ascending=False)
    disp.columns = [c.replace('_',' ').title() for c in disp.columns]
    c_dl, c_info = st.columns([3,1])
    with c_info:
        st.metric("Rows shown", f"{len(disp):,}")
    with c_dl:
        st.download_button("⬇️ Download CSV", disp.to_csv(index=False),
                           "pc_industrial_units.csv", "text/csv")
    st.dataframe(disp, use_container_width=True, height=360)

# ── Tab 2: PC × Party deep dive ───────────────────────────────────────────────
with tab2:
    st.markdown("### 🗳️ PC × Party Industrial Deep Dive")
    pp1, pp2 = st.columns(2)

    with pp1:
        st.markdown("**Party-wise PC Count vs Unit Count**")
        party_data = (
            pc_filt[pc_filt['party'].notna()]
            .groupby('party')
            .agg(pcs=('PC_NAME','count'), units=('total_units','sum'))
            .reset_index().sort_values('units', ascending=False).head(12)
        )
        fig = px.bar(
            party_data, x='party', y='units',
            color='party',
            color_discrete_map={p: get_party_color(p) for p in party_data['party']},
            labels={'units':'Industrial Units','party':'Party'},
            title='Industrial Units by Winning Party'
        )
        fig.update_layout(showlegend=False, height=360, plot_bgcolor='white',
                          xaxis_tickangle=-30, font_family='Inter')
        st.plotly_chart(fig, use_container_width=True)

    with pp2:
        st.markdown("**Top 15 PCs — Units vs Margin (Bubble = Employees)**")
        bubble_data = pc_filt[pc_filt['party'].notna() & pc_filt['margin'].notna()].head(50)
        fig2 = px.scatter(
            bubble_data, x='margin', y='total_units',
            color='party', size='total_employees',
            hover_name='PC_NAME',
            color_discrete_map={p: get_party_color(p) for p in bubble_data['party'].unique()},
            labels={'margin':'Winning Margin','total_units':'Industrial Units','total_employees':'Employees'},
            title='Units vs Margin (size = employees)'
        )
        fig2.update_layout(showlegend=False, height=360, plot_bgcolor='white', font_family='Inter')
        fig2.add_vline(x=50000, line_dash='dash', line_color='red',
                       annotation_text='50k margin', annotation_position='top right')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**All PCs with Election Data**")
    pc_show = pc_filt[['PC_NAME','state','party','winner','margin','total_units','total_employees','top_sector']].copy()
    pc_show.columns = ['PC Name','State','Party','Winner','Margin','Units','Employees','Top Sector']
    pc_show = pc_show.sort_values('Units', ascending=False)
    st.dataframe(pc_show, use_container_width=True, height=320)

# ── Tab 3: Sector analysis ────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🏭 Industry Sector Analysis")
    s1, s2 = st.columns(2)

    with s1:
        sec_counts = filt['sector'].value_counts().reset_index()
        sec_counts.columns = ['Sector','Units']
        fig3 = px.pie(sec_counts, names='Sector', values='Units',
                      color='Sector',
                      color_discrete_map=SECTOR_COLORS,
                      title='Unit Distribution by Sector')
        fig3.update_layout(height=360, font_family='Inter')
        st.plotly_chart(fig3, use_container_width=True)

    with s2:
        emp_by_sector = filt.groupby('sector')['employees'].sum().reset_index()
        emp_by_sector.columns = ['Sector','Employees']
        emp_by_sector = emp_by_sector.sort_values('Employees', ascending=True)
        fig4 = px.bar(emp_by_sector, y='Sector', x='Employees',
                      orientation='h',
                      color='Sector', color_discrete_map=SECTOR_COLORS,
                      title='Total Employees by Sector')
        fig4.update_layout(showlegend=False, height=360, plot_bgcolor='white', font_family='Inter')
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("**Sector Distribution across Top Parties**")
    sec_party = filt[filt['party'].notna()].groupby(['party','sector']).size().reset_index(name='units')
    top_parties_list = filt['party'].value_counts().head(6).index.tolist()
    sec_party = sec_party[sec_party['party'].isin(top_parties_list)]
    fig5 = px.bar(sec_party, x='party', y='units', color='sector',
                  color_discrete_map=SECTOR_COLORS,
                  labels={'units':'Units','party':'Party','sector':'Sector'},
                  title='Sector Breakdown per Party')
    fig5.update_layout(height=380, plot_bgcolor='white', font_family='Inter')
    st.plotly_chart(fig5, use_container_width=True)

# ── Tab 4: Dormant seat report ────────────────────────────────────────────────
with tab4:
    st.markdown("### ⚔️ Dormant Political Seat Report")
    st.markdown("""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:12px;margin-bottom:16px;font-size:13px;color:#92400E">
    <b>What is a "Dormant" or Vulnerable Seat?</b><br>
    A seat where industrial units are concentrated (high economic activity) but the winning margin was thin.
    These are politically sensitive constituencies — a party that lost here is likely to campaign hard on
    industrial/employment issues to flip it next election. The <b>Vulnerability Score = Units ÷ Margin</b>.
    A higher score means more industrial weight relative to the winning margin.
    </div>""", unsafe_allow_html=True)

    dormant_full = pc_filt[pc_filt['margin'].notna() & pc_filt['party'].notna()].copy()
    dormant_full['vulnerability_score'] = (dormant_full['total_units'] / dormant_full['margin'].replace(0,1)).round(2)
    dormant_full = dormant_full.sort_values('vulnerability_score', ascending=False)

    d1, d2 = st.columns(2)
    with d1:
        fig6 = px.scatter(
            dormant_full.head(60), x='margin', y='total_units',
            color='party', size='vulnerability_score',
            hover_name='PC_NAME',
            color_discrete_map={p: get_party_color(p) for p in dormant_full['party'].unique()},
            labels={'margin':'Winning Margin','total_units':'Industrial Units'},
            title='Vulnerability Map — Units vs Margin'
        )
        fig6.add_vline(x=50000, line_dash='dash', line_color='#EF4444',
                       annotation_text='Competitive threshold')
        fig6.update_layout(showlegend=False, height=380, plot_bgcolor='white', font_family='Inter')
        st.plotly_chart(fig6, use_container_width=True)

    with d2:
        top_vuln = dormant_full.head(15)[['PC_NAME','state','party','total_units','total_employees','margin','vulnerability_score']]
        top_vuln.columns = ['PC Name','State','Party','Units','Employees','Margin','Vuln. Score']
        st.markdown("**Top 15 Most Vulnerable Industrial PCs**")
        st.dataframe(top_vuln, use_container_width=True, height=380)

    st.markdown("---")
    st.download_button(
        "⬇️ Download Full Dormant Seat Report",
        dormant_full.to_csv(index=False),
        "dormant_seat_report.csv", "text/csv"
    )

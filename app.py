import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

st.set_page_config(
    page_title="Lok Sabha Industrial Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html,body,[class*="css"],.stApp {
    font-family: 'Sora', sans-serif !important;
    background: #0D0F14 !important;
    color: #E2E8F0 !important;
}
header[data-testid="stHeader"] { display:none!important; }
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"] { display:none!important; }
.block-container { padding-top:0!important; padding-bottom:1rem!important; max-width:100%!important; }

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #13161D !important;
    border-right: 1px solid #1E2433 !important;
    min-width:230px!important; max-width:230px!important;
}
section[data-testid="stSidebar"] * { color:#CBD5E1!important; }
section[data-testid="stSidebar"] [data-baseweb="select"]>div {
    background:#1A1F2E!important; border:1px solid #2D3748!important;
    border-radius:8px!important; color:#E2E8F0!important;
}
[data-baseweb="popover"] [role="listbox"], [data-baseweb="menu"] {
    background:#1A1F2E!important; border:1px solid #2D3748!important;
}
[data-baseweb="menu"] li,[data-baseweb="menu"] [role="option"] {
    color:#CBD5E1!important; background:#1A1F2E!important;
}
[data-baseweb="menu"] li:hover,[data-baseweb="menu"] [aria-selected="true"] {
    background:#252B3B!important; color:#60A5FA!important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] [data-testid="stRadio"] p { color:#CBD5E1!important; }
section[data-testid="stSidebar"] .stSlider * { color:#CBD5E1!important; }

/* TOP BAR */
.top-bar {
    background: linear-gradient(135deg,#0D1117 0%,#13161D 100%);
    border-bottom: 1px solid #1E2433;
    padding: 14px 28px;
    display: flex; align-items:center; justify-content:space-between;
    position:sticky; top:0; z-index:100;
    box-shadow: 0 2px 20px rgba(0,0,0,0.4);
}
.top-title {
    font-size:18px; font-weight:800; color:#F1F5F9;
    letter-spacing:-0.5px;
    background: linear-gradient(90deg,#60A5FA,#A78BFA);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.top-badge {
    font-size:10px; font-weight:600; color:#64748B;
    background:#1A1F2E; border:1px solid #2D3748;
    padding:4px 10px; border-radius:20px;
    font-family:'Space Mono',monospace;
}

/* STAT CARDS */
.stat-card {
    background: linear-gradient(135deg,#13161D,#1A1F2E);
    border:1px solid #1E2433; border-radius:14px;
    padding:16px 18px; position:relative; overflow:hidden;
    min-height:108px; display:flex; flex-direction:column; justify-content:space-between;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card::after {
    content:''; position:absolute; top:0; right:0;
    width:60px; height:60px; border-radius:0 14px 0 60px;
    opacity:0.06;
}
.stat-card.blue::after { background:#60A5FA; }
.stat-card.green::after { background:#34D399; }
.stat-card.orange::after { background:#FBBF24; }
.stat-card.purple::after { background:#A78BFA; }
.stat-card::before {
    content:''; position:absolute; bottom:0; left:0;
    width:100%; height:3px; border-radius:0 0 14px 14px;
}
.stat-card.blue::before { background: linear-gradient(90deg,#2563EB,#60A5FA); }
.stat-card.green::before { background: linear-gradient(90deg,#059669,#34D399); }
.stat-card.orange::before { background: linear-gradient(90deg,#D97706,#FBBF24); }
.stat-card.purple::before { background: linear-gradient(90deg,#7C3AED,#A78BFA); }

.stat-label {
    font-size:9px; font-weight:700; color:#475569;
    text-transform:uppercase; letter-spacing:1.2px;
}
.stat-value {
    font-size:26px; font-weight:800; color:#F1F5F9; line-height:1;
    font-family:'Space Mono',monospace;
}
.stat-sub { font-size:10px; font-weight:500; color:#64748B; margin-top:3px; }
.stat-icon { position:absolute; top:14px; right:14px; font-size:22px; opacity:0.2; }

/* PANELS */
.panel {
    background: #13161D; border:1px solid #1E2433; border-radius:14px;
    padding:18px; box-shadow:0 4px 24px rgba(0,0,0,0.3);
}
.panel-title { font-size:13px; font-weight:700; color:#CBD5E1; margin-bottom:14px; }

/* TABLE ROWS */
.tbl-row {
    display:flex; align-items:center; padding:9px 10px;
    border-bottom:1px solid #1E2433; gap:10px;
    border-radius:8px; margin-bottom:2px;
    transition: background 0.15s;
}
.tbl-row:hover { background:#1A1F2E; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background:#13161D!important; border-radius:10px!important;
    border:1px solid #1E2433!important; padding:4px!important;
}
.stTabs [role="tab"] { color:#64748B!important; font-weight:500!important; border-radius:7px!important; font-size:12px!important; }
.stTabs [role="tab"][aria-selected="true"] {
    background:#1A1F2E!important; color:#60A5FA!important; font-weight:700!important;
}

/* LEGEND */
.map-legend {
    background:#13161D; border:1px solid #1E2433; border-radius:10px;
    padding:12px 16px; margin-top:10px;
}
.legend-title { font-size:9px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px; }
.legend-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; font-size:11px; color:#94A3B8; font-weight:500; }
.legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }

/* PILL BADGES */
.party-pill {
    display:inline-block; padding:2px 9px; border-radius:20px;
    font-size:9px; font-weight:800; letter-spacing:.8px; text-transform:uppercase;
}

/* DATA TABLE */
[data-testid="stDataFrame"] { background:#13161D; border:1px solid #1E2433; border-radius:8px; }

/* DOWNLOAD BUTTON */
.stDownloadButton button {
    background:#1A1F2E!important; border:1px solid #2D3748!important;
    color:#60A5FA!important; font-size:12px!important; border-radius:8px!important;
}

h1,h2,h3,h4,h5,h6 { color:#E2E8F0!important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':                   '#F97316',
    'Indian National Congress':                 '#3B82F6',
    'Aam Aadmi Party':                          '#06B6D4',
    'Bahujan Samaj Party':                      '#1E40AF',
    'Samajwadi Party':                          '#E11D48',
    'All India Trinamool Congress':             '#16A34A',
    'Trinamool Congress':                       '#16A34A',
    'Dravida Munnetra Kazhagam':                '#9F1239',
    'Telugu Desam':                             '#CA8A04',
    'Telugu Desam Party':                       '#CA8A04',
    'Janata Dal  (United)':                     '#7C3AED',
    'Janata Dal (United)':                      '#7C3AED',
    'YSR Congress Party':                       '#0369A1',
    'Yuvajana Sramika Rythu Congress Party':    '#0369A1',
    'Biju Janata Dal':                          '#4ADE80',
    'Shiv Sena':                                '#D97706',
    'Shiv Sena (Uddhav Balasaheb Thackeray)':  '#F59E0B',
    'Rashtriya Lok Dal':                        '#84CC16',
    'Communist Party of India  (Marxist)':      '#DC2626',
    'Communist Party of India (Marxist)':       '#DC2626',
    'Communist Party of India':                 '#B91C1C',
    'Nationalist Congress Party':               '#0D9488',
    'Rashtriya Janata Dal':                     '#F43F5E',
    'Janasena Party':                           '#EC4899',
    'Lok Janshakti Party(Ram Vilas)':           '#14B8A6',
    'Lok Janshakti Party':                      '#14B8A6',
    'Apna Dal (Soneylal)':                      '#F472B6',
    'Asom Gana Parishad':                       '#10B981',
    'Hindustani Awam Morcha':                   '#6366F1',
    'Sikkim Krantikari Morcha':                 '#8B5CF6',
    'Independent':                              '#64748B',
    'Shiromani Akali Dal':                      '#B45309',
    'Azad Samaj Party (Kanshi Ram)':            '#0E7490',
    'Rashtriya Loktantrik Party':               '#7E22CE',
    'Bharat Adivasi Party':                     '#92400E',
    'Janata Dal (Secular)':                     '#A855F7',
    'Naga Peoples Front':                       '#0C4A6E',
    'Zoram People\'s Movement':                 '#0C4A6E',
    'Voice of the People Party':                '#78716C',
}
PARTY_ABBR = {
    'Bharatiya Janata Party':'BJP','Indian National Congress':'INC',
    'Aam Aadmi Party':'AAP','Samajwadi Party':'SP','Bahujan Samaj Party':'BSP',
    'All India Trinamool Congress':'TMC','Trinamool Congress':'TMC',
    'Dravida Munnetra Kazhagam':'DMK','Telugu Desam':'TDP','Telugu Desam Party':'TDP',
    'Janata Dal  (United)':'JD(U)','Janata Dal (United)':'JD(U)',
    'YSR Congress Party':'YSRCP','Yuvajana Sramika Rythu Congress Party':'YSRCP',
    'Biju Janata Dal':'BJD','Shiv Sena':'SS',
    'Shiv Sena (Uddhav Balasaheb Thackeray)':'SS(UBT)',
    'Rashtriya Lok Dal':'RLD','Communist Party of India  (Marxist)':'CPM',
    'Communist Party of India (Marxist)':'CPM','Communist Party of India':'CPI',
    'Nationalist Congress Party':'NCP','Rashtriya Janata Dal':'RJD',
    'Janasena Party':'JSP','Lok Janshakti Party(Ram Vilas)':'LJP',
    'Lok Janshakti Party':'LJP','Apna Dal (Soneylal)':'Apna',
    'Asom Gana Parishad':'AGP','Hindustani Awam Morcha':'HAM',
    'Sikkim Krantikari Morcha':'SKM','Independent':'IND',
    'Shiromani Akali Dal':'SAD','Azad Samaj Party (Kanshi Ram)':'ASPKR',
    'Rashtriya Loktantrik Party':'RLTP','Bharat Adivasi Party':'BAP',
    'Janata Dal (Secular)':'JD(S)',
}
_FALLBACK = ['#6366F1','#0891B2','#65A30D','#B45309','#BE185D','#0E7490',
             '#4338CA','#15803D','#C2410C','#7E22CE','#0F766E','#1D4ED8']

NIC3_MAP = {
    163:'Wood Products', 164:'Wood Products', 893:'Other Services',
    101:'Food Products',102:'Food Products',103:'Food Products',
    104:'Vegetable/Animal Oils',105:'Dairy Products',106:'Grain Mill Products',
    107:'Bakery Products',108:'Other Food',109:'Animal Feed',
    110:'Beverages',111:'Beverages',120:'Tobacco Products',
    131:'Spinning/Weaving',132:'Textile Finishing',133:'Textile Fabrics',
    139:'Other Textiles',141:'Wearing Apparel',142:'Apparel',143:'Knitted Fabrics',
    151:'Leather',152:'Footwear',161:'Wood Products',162:'Wood Products',
    170:'Paper',171:'Paper',172:'Printing',181:'Printing',182:'Publishing',
    191:'Coke/Petroleum',192:'Refined Petroleum',201:'Basic Chemicals',
    202:'Fertilizers/Pesticides',203:'Paints/Varnishes',204:'Soaps/Cosmetics',
    205:'Other Chemicals',206:'Agro Chemicals',209:'Other Chemicals',
    210:'Pharmaceuticals',211:'Pharmaceuticals',221:'Rubber Products',
    222:'Plastic Products',231:'Glass Products',239:'Non-Metallic Minerals',
    241:'Iron & Steel',242:'Non-Ferrous Metals',243:'Metal Casting',
    251:'Structural Metals',252:'Tanks/Containers',259:'Other Metal Products',
    261:'Electronic Components',262:'Computers/Peripherals',263:'Comm Equipment',
    264:'Consumer Electronics',265:'Instruments',266:'Medical Devices',
    267:'Optical Equipment',271:'Electrical Equipment',272:'Batteries',
    273:'Wiring/Cables',274:'Lighting',275:'Domestic Appliances',279:'Other Electrical',
    281:'General Machinery',282:'Special Purpose Machinery',289:'Other Machinery',
    291:'Motor Vehicles',292:'Bodies/Trailers',293:'Auto Parts',
    301:'Ships/Boats',302:'Railway Equipment',303:'Aircraft',309:'Other Transport',
    310:'Furniture',321:'Jewellery',322:'Musical Instruments',323:'Sports Goods',
    324:'Games/Toys',325:'Medical Devices',329:'Other Manufacturing',
    331:'Repair/Maintenance',332:'Installation',
}

IND_COLORS = ['#60A5FA','#34D399','#F87171','#FBBF24','#A78BFA','#F472B6',
              '#38BDF8','#FB923C','#818CF8','#D97706','#4ADE80','#EAB308',
              '#E879F9','#F43F5E','#2DD4BF','#84CC16','#0EA5E9','#C084FC']

def get_party_color(p):
    if p in PARTY_COLORS: return PARTY_COLORS[p]
    return _FALLBACK[abs(hash(p or '')) % len(_FALLBACK)]

def get_party_abbr(p): return PARTY_ABBR.get(p, p[:5] if p else '')

def get_dist_km(lat1,lon1,lat2,lon2):
    R=6371; dL=math.radians(lat2-lat1); dO=math.radians(lon2-lon1)
    a=math.sin(dL/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dO/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

# ── Load Data ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    path = os.path.join(BASE_DIR, 'units_enriched.csv')
    df = pd.read_csv(path, low_memory=False)

    # NIC 3-digit sector
    df['nic3'] = (df['nic_code'] // 10).astype(int)
    df['sector'] = df['nic3'].map(NIC3_MAP).fillna('Other Manufacturing')

    # Centroid per PC from actual unit lat/lons
    pc_geo = (df.dropna(subset=['ls_name','latitude','longitude'])
              .groupby('ls_name')
              .agg(lat=('latitude','mean'), lon=('longitude','mean'),
                   ls_state=('ls_state','first'),
                   winner_party=('winner_party','first'),
                   winner_name=('winner_name','first'))
              .reset_index())

    # Aggregate units per PC
    pc_units = (df.dropna(subset=['ls_name'])
                .groupby(['ls_name','ls_state','winner_party','winner_name'])
                ['unit_id'].count()
                .reset_index()
                .rename(columns={'unit_id':'total_units'}))

    # Aggregate units per PC per sector
    pc_sector = (df.dropna(subset=['ls_name'])
                 .groupby(['ls_name','sector'])['unit_id'].count()
                 .reset_index()
                 .rename(columns={'unit_id':'cnt'}))
    # Build sector dict per PC
    sector_dict = {}
    for _, row in pc_sector.iterrows():
        sector_dict.setdefault(row['ls_name'], {})[row['sector']] = int(row['cnt'])

    # Aggregate employees per PC
    pc_emp = (df.dropna(subset=['ls_name','employees'])
              .groupby('ls_name')['employees'].sum()
              .reset_index()
              .rename(columns={'employees':'total_employees'}))

    # Merge all
    main = pc_units.merge(pc_geo[['ls_name','lat','lon']], on='ls_name', how='left')
    main = main.merge(pc_emp, on='ls_name', how='left')
    main['sectors'] = main['ls_name'].map(sector_dict).fillna({}).apply(lambda x: x if isinstance(x,dict) else {})
    main['total_employees'] = main['total_employees'].fillna(0).astype(int)

    # Top sector per PC
    main['top_sector'] = main['sectors'].apply(
        lambda d: max(d, key=d.get) if d else 'Other Manufacturing'
    )

    # Election margin from original Lok Sabha file
    try:
        lok_path = os.path.join(BASE_DIR, 'Lok_Sabha_Elections_Winners_2024.xlsx')
        lok = pd.read_excel(lok_path)
        lok_margin = lok[['PC Name','Margin Votes']].copy()
        lok_margin.columns = ['ls_name','margin']
        lok_margin['margin'] = pd.to_numeric(lok_margin['margin'], errors='coerce').fillna(0).astype(int)
        # Try fuzzy match on name
        main = main.merge(lok_margin, on='ls_name', how='left')
        main['margin'] = main['margin'].fillna(0).astype(int)
    except:
        main['margin'] = 0

    # Runner-up party from Lok Sabha file
    try:
        lok2 = pd.read_excel(lok_path)
        lok2 = lok2[['PC Name','Runner-up Party']].copy()
        lok2.columns = ['ls_name','runner_party']
        main = main.merge(lok2, on='ls_name', how='left')
        main['runner_party'] = main['runner_party'].fillna('')
    except:
        main['runner_party'] = ''

    all_sectors = sorted(df['sector'].dropna().unique())
    all_states  = sorted(df['ls_state'].dropna().unique())
    all_parties = sorted(df['winner_party'].dropna().unique())
    
    ind_color_map = {s: IND_COLORS[i % len(IND_COLORS)] for i, s in enumerate(all_sectors)}

    # Overall stats
    stats = {
        'total_units': int(df['unit_id'].count()),
        'total_pcs': int(main['ls_name'].nunique()),
        'total_states': int(df['ls_state'].dropna().nunique()),
        'total_employees': int(df['employees'].dropna().sum()),
    }

    return main, all_sectors, all_states, all_parties, ind_color_map, stats

with st.spinner("Loading constituency data..."):
    df, all_sectors, all_states, all_parties, ind_color_map, stats = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 16px 10px">
      <div style="font-size:15px;font-weight:800;letter-spacing:-0.5px;
           background:linear-gradient(90deg,#60A5FA,#A78BFA);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        Lok Sabha Industrial Intelligence
      </div>
      <div style="font-size:10px;color:#475569;margin-top:3px;font-family:'Space Mono',monospace">
        Lok Sabha 2024 × Industrial Units
      </div>
    </div>
    <div style="height:1px;background:#1E2433;margin:8px 0 14px"></div>
    <p style="font-size:9px;font-weight:700;color:#475569;text-transform:uppercase;
       letter-spacing:1.2px;padding:0 16px;margin-bottom:10px">Filters</p>
    """, unsafe_allow_html=True)

    sel_state   = st.selectbox("State", ['All States'] + all_states, key="ss")
    sel_sector  = st.selectbox("Industry Sector", ['All Sectors'] + all_sectors, key="si")
    sel_party   = st.selectbox("Winning Party", ['All Parties'] + all_parties, key="sp")
    min_units   = st.slider("Min Units in PC", 0, 5000, 0, 100, key="mu")

    st.markdown('<div style="height:1px;background:#1E2433;margin:14px 0"></div>', unsafe_allow_html=True)
    view_mode = st.radio("Map Color Mode", ['Winning Party', 'Top Industry Sector', 'Units Count'], key="vm")

    st.markdown("""
    <div style="margin:14px 8px 0;padding:10px 12px;background:#1A1F2E;
    border:1px solid #2D3748;border-radius:8px;font-size:10px;color:#64748B;line-height:1.6">
    📍 <b style="color:#94A3B8">PC Assignment:</b> Each unit is spatially assigned to a Lok Sabha constituency using polygon boundaries — covering all 539 contested seats.
    </div>
    """, unsafe_allow_html=True)

# ── FILTER ─────────────────────────────────────────────────────────────────
filt = df.copy()
if sel_state  != 'All States':  filt = filt[filt['ls_state']  == sel_state]
if sel_party  != 'All Parties': filt = filt[filt['winner_party'] == sel_party]
if sel_sector != 'All Sectors':
    filt = filt[filt['sectors'].apply(lambda d: d.get(sel_sector, 0) > 0)]
filt = filt[filt['total_units'] >= min_units]
filt = filt.dropna(subset=['lat','lon']).reset_index(drop=True)

# ── KPIs ───────────────────────────────────────────────────────────────────
total_units_f    = int(filt['total_units'].sum())
total_pcs_f      = int(filt['ls_name'].nunique())
total_emp_f      = int(filt['total_employees'].sum())
competitive_f    = int((filt['margin'] < 50000).sum()) if 'margin' in filt.columns else 0
if len(filt):
    top_idx = filt['total_units'].idxmax()
    top_pc  = filt.loc[top_idx, 'ls_name']
    top_u   = int(filt.loc[top_idx, 'total_units'])
else:
    top_pc = '—'; top_u = 0

# ── TOP BAR ────────────────────────────────────────────────────────────────
from datetime import datetime
st.markdown(f"""
<div class="top-bar">
  <div class="top-title">🏛️ Parliamentary Industrial Intelligence</div>
  <div style="display:flex;align-items:center;gap:10px">
    <span class="top-badge">Lok Sabha 2024</span>
    <span class="top-badge">{len(filt)} constituencies</span>
    <span class="top-badge">Polygon-based matching ✓</span>
  </div>
</div>
<div style="height:18px"></div>
""", unsafe_allow_html=True)

# ── 4 STAT CARDS ───────────────────────────────────────────────────────────
c1,c2,c3,c4 = st.columns(4)
def stat_card(col,cls,icon,label,val,sub):
    with col:
        st.markdown(f"""
        <div class="stat-card {cls}">
          <div class="stat-label">{label}</div>
          <div>
            <div class="stat-value">{val}</div>
            <div class="stat-sub">{sub}</div>
          </div>
          <div class="stat-icon">{icon}</div>
        </div>""", unsafe_allow_html=True)

stat_card(c1,'blue','🗺️','Constituencies Matched', f'{total_pcs_f:,}', f'of {stats["total_pcs"]} total with unit data')
stat_card(c2,'green','🏭','Industrial Units', f'{total_units_f:,}', f'{stats["total_units"]:,} total in full dataset')
stat_card(c3,'orange','👷','Total Employees', f'{total_emp_f:,}', 'employed in filtered constituencies')
stat_card(c4,'purple','🏆','Largest Industrial PC', f'{top_u:,}', f'units · {top_pc[:22]}')

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ── MAP HELPERS ─────────────────────────────────────────────────────────────
def get_color(row):
    if view_mode == 'Winning Party':
        return get_party_color(row.get('winner_party',''))
    elif view_mode == 'Top Industry Sector':
        return ind_color_map.get(row.get('top_sector',''), '#6366F1')
    else:
        u = row['total_units']
        if u > 3000: return '#F87171'
        if u > 1000: return '#FBBF24'
        if u > 300:  return '#34D399'
        return '#60A5FA'

def get_radius(u): return max(5, min(32, math.sqrt(u + 1) * 1.05))

def build_legend():
    rows = ""
    if view_mode == 'Units Count':
        for c,l in [('#F87171','3000+ units'),('#FBBF24','1000–3000'),('#34D399','300–1000'),('#60A5FA','< 300')]:
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{c}"></div>{l}</div>'
    elif view_mode == 'Top Industry Sector':
        sc = {}
        for _, r in filt.iterrows():
            for k,v in r['sectors'].items(): sc[k] = sc.get(k,0)+v
        for k,_ in sorted(sc.items(), key=lambda x:-x[1])[:8]:
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{ind_color_map.get(k,"#6366F1")}"></div>{k[:28]}</div>'
    else:
        parties = filt['winner_party'].dropna().unique()
        for p in sorted(parties)[:12]:
            c = get_party_color(p)
            rows += f'<div class="legend-row"><div class="legend-dot" style="background:{c}"></div><b style="color:{c}">{get_party_abbr(p)}</b> — {p[:22]}</div>'
    return f'<div class="map-legend"><div class="legend-title">{view_mode}</div>{rows}<div style="margin-top:8px;padding-top:8px;border-top:1px solid #1E2433;font-size:10px;color:#334155">● Bubble size ∝ industrial unit count in constituency</div></div>'

# ── MAIN LAYOUT ─────────────────────────────────────────────────────────────
left_col, right_col = st.columns([2, 1])

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="font-size:13px;font-weight:700;color:#CBD5E1">🗺️ Constituency Industrial Map</div>
      <div style="font-size:10px;color:#475569">Polygon-assigned units — all 543 Lok Sabha seats</div>
    </div>""", unsafe_allow_html=True)

    clat = filt['lat'].mean() if len(filt) > 0 else 22.5
    clon = filt['lon'].mean() if len(filt) > 0 else 80.0
    zoom = 5 if sel_state == 'All States' else 7

    m = folium.Map(location=[clat,clon], zoom_start=zoom, tiles=None, prefer_canvas=True)
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='© OpenStreetMap © CartoDB', name='Dark', max_zoom=19
    ).add_to(m)

    for _, row in filt.iterrows():
        color   = get_color(row)
        radius  = get_radius(row['total_units'])
        party   = str(row.get('winner_party',''))
        pc_col  = get_party_color(party)
        abbr    = get_party_abbr(party)

        top_sectors = sorted(row['sectors'].items(), key=lambda x:-x[1])[:5]
        sec_rows = ""
        for s, cnt in top_sectors:
            c = ind_color_map.get(s,'#60A5FA')
            sec_rows += (f'<tr><td style="color:#94A3B8;font-size:10px;padding:2px 5px">{s[:28]}</td>'
                         f'<td style="color:{c};font-size:10px;font-weight:700;padding:2px 5px;text-align:right">{cnt:,}</td></tr>')

        margin_str = f"{row.get('margin',0):,}" if row.get('margin',0) else 'N/A'
        emp_str    = f"{row.get('total_employees',0):,}"

        popup_html = (
            f'<div style="font-family:Sora,sans-serif;min-width:220px;'
            f'background:#13161D;color:#E2E8F0;padding:6px;border-radius:8px">'
            f'<div style="font-size:14px;font-weight:800;color:#F1F5F9">{row["ls_name"]}</div>'
            f'<div style="font-size:11px;color:#64748B;margin-bottom:6px">{row["ls_state"]}</div>'
            f'<div style="display:flex;gap:10px;margin-bottom:8px">'
            f'<div><div style="font-size:20px;font-weight:800;color:#60A5FA;font-family:Space Mono,monospace">{row["total_units"]:,}</div>'
            f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px">Units</div></div>'
            f'<div><div style="font-size:20px;font-weight:800;color:#34D399;font-family:Space Mono,monospace">{emp_str}</div>'
            f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px">Employees</div></div>'
            f'</div>'
            f'<table style="width:100%;border-collapse:collapse;margin-bottom:8px">{sec_rows}</table>'
            f'<div style="border-top:1px solid #1E2433;padding-top:8px;margin-top:4px">'
            f'<div style="font-size:9px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px">Winner</div>'
            f'<div style="font-size:12px;font-weight:700;color:{pc_col};margin-top:2px">'
            f'<span style="background:{pc_col}22;padding:2px 8px;border-radius:4px">{abbr}</span> '
            f'{str(row.get("winner_name",""))}</div>'
            f'<div style="font-size:10px;color:#64748B;margin-top:2px">Margin: {margin_str} votes</div>'
            f'</div></div>'
        )

        folium.CircleMarker(
            location=[row['lat'], row['lon']], radius=radius,
            color=color, weight=1.5,
            fill=True, fill_color=color, fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f'<b>{row["ls_name"]}</b> · {row["total_units"]:,} units · {abbr}',
        ).add_to(m)

    map_data = st_folium(m, width=None, height=500, returned_objects=["last_object_clicked"])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(build_legend(), unsafe_allow_html=True)

    # Top constituencies grid
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">'
        '<div style="font-size:13px;font-weight:700;color:#CBD5E1">📋 Top Constituencies by Industrial Units</div>'
        '<div style="font-size:10px;color:#475569">Top 18 · sorted by unit count</div>'
        '</div>', unsafe_allow_html=True
    )

    top18 = filt.sort_values('total_units', ascending=False).head(18).reset_index(drop=True)
    for row_start in range(0, len(top18), 3):
        chunk = top18.iloc[row_start:row_start+3]
        cols  = st.columns(3)
        for col_idx, (_, row) in enumerate(chunk.iterrows()):
            party  = str(row.get('winner_party',''))
            pc_col = get_party_color(party)
            abbr   = get_party_abbr(party)
            top_s  = row.get('top_sector','—')
            short  = top_s[:20]+'…' if len(top_s)>20 else top_s
            emp    = int(row.get('total_employees',0))
            with cols[col_idx]:
                st.markdown(
                    f'<div style="background:#1A1F2E;border:1px solid #1E2433;'
                    f'border-left:3px solid {pc_col};border-radius:10px;'
                    f'padding:12px 14px;margin-bottom:8px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:flex-start">'
                    f'<div style="flex:1;min-width:0">'
                    f'<div style="font-weight:700;font-size:12px;color:#E2E8F0;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row["ls_name"]}</div>'
                    f'<div style="color:#475569;font-size:10px;margin-top:1px">{row["ls_state"]}</div>'
                    f'</div>'
                    f'<div style="text-align:right;flex-shrink:0;margin-left:8px">'
                    f'<div style="color:#60A5FA;font-weight:800;font-size:15px;'
                    f'font-family:Space Mono,monospace;line-height:1">{row["total_units"]:,}</div>'
                    f'<div style="color:#475569;font-size:9px">units</div>'
                    f'</div></div>'
                    f'<div style="margin-top:8px;padding-top:7px;border-top:1px solid #1E2433;'
                    f'display:flex;align-items:center;justify-content:space-between;gap:6px">'
                    f'<div style="color:#64748B;font-size:10px;flex:1;'
                    f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{short}</div>'
                    f'<span style="font-size:9px;font-weight:800;color:{pc_col};'
                    f'background:{pc_col}22;padding:2px 7px;border-radius:10px">{abbr}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
    st.markdown('</div>', unsafe_allow_html=True)

# ── RIGHT COLUMN ────────────────────────────────────────────────────────────
with right_col:
    # Party dominance panel
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🏆 Party Industrial Strength</div>', unsafe_allow_html=True)
    party_agg = (filt.groupby('winner_party')
                 .agg(pcs=('ls_name','count'), units=('total_units','sum'), emp=('total_employees','sum'))
                 .reset_index().sort_values('units', ascending=False))
    tot_u = party_agg['units'].sum() or 1
    for _, pr in party_agg.head(10).iterrows():
        c    = get_party_color(pr['winner_party'])
        pct  = pr['units'] / tot_u
        abbr = get_party_abbr(pr['winner_party'])
        st.markdown(
            f'<div style="margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;margin-bottom:3px">'
            f'<span style="color:{c};font-weight:800;background:{c}22;padding:1px 7px;border-radius:4px">{abbr}</span>'
            f'<span style="color:#475569;font-size:10px">{int(pr["pcs"])} seats</span>'
            f'<span style="color:#60A5FA;font-family:Space Mono,monospace;font-size:10px">{int(pr["units"]):,}</span>'
            f'</div>'
            f'<div style="background:#1E2433;border-radius:3px;height:6px">'
            f'<div style="background:{c};width:{int(pct*100)}%;height:6px;border-radius:3px"></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Clicked constituency detail
    sel_row = None
    if map_data and map_data.get('last_object_clicked'):
        clicked = map_data['last_object_clicked']
        clat2, clon2 = clicked.get('lat'), clicked.get('lng')
        if clat2 and clon2 and len(filt) > 0:
            dists = filt.apply(lambda r: get_dist_km(clat2,clon2,r['lat'],r['lon']), axis=1)
            sel_row = filt.loc[dists.idxmin()]

    if sel_row is not None:
        party  = str(sel_row.get('winner_party',''))
        pc_col = get_party_color(party)
        abbr   = get_party_abbr(party)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#1A1F2E;border:1px solid {pc_col}44;border-radius:10px;padding:14px;margin-bottom:12px">'
            f'<div style="font-size:16px;font-weight:800;color:#F1F5F9">{sel_row["ls_name"]}</div>'
            f'<div style="font-size:11px;color:#64748B">{sel_row["ls_state"]}</div>'
            f'<div style="display:flex;gap:16px;margin-top:10px">'
            f'<div><div style="font-size:24px;font-weight:800;color:#60A5FA;font-family:Space Mono,monospace">{sel_row["total_units"]:,}</div>'
            f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px">units</div></div>'
            f'<div><div style="font-size:24px;font-weight:800;color:#34D399;font-family:Space Mono,monospace">{int(sel_row.get("total_employees",0)):,}</div>'
            f'<div style="font-size:9px;color:#475569;text-transform:uppercase;letter-spacing:1px">employees</div></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        # Winner block
        margin = int(sel_row.get('margin',0))
        st.markdown(
            f'<div style="background:{pc_col}11;border:1px solid {pc_col}33;border-radius:8px;padding:12px;margin-bottom:10px">'
            f'<div style="font-size:9px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px">🗳 Election Result</div>'
            f'<div style="font-size:13px;font-weight:700;color:{pc_col}">'
            f'<span style="background:{pc_col}22;padding:2px 8px;border-radius:4px">{abbr}</span> '
            f'{str(sel_row.get("winner_name",""))}</div>'
            f'<div style="font-size:11px;color:#64748B;margin-top:3px">{party}</div>'
            f'<div style="font-size:10px;color:#64748B;margin-top:3px">Margin: <b style="color:#94A3B8">{margin:,}</b> votes</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        # Top sectors
        st.markdown('<div style="font-size:10px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid #1E2433">🏭 Top Industry Sectors</div>', unsafe_allow_html=True)
        top_secs = sorted(sel_row['sectors'].items(), key=lambda x:-x[1])[:8]
        mx = top_secs[0][1] if top_secs else 1
        for sname, cnt in top_secs:
            pct = cnt / mx
            c   = ind_color_map.get(sname,'#60A5FA')
            st.markdown(
                f'<div style="margin-bottom:6px">'
                f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">'
                f'<span style="color:#94A3B8">{sname[:26]}</span>'
                f'<span style="color:{c};font-family:Space Mono,monospace;font-weight:700">{cnt:,}</span>'
                f'</div>'
                f'<div style="background:#1E2433;border-radius:3px;height:4px">'
                f'<div style="background:{c};width:{int(pct*100)}%;height:4px;border-radius:3px"></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Top list when nothing clicked
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📍 Top Constituencies (click map for details)</div>', unsafe_allow_html=True)
        for _, r2 in filt.sort_values('total_units',ascending=False).head(10).iterrows():
            pc_col = get_party_color(str(r2.get('winner_party','')))
            abbr   = get_party_abbr(str(r2.get('winner_party','')))
            st.markdown(
                f'<div class="tbl-row">'
                f'<div style="flex:1;min-width:0">'
                f'<div style="font-size:12px;font-weight:600;color:#CBD5E1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{r2["ls_name"]}</div>'
                f'<div style="font-size:10px;font-weight:600;color:{pc_col}">{abbr} · {r2["ls_state"][:14]}</div>'
                f'</div>'
                f'<div style="text-align:right;font-size:13px;font-weight:700;font-family:Space Mono,monospace;color:#60A5FA">{r2["total_units"]:,}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# ── BOTTOM TABS ─────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Data Table", "🗳 Party Analysis", "🏭 Industry Breakdown"])

with tab1:
    dcols = ['ls_name','ls_state','total_units','total_employees','top_sector','winner_party','winner_name']
    if 'margin' in filt.columns: dcols.append('margin')
    disp = filt[dcols].copy()
    disp.columns = [c.replace('_',' ').title() for c in dcols]
    disp = disp.sort_values('Total Units', ascending=False)
    ca, cb = st.columns([3,1])
    with cb:
        st.download_button("⬇️ Download CSV", disp.to_csv(index=False), "pc_industrial_data.csv", "text/csv")
    st.dataframe(disp, use_container_width=True, height=340)

with tab2:
    st.markdown("### 🗳 Party-wise Industrial Analysis")
    if len(filt) and 'winner_party' in filt.columns:
        pa = (filt.groupby('winner_party')
              .agg(constituencies=('ls_name','count'),
                   total_units=('total_units','sum'),
                   total_employees=('total_employees','sum'),
                   avg_units=('total_units','mean'),
                   competitive=('margin', lambda x: (x < 50000).sum()))
              .reset_index().sort_values('total_units', ascending=False))
        pp1, pp2 = st.columns(2)
        with pp1:
            st.markdown("**Party-wise Industrial Strength**")
            tot2 = pa['total_units'].sum() or 1
            for _, pr in pa.iterrows():
                c    = get_party_color(pr['winner_party'])
                pct  = pr['total_units'] / tot2
                abbr = get_party_abbr(pr['winner_party'])
                st.markdown(
                    f'<div style="margin-bottom:12px">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:4px">'
                    f'<span style="color:{c};font-weight:800;background:{c}22;padding:1px 8px;border-radius:4px">{abbr}</span>'
                    f'<span style="font-size:10px;color:#64748B">{pr["winner_party"][:22]}</span>'
                    f'<span style="color:#60A5FA;font-family:Space Mono,monospace;font-size:11px">{int(pr["total_units"]):,}</span>'
                    f'</div>'
                    f'<div style="background:#1E2433;border-radius:4px;height:8px">'
                    f'<div style="background:{c};width:{int(pct*100)}%;height:8px;border-radius:4px"></div>'
                    f'</div>'
                    f'<div style="color:#475569;font-size:10px;margin-top:3px">'
                    f'{int(pr["constituencies"])} seats · avg {int(pr["avg_units"]):,}/seat · '
                    f'{int(pr["competitive"])} competitive</div>'
                    f'</div>', unsafe_allow_html=True)
        with pp2:
            st.markdown("**Top Constituencies by Party**")
            for _, pr in filt.sort_values('total_units', ascending=False).head(18).iterrows():
                c    = get_party_color(str(pr.get('winner_party','')))
                abbr = get_party_abbr(str(pr.get('winner_party','')))
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'margin-bottom:5px;padding:8px 12px;background:#1A1F2E;border-radius:8px;'
                    f'border-left:3px solid {c}">'
                    f'<div><div style="font-size:12px;font-weight:600;color:#CBD5E1">{pr["ls_name"]}</div>'
                    f'<div style="font-size:10px;color:{c};font-weight:600">{abbr} · {pr["ls_state"][:14]}</div></div>'
                    f'<div style="color:#60A5FA;font-weight:700;font-family:Space Mono,monospace;font-size:12px">'
                    f'{pr["total_units"]:,}</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        st.info("No data available for current filters.")

with tab3:
    st.markdown("### 🏭 Industry Sector Summary")
    # Aggregate across all filtered PCs
    ia = {}
    for _, row in filt.iterrows():
        for sec, cnt in row['sectors'].items():
            ia[sec] = ia.get(sec, 0) + cnt
    isr = sorted(ia.items(), key=lambda x:-x[1])
    ti  = sum(v for _,v in isr) or 1
    ci1, ci2 = st.columns(2)
    with ci1:
        st.markdown("**All Industry Sectors (Filtered)**")
        for sec, cnt in isr:
            pct = cnt / ti
            c   = ind_color_map.get(sec,'#60A5FA')
            st.markdown(
                f'<div style="margin-bottom:7px">'
                f'<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">'
                f'<span style="color:#94A3B8">{sec[:36]}</span>'
                f'<span style="color:{c};font-family:Space Mono,monospace;font-weight:700">{cnt:,}</span>'
                f'</div>'
                f'<div style="background:#1E2433;border-radius:3px;height:5px">'
                f'<div style="background:{c};width:{int(pct*100)}%;height:5px;border-radius:3px"></div>'
                f'</div>'
                f'<div style="color:#475569;font-size:10px;margin-top:1px">{pct*100:.1f}% of total</div>'
                f'</div>', unsafe_allow_html=True)
    with ci2:
        st.markdown("**State-wise Distribution**")
        if sel_sector != 'All Sectors' and sel_state == 'All States':
            sdf = filt.copy()
            sdf['su'] = sdf['sectors'].apply(lambda x: x.get(sel_sector, 0))
            sg = sdf.groupby('ls_state')['su'].sum().sort_values(ascending=False).head(20)
            mx = sg.max() or 1
            for state, val in sg.items():
                if val > 0:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">'
                        f'<div style="width:130px;font-size:11px;color:#94A3B8;font-weight:500">{state[:18]}</div>'
                        f'<div style="flex:1;background:#1E2433;border-radius:3px;height:6px">'
                        f'<div style="background:#60A5FA;width:{int(val/mx*100)}%;height:6px;border-radius:3px"></div>'
                        f'</div>'
                        f'<div style="font-size:11px;color:#60A5FA;font-family:Space Mono,monospace;width:45px;text-align:right">{val:,}</div>'
                        f'</div>', unsafe_allow_html=True)
        else:
            st.info("Select a specific Industry Sector (in sidebar) to see state-wise breakdown.")

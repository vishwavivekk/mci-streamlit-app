import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Manufacturing Cluster Intelligence",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS — Light Theme ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif !important; }

.stApp { background-color: #F5F7FA !important; }
section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #DCE3EA; }
section[data-testid="stSidebar"] * { color: #1F2937 !important; }

.metric-card {
    background: #FFFFFF;
    border: 1px solid #DCE3EA;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.metric-val {
    font-size: 28px;
    font-weight: 700;
    color: #2563EB;
    font-family: 'JetBrains Mono', monospace;
}
.metric-lbl {
    font-size: 11px;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}
.section-title {
    font-size: 12px;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #DCE3EA;
}
.party-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.stTabs [role="tab"] { color: #1F2937 !important; }
.stTabs [role="tab"][aria-selected="true"] { color: #2563EB !important; border-bottom-color: #2563EB !important; }
[data-testid="stDataFrame"] { background: #FFFFFF; border: 1px solid #DCE3EA; border-radius: 8px; }
h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #1F2937 !important; }
.stCaption { color: #6B7280 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Data Loading ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':       '#E8620A',
    'Indian National Congress':     '#1A56DB',
    'Aam Aadmi Party':              '#3B9EE2',
    'Samajwadi Party':              '#DC2626',
    'Bahujan Samaj Party':          '#1E3A8A',
    'All India Trinamool Congress': '#16A34A',
    'Trinamool Congress':           '#16A34A',
    'Dravida Munnetra Kazhagam':    '#7F1D1D',
    'Telugu Desam':                 '#CA8A04',
    'Janata Dal  (United)':         '#7C3AED',
    'YSR Congress Party':           '#0D6EFD',
    'Biju Janata Dal':              '#0D9488',
    'Shiv Sena':                    '#B45309',
    'Janasena Party':               '#BE185D',
    'Rashtriya Lok Dal':            '#65A30D',
}

IND_COLORS = [
    '#2563EB','#059669','#DC2626','#D97706','#7C3AED',
    '#DB2777','#0891B2','#EA580C','#4F46E5','#B45309',
    '#16A34A','#CA8A04','#6D28D9','#BE185D','#0D9488',
    '#E11D48','#84CC16','#0284C7','#A21CAF','#C2410C',
    '#0E7490','#15803D','#B91C1C','#6B21A8','#A16207',
    '#166534','#1E40AF','#991B1B','#5B21B6','#92400E',
]

def get_party_color(party):
    return PARTY_COLORS.get(party, '#6B7280')

def get_dist_km(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@st.cache_data
def load_data():
    csv_path = os.path.join(BASE_DIR, 'Annexure_with_3digit_Sheet1_.csv')
    df_raw = pd.read_csv(csv_path)
    df_units = df_raw.iloc[1:].reset_index(drop=True)
    df_units.columns = df_raw.columns

    industry_cols = [c for c in df_units.columns if c not in ['State', 'District', 'Latitude', 'Longitude']]
    df_units['Latitude']  = pd.to_numeric(df_units['Latitude'],  errors='coerce')
    df_units['Longitude'] = pd.to_numeric(df_units['Longitude'], errors='coerce')

    def safe_num(v):
        try:
            f = float(str(v).replace('-', '0').replace(',', ''))
            return 0 if math.isnan(f) else f
        except:
            return 0

    base_industries = {}
    for col in industry_cols:
        base = col.split('.')[0].strip()
        if base not in base_industries:
            base_industries[base] = []
        base_industries[base].append(col)

    records = []
    for _, row in df_units.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
            continue
        ind_totals = {}
        for base, cols in base_industries.items():
            total = sum(safe_num(row[c]) for c in cols)
            if total > 0:
                ind_totals[base] = int(total)
        total_all = sum(ind_totals.values())
        records.append({
            'state':       str(row['State']),
            'district':    str(row['District']),
            'lat':         float(row['Latitude']),
            'lon':         float(row['Longitude']),
            'total_units': total_all,
            'industries':  ind_totals,
        })

    xlsx_path = os.path.join(BASE_DIR, 'Lok_Sabha_Elections_Winners_2024.xlsx')
    df_lok = pd.read_excel(xlsx_path)

    lok_dict = {}
    for _, r in df_lok.iterrows():
        try:
            margin = int(r['Margin Votes'])
        except:
            margin = 0
        lok_dict[str(r['PC Name']).upper().strip()] = {
            'pc_name':      str(r['PC Name']),
            'state':        str(r['State']),
            'winner':       str(r['Winning Candidate']),
            'party':        str(r['Winning Party']),
            'runner_up':    str(r['Runner-up Canddiate']),
            'runner_party': str(r['Runner-up Party']),
            'margin':       margin,
        }

    for rec in records:
        key = rec['district'].upper().strip()
        if key in lok_dict:
            rec.update(lok_dict[key])
            rec['matched_pc'] = True
        else:
            rec['matched_pc'] = False

    df = pd.DataFrame(records)

    all_industries = sorted(set(
        ind for rec in records for ind in rec['industries'].keys()
    ))
    ind_color_map = {ind: IND_COLORS[i % len(IND_COLORS)] for i, ind in enumerate(all_industries)}

    lok_list = list(lok_dict.values())

    return df, lok_list, all_industries, ind_color_map

# ─── Load ───────────────────────────────────────────────────────────────
df, lok_list, all_industries, ind_color_map = load_data()

# ─── Sidebar Filters ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Manufacturing Cluster Intelligence")
    st.markdown("*Lok Sabha 2024 × Industrial Units*")
    st.divider()

    st.markdown("#### 🔍 Filters")

    states = ['All States'] + sorted(df['state'].unique().tolist())
    sel_state = st.selectbox("State", states)

    industries_list = ['All Industries'] + all_industries
    sel_industry = st.selectbox("Industry Sector", industries_list)

    all_parties = ['All Parties'] + sorted(set(p['party'] for p in lok_list))
    sel_party = st.selectbox("Winning Party (PC)", all_parties)

    match_filter = st.radio("District Type", ['All', 'PC Matched Only', 'Non-PC Districts'])

    st.divider()
    st.markdown("#### 🗺️ Map Options")
    view_mode = st.radio("Color Mode", ['Winning Party', 'Top Industry', 'Units Count'])

    st.divider()
    st.caption(f"📊 {len(df)} districts · {df['total_units'].sum():,} total units")

# ─── Apply Filters ──────────────────────────────────────────────────────────
filtered = df.copy()

if sel_state != 'All States':
    filtered = filtered[filtered['state'] == sel_state]

if sel_industry != 'All Industries':
    filtered = filtered[filtered['industries'].apply(
        lambda x: sel_industry in x and x.get(sel_industry, 0) > 0
    )]

if sel_party != 'All Parties' and 'party' in filtered.columns:
    filtered = filtered[filtered['party'].fillna('') == sel_party]

if match_filter == 'PC Matched Only':
    filtered = filtered[filtered['matched_pc'] == True]
elif match_filter == 'Non-PC Districts':
    filtered = filtered[filtered['matched_pc'] == False]

# ─── Compute new summary card values ─────────────────────────────────────────
pc_with_units    = 0
pc_without_units = 0
if 'matched_pc' in filtered.columns:
    pc_matched_df    = filtered[filtered['matched_pc'] == True]
    pc_with_units    = int((pc_matched_df['total_units'] > 0).sum())
    pc_without_units = int((pc_matched_df['total_units'] == 0).sum())

# ─── Header Metrics ────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{len(filtered)}</div>'
        f'<div class="metric-lbl">Districts Shown</div></div>',
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{int(filtered["total_units"].sum()):,}</div>'
        f'<div class="metric-lbl">Industrial Units</div></div>',
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{pc_with_units}</div>'
        f'<div class="metric-lbl">Principal Constituencies with Units</div></div>',
        unsafe_allow_html=True
    )
with c4:
    st.markdown(
        f'<div class="metric-card"><div class="metric-val">{pc_without_units}</div>'
        f'<div class="metric-lbl">Principal Constituencies without Units</div></div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Layout: Full-width Map ───────────────────────────────────────────────
center_lat = filtered['lat'].mean() if len(filtered) > 0 else 22.5
center_lon = filtered['lon'].mean() if len(filtered) > 0 else 80.0

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=5 if sel_state == 'All States' else 7,
    tiles=None,
    prefer_canvas=True,
)

# Light tile layer
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='© OpenStreetMap © CartoDB',
    name='Light',
    max_zoom=18,
).add_to(m)

def get_color(row):
    if view_mode == 'Top Industry':
        if row['industries']:
            top_ind = max(row['industries'], key=row['industries'].get)
            return ind_color_map.get(top_ind, '#6B7280')
        return '#6B7280'
    elif view_mode == 'Winning Party':
        if row.get('matched_pc') and 'party' in row.index and pd.notna(row.get('party', '')):
            return get_party_color(row['party'])
        return '#9CA3AF'
    else:  # Units Count
        u = row['total_units']
        if u > 500: return '#DC2626'
        if u > 100: return '#D97706'
        if u > 20:  return '#059669'
        return '#2563EB'

def get_radius(units):
    """Bubble size represents industrial unit count."""
    return max(5, min(28, math.sqrt(units + 1) * 1.1))

for _, row in filtered.iterrows():
    color  = get_color(row)
    r      = get_radius(row['total_units'])
    is_pc  = row.get('matched_pc', False)

    top_inds = sorted(row['industries'].items(), key=lambda x: -x[1])[:5] if row['industries'] else []
    ind_html = ''.join(
        f'<tr>'
        f'<td style="color:#374151;font-size:11px;padding:1px 4px">{k[:35]}</td>'
        f'<td style="font-weight:600;color:#2563EB;font-size:11px;padding:1px 4px">{v}</td>'
        f'</tr>'
        for k, v in top_inds
    )

    pc_html = ''
    if is_pc:
        pc_color = get_party_color(row.get('party', ''))
        pc_html = f'''
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid #DCE3EA">
          <div style="font-size:10px;color:#6B7280;margin-bottom:4px">PARLIAMENTARY CONSTITUENCY</div>
          <div style="font-weight:700;color:#059669;font-size:12px">{row.get('pc_name','')}</div>
          <div style="font-size:11px;color:#1F2937;margin-top:3px">🏆 {row.get('winner','')}</div>
          <div style="font-size:11px;color:{pc_color};font-weight:600">{row.get('party','')}</div>
          <div style="font-size:11px;color:#6B7280">Margin: {row.get('margin',0):,} votes</div>
        </div>'''

    popup_html = f'''
    <div style="font-family:'Space Grotesk',sans-serif;min-width:220px;background:#FFFFFF;color:#1F2937;border-radius:8px;padding:4px;">
      <div style="font-size:14px;font-weight:700;margin-bottom:2px;color:#1F2937">{row['district']}</div>
      <div style="font-size:11px;color:#6B7280;margin-bottom:8px">{row['state']}</div>
      <div style="font-size:20px;font-weight:700;color:#2563EB;margin-bottom:4px">{row['total_units']:,}</div>
      <div style="font-size:10px;color:#6B7280;margin-bottom:8px">INDUSTRIAL UNITS</div>
      <table style="width:100%">{ind_html}</table>
      {pc_html}
    </div>'''

    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=r,
        color='#1F2937' if is_pc else color,
        weight=2 if is_pc else 0.8,
        fill=True,
        fill_color=color,
        fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=280),
        tooltip=f"{row['district']} | {row['total_units']:,} units" + (
            f" | PC: {row.get('pc_name','')}" if is_pc else ''
        ),
    ).add_to(m)

st.markdown("#### 🗺️ Interactive Map")
map_data = st_folium(m, width=None, height=560, returned_objects=["last_object_clicked"])

# ─── District Rankings Section (Below Map) ────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### 📋 District Rankings")

ranking_cols = st.columns([2, 1, 1])
sorted_filtered = filtered.sort_values('total_units', ascending=False)

selected_district_data = None

if map_data and map_data.get('last_object_clicked'):
    clicked = map_data['last_object_clicked']
    clat, clon = clicked.get('lat'), clicked.get('lng')
    if clat and clon:
        dists = filtered.apply(lambda r: get_dist_km(clat, clon, r['lat'], r['lon']), axis=1)
        if len(dists) > 0:
            closest_idx = dists.idxmin()
            selected_district_data = filtered.loc[closest_idx]

# Layout: Rankings on left, detail on right
rank_col, detail_col = st.columns([2, 1])

with rank_col:
    st.markdown("**Top Districts by Industrial Units**")
    for i, (_, row) in enumerate(sorted_filtered.head(20).iterrows()):
        is_pc      = row.get('matched_pc', False)
        top_ind    = max(row['industries'], key=row['industries'].get) if row['industries'] else '—'
        top_short  = top_ind[:25] + '…' if len(top_ind) > 25 else top_ind
        border     = '#059669' if is_pc else '#DCE3EA'
        party_info = (
            f'<div style="color:{get_party_color(row.get("party",""))};font-size:10px;font-weight:600">'
            f'{row.get("party","")[:22]}</div>'
            if is_pc else ''
        )
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid {border};border-radius:7px;padding:10px;
                    margin-bottom:7px;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                    <div style="font-weight:700;font-size:12px;color:#1F2937">{row['district']}</div>
                    <div style="color:#6B7280;font-size:10px">{row['state']}</div>
                    <div style="color:#9CA3AF;font-size:10px;margin-top:2px">{top_short}</div>
                    {party_info}
                </div>
                <div style="text-align:right">
                    <div style="color:#2563EB;font-weight:700;font-family:'JetBrains Mono',monospace">{row['total_units']:,}</div>
                    <div style="color:#9CA3AF;font-size:10px">units</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with detail_col:
    if selected_district_data is not None:
        sel_row = selected_district_data
        st.markdown(f"**{sel_row['district']}**")
        st.caption(sel_row['state'])
        st.metric("Total Units", f"{sel_row['total_units']:,}")

        if sel_row.get('matched_pc'):
            pc_color = get_party_color(sel_row.get('party', ''))
            st.markdown(f"""
            <div style="background:#EFF6FF;border:1px solid #059669;border-radius:8px;padding:12px;margin:8px 0">
                <div class="section-title">🗳 PC Details</div>
                <div style="font-weight:700;color:#059669">{sel_row.get('pc_name','')}</div>
                <div style="font-size:12px;margin-top:4px;color:#1F2937">🏆 {sel_row.get('winner','')}</div>
                <div style="font-size:12px;color:{pc_color};font-weight:600">{sel_row.get('party','')}</div>
                <div style="font-size:11px;color:#6B7280">Margin: {sel_row.get('margin',0):,}</div>
            </div>
            """, unsafe_allow_html=True)

        if sel_row['industries']:
            st.markdown('<div class="section-title">🏭 Industries</div>', unsafe_allow_html=True)
            top_inds = sorted(sel_row['industries'].items(), key=lambda x: -x[1])
            max_val  = top_inds[0][1] if top_inds else 1
            for ind_name, cnt in top_inds[:10]:
                pct   = cnt / max_val
                color = ind_color_map.get(ind_name, '#2563EB')
                short = ind_name[:28] + '…' if len(ind_name) > 28 else ind_name
                st.markdown(f"""
                <div style="margin-bottom:6px">
                    <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">
                        <span style="color:#374151" title="{ind_name}">{short}</span>
                        <span style="color:{color};font-family:'JetBrains Mono',monospace;font-weight:600">{cnt}</span>
                    </div>
                    <div style="background:#E5E7EB;border-radius:2px;height:5px">
                        <div style="background:{color};width:{int(pct*100)}%;height:5px;border-radius:2px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        nearby = []
        for _, r2 in df[df['matched_pc'] == True].iterrows():
            d = get_dist_km(sel_row['lat'], sel_row['lon'], r2['lat'], r2['lon'])
            if 0 < d <= 150:
                nearby.append((d, r2))
        nearby.sort(key=lambda x: x[0])
        if nearby:
            st.markdown('<div class="section-title" style="margin-top:12px">📍 Nearby PCs (&lt;150km)</div>', unsafe_allow_html=True)
            for dist, nr in nearby[:6]:
                pc_col = get_party_color(nr.get('party', ''))
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:11px">
                    <span><b style="color:#1F2937">{nr.get('pc_name','')}</b><br>
                    <span style="color:{pc_col};font-weight:600">{nr.get('party','')[:20]}</span></span>
                    <span style="color:#6B7280;font-family:'JetBrains Mono',monospace">{dist:.0f}km</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👉 Click on a district marker on the map to see detailed information here")

# ─── Bottom Tabs ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["📊 Data Table", "🗳 PC Analysis", "🏭 Industry Summary"])

with tab1:
    display_cols = ['state', 'district', 'lat', 'lon', 'total_units', 'matched_pc']
    if 'pc_name' in filtered.columns:
        display_cols += ['pc_name', 'winner', 'party', 'margin']

    disp = filtered[display_cols].copy()
    disp.columns = [c.replace('_', ' ').title() for c in disp.columns]
    disp = disp.sort_values('Total Units', ascending=False)

    col_a, col_b = st.columns([3, 1])
    with col_b:
        csv_data = disp.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv_data, "manufacturing_clusters.csv", "text/csv")

    st.dataframe(disp, use_container_width=True, height=350)

with tab2:
    st.markdown("### Parliamentary Constituency Analysis")

    pc_df = (
        filtered[filtered['matched_pc'] == True].copy()
        if 'matched_pc' in filtered.columns
        else pd.DataFrame()
    )

    if len(pc_df) > 0 and 'party' in pc_df.columns:
        party_summary = pc_df.groupby('party').agg(
            constituencies=('pc_name', 'count'),
            total_units=('total_units', 'sum'),
            avg_units=('total_units', 'mean'),
        ).reset_index().sort_values('total_units', ascending=False)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Party-wise Industrial Strength**")
            for _, pr in party_summary.iterrows():
                col = get_party_color(pr['party'])
                pct = pr['total_units'] / party_summary['total_units'].sum()
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
                        <span style="color:{col};font-weight:600">{pr['party'][:35]}</span>
                        <span style="color:#2563EB;font-family:'JetBrains Mono',monospace">{int(pr['total_units']):,} units</span>
                    </div>
                    <div style="background:#E5E7EB;border-radius:2px;height:6px">
                        <div style="background:{col};width:{int(pct*100)}%;height:6px;border-radius:2px"></div>
                    </div>
                    <div style="color:#6B7280;font-size:10px">{int(pr['constituencies'])} constituencies · avg {int(pr['avg_units']):,}/const</div>
                </div>
                """, unsafe_allow_html=True)

        with col_p2:
            st.markdown("**Top PC Constituencies by Industrial Units**")
            top_pcs = pc_df.sort_values('total_units', ascending=False).head(15)
            for _, pr in top_pcs.iterrows():
                col = get_party_color(pr.get('party', ''))
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;
                            padding:6px 8px;background:#FFFFFF;border-radius:5px;border-left:3px solid {col};
                            box-shadow:0 1px 3px rgba(0,0,0,0.06)">
                    <div>
                        <div style="font-size:12px;font-weight:600;color:#1F2937">{pr.get('pc_name','')}</div>
                        <div style="font-size:10px;color:{col};font-weight:600">{pr.get('party','')[:25]}</div>
                    </div>
                    <div style="color:#2563EB;font-weight:700;font-family:'JetBrains Mono',monospace">{pr['total_units']:,}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No PC-matched districts in current filter. Try selecting 'All' in District Type.")

with tab3:
    st.markdown("### Industry Sector Summary")
    ind_agg = {}
    for _, row in filtered.iterrows():
        for ind, cnt in row['industries'].items():
            ind_agg[ind] = ind_agg.get(ind, 0) + cnt

    ind_sorted = sorted(ind_agg.items(), key=lambda x: -x[1])
    total_ind   = sum(v for _, v in ind_sorted)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**All Industry Sectors**")
        for ind, cnt in ind_sorted:
            pct = cnt / total_ind if total_ind else 0
            col = ind_color_map.get(ind, '#6B7280')
            st.markdown(f"""
            <div style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:2px">
                    <span style="color:#1F2937" title="{ind}">{ind[:40] if len(ind) > 40 else ind}</span>
                    <span style="color:{col};font-family:'JetBrains Mono',monospace;font-weight:600">{cnt:,}</span>
                </div>
                <div style="background:#E5E7EB;border-radius:2px;height:5px">
                    <div style="background:{col};width:{int(pct*100)}%;height:5px;border-radius:2px"></div>
                </div>
                <div style="color:#9CA3AF;font-size:10px">{pct*100:.1f}% of total units</div>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        st.markdown("**Industry Distribution by State**")
        if sel_industry != 'All Industries' and sel_state == 'All States':
            state_ind = filtered.apply(lambda r: r['industries'].get(sel_industry, 0), axis=1)
            state_df  = filtered.copy()
            state_df['sel_ind_units'] = state_ind
            sg     = state_df.groupby('state')['sel_ind_units'].sum().sort_values(ascending=False).head(20)
            max_sg = sg.max() if len(sg) else 1
            for state, val in sg.items():
                if val > 0:
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
                        <div style="width:130px;font-size:11px;color:#374151">{state[:20]}</div>
                        <div style="flex:1;background:#E5E7EB;border-radius:2px;height:6px">
                            <div style="background:#2563EB;width:{int(val/max_sg*100)}%;height:6px;border-radius:2px"></div>
                        </div>
                        <div style="font-size:11px;color:#2563EB;font-family:'JetBrains Mono',monospace;width:40px;text-align:right">{val:,}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Select a specific Industry Sector in the sidebar to see state-wise distribution here.")

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os
from datetime import datetime

st.set_page_config(page_title="Janmat Industrial Constituency Portal", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

# ── CSS ──────────────────────────────────────────────────────────────[...]
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html,body,[class*="css"],.stApp{font-family:'Inter',sans-serif!important;background:#F4F6F9!important;color:#1E293B!important;}

/* kill header */
header[data-testid="stHeader"]{height:0!important;overflow:hidden!important;visibility:hidden!important;}
#MainMenu,footer,.stDeployButton,[data-testid="stToolbar"]{display:none!important;visibility:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:1rem!important;max-width:100%!important;}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{background:#FFFFFF!important;border-right:1px solid #E8ECF0!important;min-width:220px!important;max-width:220px!important;}
section[data-testid="stSidebar"] *{color:#1E293B!important;}
section[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#F8FAFC!important;border:1px solid #E2E8F0!important;border-radius:8px!important;color:#1E293B!important;}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div{color:#1E293B!important;background:transparent!important;}
[data-baseweb="popover"] [role="listbox"],[data-baseweb="menu"]{background:#FFFFFF!important;border:1px solid #CBD5E1!important;}
[data-baseweb="menu"] li,[data-baseweb="menu"] [role="option"]{color:#1E293B!important;background:#FFFFFF!important;}
[data-baseweb="menu"] li:hover,[data-baseweb="menu"] [aria-selected="true"]{background:#EFF6FF!important;color:#1D4ED8!important;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label,
section[data-testid="stSidebar"] [data-testid="stRadio"] p{color:#1E293B!important;}

/* sidebar nav item active */
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 16px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:500;color:#64748B;transition:all .15s;}
.nav-item:hover{background:#F0F4FF;color:#1D4ED8;}
.nav-item.active{background:#EFF6FF;color:#1D4ED8;border-left:3px solid #1D4ED8;font-weight:600;}
.nav-icon{font-size:16px;width:20px;text-align:center;}

/* ── TOP NAV BAR ── */
.top-bar{background:#FFFFFF;border-bottom:1px solid #E8ECF0;padding:10px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.search-box{display:flex;align-items:center;gap:8px;background:#F4F6F9;border:1px solid #E2E8F0;border-radius:20px;padding:7px 16px;min-width:320px;}
.search-box input{border:none;background:transparent;outline:none;font-size:13px;color:#64748B;width:100%;}
.page-title{font-size:17px;font-weight:700;color:#1E293B;letter-spacing:-.3px;}
.user-pill{display:flex;align-items:center;gap:8px;background:#F4F6F9;border-radius:20px;padding:5px 12px 5px 5px;}
.user-avatar{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#1D4ED8,#3B82F6);display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:700;}

/* ── METRIC CARDS ── */
.stat-card{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:12px;padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);position:relative;overflow:hidden;height:100px;display:flex;flex-direction:column;justify-content:space-between;}
.stat-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;border-radius:4px 0 0 4px;}
.stat-card.blue::before{background:#1D4ED8;}
.stat-card.green::before{background:#059669;}
.stat-card.orange::before{background:#F59E0B;}
.stat-card.red::before{background:#EF4444;}
.stat-label{font-size:9.5px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;}
.stat-value{font-size:26px;font-weight:800;color:#1E293B;line-height:1;font-family:'JetBrains Mono',monospace;white-space:nowrap;}
.stat-sub{font-size:10px;font-weight:600;margin-top:2px;}
.stat-sub.up{color:#059669;}
.stat-sub.warn{color:#F59E0B;}
.stat-sub.danger{color:#EF4444;}
.stat-icon{position:absolute;top:16px;right:16px;font-size:20px;opacity:.2;}

/* ── CARDS & PANELS ── */
.panel{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:12px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.panel-title{font-size:14px;font-weight:700;color:#1E293B;margin-bottom:14px;}

/* ── TABLE ROWS ── */
.tbl-row{display:flex;align-items:center;padding:10px 12px;border-bottom:1px solid #F1F5F9;gap:10px;}
.tbl-row:last-child{border-bottom:none;}
.tbl-row:hover{background:#F8FAFC;}
.status-pill{font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;text-transform:uppercase;letter-spacing:.5px;}
.optimal{background:#DCFCE7;color:#15803D;}
.expanding{background:#DBEAFE;color:#1D4ED8;}
.stable{background:#FEF9C3;color:#92400E;}
.excellent{background:#D1FAE5;color:#065F46;}

/* ── LOG ITEMS ── */
.log-item{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #F1F5F9;}
.log-time{font-size:10px;color:#94A3B8;font-family:'JetBrains Mono',monospace;white-space:nowrap;padding-top:2px;}
.log-bar{width:3px;border-radius:2px;flex-shrink:0;align-self:stretch;}
.log-content{font-size:12px;color:#374151;line-height:1.5;}

/* ── DISTRICT LIST ── */
.dist-card{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:8px;padding:9px 11px;margin-bottom:6px;box-shadow:0 1px 3px rgba(0,0,0,0.04);}
.dist-card.pc{border-left:3px solid #059669;background:#F0FDF4;}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"]{background:#FFFFFF!important;border-radius:10px!important;border:1px solid #E2E8F0!important;padding:4px!important;}
.stTabs [role="tab"]{color:#64748B!important;font-weight:500!important;border-radius:7px!important;padding:6px 14px!important;font-size:13px!important;}
.stTabs [role="tab"][aria-selected="true"]{background:#EFF6FF!important;color:#1D4ED8!important;font-weight:600!important;}

/* ── ZONE TOGGLE ── */
.zone-btn{display:inline-block;padding:4px 12px;font-size:11px;font-weight:600;border-radius:6px;cursor:pointer;}
.zone-btn.active{background:#1D4ED8;color:#fff;}
.zone-btn.inactive{background:#F1F5F9;color:#64748B;}

/* map legend */
.map-legend{background:#FFFFFF;border:1px solid #E8ECF0;border-radius:8px;padding:12px 14px;margin-top:8px;box-shadow:0 1px 4px rgba(0,0,0,0.05);}
.legend-title{font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
.legend-row{display:flex;align-items:center;gap:8px;margin-bottom:5px;font-size:11.5px;color:#374151;font-weight:500;}
.legend-dot{width:11px;height:11px;border-radius:50%;flex-shrink:0;}

h1,h2,h3,h4,h5,h6,p,span,label{color:#1E293B;}
.stCaption,.stCaption p{color:#64748B!important;}
[data-testid="stDataFrame"]{background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PARTY_COLORS = {
    'Bharatiya Janata Party':           '#F97316',
    'Indian National Congress':         '#3B82F6',
    'Aam Aadmi Party':                  '#06B6D4',
    'Samajwadi Party':                  '#EF4444',
    'Bahujan Samaj Party':              '#1E3A8A',
    'All India Trinamool Congress':     '#22C55E',
    'Trinamool Congress':               '#22C55E',
    'Dravida Munnetra Kazhagam':        '#991B1B',
    'Telugu Desam':                     '#EAB308',
    'Janata Dal  (United)':             '#8B5CF6',
    'YSR Congress Party':               '#0369A1',
    'Biju Janata Dal':                  '#0D9488',
    'Shiv Sena':                        '#D97706',
    'Janasena Party':                   '#EC4899',
    'Rashtriya Lok Dal':                '#84CC16',
    'Communist Party of India  (Marxist)':'#DC2626',
    'Nationalist Congress Party':       '#16A34A',
}
PARTY_ABBR = {
    'Bharatiya Janata Party':'BJP','Indian National Congress':'INC',
    'Aam Aadmi Party':'AAP','Samajwadi Party':'SP','Bahujan Samaj Party':'BSP',
    'All India Trinamool Congress':'TMC','Trinamool Congress':'TMC',
    'Dravida Munnetra Kazhagam':'DMK','Telugu Desam':'TDP',
    'Janata Dal  (United)':'JD(U)','YSR Congress Party':'YSRCP',
    'Biju Janata Dal':'BJD','Shiv Sena':'SS','Janasena Party':'JSP',
    'Rashtriya Lok Dal':'RLD','Communist Party of India  (Marxist)':'CPM',
    'Nationalist Congress Party':'NCP',
}
IND_COLORS = ['#3B82F6','#22C55E','#EF4444','#F59E0B','#8B5CF6','#EC4899',
              '#06B6D4','#F97316','#6366F1','#D97706','#16A34A','#EAB308',
              '#7C3AED','#BE185D','#0D9488','#E11D48','#84CC16','#0284C7',
              '#A21CAF','#C2410C','#0E7490','#15803D','#B91C1C','#6B21A8']

def get_party_color(p): return PARTY_COLORS.get(p,'#6366F1')
def get_party_abbr(p):  return PARTY_ABBR.get(p, p[:5] if p else '')

def get_dist_km(lat1,lon1,lat2,lon2):
    R=6371; dL=math.radians(lat2-lat1); dO=math.radians(lon2-lon1)
    a=math.sin(dL/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dO/2)**2
    return R*2*math.atan2(math.sqrt(a),math.sqrt(1-a))

# ── Data ──────────────────────────────────────────────────────────────[...]
@st.cache_data
def load_data():
    csv_path=os.path.join(BASE_DIR,'Annexure_with_3digit_Sheet1_.csv')
    df_raw=pd.read_csv(csv_path); df_u=df_raw.iloc[1:].reset_index(drop=True); df_u.columns=df_raw.columns
    icols=[c for c in df_u.columns if c not in ['State','District','Latitude','Longitude']]
    df_u['Latitude']=pd.to_numeric(df_u['Latitude'],errors='coerce')
    df_u['Longitude']=pd.to_numeric(df_u['Longitude'],errors='coerce')
    def sn(v):
        try: f=float(str(v).replace('-','0').replace(',','')); return 0 if math.isnan(f) else f
        except: return 0
    bases={}
    for c in icols: b=c.split('.')[0].strip(); bases.setdefault(b,[]).append(c)
    recs=[]
    for _,row in df_u.iterrows():
        if pd.isna(row['Latitude']) or pd.isna(row['Longitude']): continue
        it={b:int(s) for b,cs in bases.items() if (s:=sum(sn(row[c]) for c in cs))>0}
        recs.append({'state':str(row['State']),'district':str(row['District']),
                     'lat':float(row['Latitude']),'lon':float(row['Longitude']),
                     'total_units':sum(it.values()),'industries':it})
    xlsx_path=os.path.join(BASE_DIR,'Lok_Sabha_Elections_Winners_2024.xlsx')
    df_lok=pd.read_excel(xlsx_path); lok={}
    for _,r in df_lok.iterrows():
        try: mg=int(r['Margin Votes'])
        except: mg=0
        lok[str(r['PC Name']).upper().strip()]={
            'pc_name':str(r['PC Name']),'state':str(r['State']),
            'winner':str(r['Winning Candidate']),'party':str(r['Winning Party']),
            'runner_up':str(r['Runner-up Canddiate']),'runner_party':str(r['Runner-up Party']),'margin':mg}
    for rec in recs:
        k=rec['district'].upper().strip()
        if k in lok: rec.update(lok[k]); rec['matched_pc']=True
        else: rec['matched_pc']=False
    df=pd.DataFrame(recs)
    all_ind=sorted({i for r in recs for i in r['industries']})
    icm={i:IND_COLORS[n%len(IND_COLORS)] for n,i in enumerate(all_ind)}
    return df,list(lok.values()),all_ind,icm

df,lok_list,all_industries,ind_color_map=load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 16px 8px">
      <div style="font-size:16px;font-weight:800;color:#1D4ED8;line-height:1.2">Janmat Industrial</div>
      <div style="font-size:10px;color:#64748B;margin-top:2px;font-weight:500">Constituency Portal v1.0</div>
    </div>
    <div style="height:1px;background:#E8ECF0;margin:8px 0 12px"></div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:1px;padding:0 16px;margin-bottom:8px">Filters</p>',unsafe_allow_html=True)

    states=['All States']+sorted(df['state'].unique().tolist())
    sel_state=st.selectbox("State",states,key="ss")
    industries_l=['All Industries']+all_industries
    sel_industry=st.selectbox("Industry",industries_l,key="si")
    all_parties=['All Parties']+sorted({p['party'] for p in lok_list})
    sel_party=st.selectbox("Winning Party",all_parties,key="sp")
    match_filter=st.radio("District Type",['All','Matched Principal Constituency','Non-Principal Constituency Districts'])
    st.markdown('<div style="height:1px;background:#E8ECF0;margin:12px 0"></div>',unsafe_allow_html=True)
    view_mode=st.radio("Map Colors",['Winning Party','Top Industry','Units Count'])

# ── Filters ───────────────────────────────────────────────────────────────
filtered=df.copy()
if sel_state!='All States': filtered=filtered[filtered['state']==sel_state]
if sel_industry!='All Industries': filtered=filtered[filtered['industries'].apply(lambda x:x.get(sel_industry,0)>0)]
if sel_party!='All Parties' and 'party' in filtered.columns: filtered=filtered[filtered['party'].fillna('')==sel_party]
if match_filter=='Matched Principal Constituency': filtered=filtered[filtered['matched_pc']==True]
elif match_filter=='Non-Principal Constituency Districts': filtered=filtered[filtered['matched_pc']==False]

pc_df2=filtered[filtered['matched_pc']==True] if 'matched_pc' in filtered.columns else pd.DataFrame()
pc_with=int((pc_df2['total_units']>0).sum()) if len(pc_df2) else 0
pc_without=int((pc_df2['total_units']==0).sum()) if len(pc_df2) else 0
avg_u=int(filtered['total_units'].mean()) if len(filtered) else 0
tot_u=int(filtered['total_units'].sum())

# ── Top nav bar ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="top-bar">
  <div class="search-box">
    <span style="color:#94A3B8;font-size:14px">🔍</span>
    <span style="font-size:13px;color:#94A3B8">Search PCs (e.g. Varanasi, Wayanad)...</span>
  </div>
  <div class="page-title">Parliamentary Industrial Intelligence</div>
  <div style="display:flex;align-items:center;gap:14px">
    <div style="font-size:12px;color:#64748B;font-weight:500">Lok Sabha Secretariat</div>
  </div>
</div>
<div style="height:16px"></div>
""",unsafe_allow_html=True)

# ── Stat cards ──────────────────────────────────────────────────────────
c1,c2,c3,c4=st.columns(4)
def stat_card(col,cls,icon,label,value,sub,sub_cls):
    with col:
        st.markdown(f"""
        <div class="stat-card {cls}">
          <div class="stat-label">{label}</div>
          <div>
            <div class="stat-value">{value}</div>
            <div class="stat-sub {sub_cls}">{sub}</div>
          </div>
          <div class="stat-icon">{icon}</div>
        </div>""",unsafe_allow_html=True)

stat_card(c1,'blue','📊','Avg PC Productivity',f'₹ {avg_u:,}','+ Industrial Units / PC','up')
stat_card(c2,'green','🏗️','Constituency Growth',f'{pc_with}','Principal Constituencies with Active Units','up')
stat_card(c3,'orange','👥','Active Political Rep.',f'{len(filtered):,}','Districts Reporting','warn')
stat_card(c4,'red','📅','Pending (No Units)',f'{pc_without}',f'ACTION REQUIRED: {pc_without} PCs','danger')

st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)

# ── Map helpers ──────────────────────────────────────────────────────────
def get_color(row):
    if view_mode=='Top Industry':
        return ind_color_map.get(max(row['industries'],key=row['industries'].get),'#6366F1') if row['industries'] else '#6366F1'
    elif view_mode=='Winning Party':
        return get_party_color(row['party']) if row.get('matched_pc') and pd.notna(row.get('party','')) else '#6366F1'
    else:
        u=row['total_units']
        if u>500: return '#EF4444'
        if u>100: return '#F59E0B'
        if u>20:  return '#22C55E'
        return '#3B82F6'

def get_radius(u): return max(5,min(30,math.sqrt(u+1)*1.15))

def build_legend():
    rows=""
    if view_mode=='Units Count':
        for col,lbl in [('#EF4444','500+ units'),('#F59E0B','100–500'),('#22C55E','20–100'),('#3B82F6','< 20')]:
            rows+=f'<div class="legend-row"><div class="legend-dot" style="background:{col}"></div>{lbl}</div>'
    elif view_mode=='Top Industry':
        ic={}
        for _,row in filtered.iterrows():
            for k,v in row['industries'].items(): ic[k]=ic.get(k,0)+v
        for k,_ in sorted(ic.items(),key=lambda x:-x[1])[:8]:
            rows+=f'<div class="legend-row"><div class="legend-dot" style="background:{ind_color_map.get(k,"#6366F1")}"></div>{k[:26]}</div>'
    else:
        if 'party' in filtered.columns:
            for p in sorted(filtered[filtered['matched_pc']==True]['party'].dropna().unique())[:10]:
                c=get_party_color(p)
                rows+=f'<div class="legend-row"><div class="legend-dot" style="background:{c}"></div><b style="color:{c}">{get_party_abbr(p)}</b> — {p[:22]}</div>'
        rows+='<div class="legend-row"><div class="legend-dot" style="background:#6366F1"></div>No PC data</div>'
    return f'<div class="map-legend"><div class="legend-title">{view_mode}</div>{rows}<div style="margin-top:8px;padding-top:8px;border-top:1px solid #E8ECF0;font-size:10px;color:#94A3B8">● Bubble size represents industrial unit count</div></div>'

# ── Main layout ──────────────────────────────────────────────────────────
left_col, right_col = st.columns([2, 1])

with left_col:
    # Map panel
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="font-size:14px;font-weight:700;color:#1E293B">🗺️ National Industrial Heatmap</div>
    </div>""",unsafe_allow_html=True)

    clat=filtered['lat'].mean() if len(filtered)>0 else 22.5
    clon=filtered['lon'].mean() if len(filtered)>0 else 80.0
    m=folium.Map(location=[clat,clon],zoom_start=5 if sel_state=='All States' else 7,tiles=None,prefer_canvas=True)
    folium.TileLayer(tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                     attr='© OpenStreetMap © CartoDB',name='Light',max_zoom=19).add_to(m)

    for _,row in filtered.iterrows():
        color=get_color(row); r=get_radius(row['total_units']); is_pc=row.get('matched_pc',False)
        top_inds=sorted(row['industries'].items(),key=lambda x:-x[1])[:5] if row['industries'] else []
        # Build popup as plain HTML (no f-string nesting that causes rendering issues)
        ind_rows=""
        for k,v in top_inds:
            ind_rows+='<tr><td style="color:#374151;font-size:11px;padding:2px 5px">'+k[:30]+'</td><td style="font-weight:600;color:#1D4ED8;font-size:11px;padding:2px 5px;text-align:right">'+str(v)+'</td></tr>'
        pc_block=""
        if is_pc:
            pc_col=get_party_color(row.get('party',''))
            pc_name=str(row.get('pc_name',''))
            winner=str(row.get('winner',''))
            party=str(row.get('party',''))
            margin=str(row.get('margin',0))
            pc_block=(
                '<div style="margin-top:8px;padding-top:8px;border-top:1px solid #E2E8F0">'
                '<div style="font-size:9px;font-weight:700;color:#64748B;letter-spacing:.8px;text-transform:uppercase">Parliamentary Constituency</div>'
                '<div style="font-weight:700;color:#059669;font-size:12px;margin-top:3px">'+pc_name+'</div>'
                '<div style="font-size:11px;color:#1E293B;margin-top:3px">🏆 '+winner+'</div>'
                '<div style="font-size:11px;font-weight:600;color:'+pc_col+';margin-top:1px">'+party+'</div>'
                '<div style="font-size:10px;color:#64748B;margin-top:1px">Margin: '+margin+' votes</div>'
                '</div>'
            )
        popup_html=(
            '<div style="font-family:Inter,sans-serif;min-width:210px;background:#FFFFFF;color:#1E293B;padding:4px">'
            '<div style="font-size:14px;font-weight:700;color:#1E293B">'+str(row['district'])+'</div>'
            '<div style="font-size:11px;color:#64748B;margin-bottom:6px">'+str(row['state'])+'</div>'
            '<div style="font-size:22px;font-weight:800;color:#1D4ED8;line-height:1.1">'+str(row['total_units'])+'</div>'
            '<div style="font-size:9.5px;color:#94A3B8;letter-spacing:.8px;margin-bottom:6px">INDUSTRIAL UNITS</div>'
            '<table style="width:100%;border-collapse:collapse">'+ind_rows+'</table>'
            +pc_block+
            '</div>'
        )
        folium.CircleMarker(
            location=[row['lat'],row['lon']],radius=r,
            color='#1E293B' if is_pc else color,weight=2.5 if is_pc else 0.8,
            fill=True,fill_color=color,fill_opacity=0.82,
            popup=folium.Popup(popup_html,max_width=270),
            tooltip='<b>'+str(row['district'])+'</b> · '+str(row['total_units'])+' units'+((' · '+str(row.get('pc_name',''))) if is_pc else ''),
        ).add_to(m)

    map_data=st_folium(m,width=None,height=480,returned_objects=["last_object_clicked"])
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown(build_legend(),unsafe_allow_html=True)

    # Activity / Output section below map
    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

    zone_l, zone_r = st.columns(2)
    with zone_l:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
          <div style="font-size:13px;font-weight:700;color:#1E293B">📈 Industrial Output Trend by Zone</div>
          <div style="display:flex;gap:4px">
            <span class="zone-btn inactive">NORTH</span>
            <span class="zone-btn active">SOUTH</span>
            <span class="zone-btn inactive">EAST</span>
          </div>
        </div>""",unsafe_allow_html=True)
        if len(filtered) > 0:
            zone_data = filtered.sort_values('total_units', ascending=False).head(8).copy()
            max_v = zone_data['total_units'].max()
            if max_v == 0: max_v = 1
            bar_html = '<div style="display:flex;align-items:flex-end;gap:6px;height:80px;padding-top:4px">'
            for _, r2 in zone_data.iterrows():
                h = max(8, int(r2['total_units'] / max_v * 76))
                is_top = r2['total_units'] == zone_data['total_units'].max()
                dname = str(r2['district'])[:5]
                bar_html += (
                    '<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:2px">'
                    '<div style="width:100%;height:' + str(h) + 'px;background:' +
                    ('#1D4ED8' if is_top else '#BFDBFE') +
                    ';border-radius:4px 4px 0 0"></div>'
                    '<div style="font-size:8px;color:#94A3B8;text-align:center">' + dname + '</div>'
                    '</div>'
                )
            bar_html += '</div>'
            st.markdown(bar_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with zone_r:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:700;color:#1E293B;margin-bottom:12px">📋 Principal Constituency Activity Logs</div>',unsafe_allow_html=True)
        # Real activity from top PC matches
        top_pcs=df[df['matched_pc']==True].sort_values('total_units',ascending=False).head(4)
        log_colors=['#1D4ED8','#F59E0B','#059669','#EF4444']
        log_types=['APPROVAL','NOTICE','REPORT','ALERT']
        log_msgs=['New industrial units sanctioned in PC:','Land acquisition query raised for PC:',
                  'Quarterly compliance data updated for:','Industrial review pending for PC:']
        now=datetime.now()
        for i,((_,pc_r),lc,lt,lm) in enumerate(zip(top_pcs.iterrows(),log_colors,log_types,log_msgs)):
            t=f"{(now.hour-i)%12 or 12}:{['45','12','58','30'][i]} {'AM' if i<2 else 'PM'}"
            pn=str(pc_r.get('pc_name','Unknown'))
            st.markdown(
                '<div class="log-item">'
                '<div class="log-time">'+t+'</div>'
                '<div class="log-bar" style="background:'+lc+'"></div>'
                '<div class="log-content"><b>'+lt+'</b> '+lm+' <b style="color:'+lc+'">'+pn+'</b></div>'
                '</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>',unsafe_allow_html=True)

with right_col:
    # Top Industrial Principal Constituencies table
    st.markdown('<div class="panel">',unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🏆 Top Industrial Principal Constituencies</div>',unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;padding:0 0 8px;border-bottom:1px solid #E8ECF0;margin-bottom:4px">
      <div style="flex:1;font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase">PC / Party</div>
      <div style="width:55px;text-align:right;font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase">Units</div>
      <div style="width:70px;text-align:right;font-size:10px;font-weight:700;color:#94A3B8;text-transform:uppercase">Status</div>
    </div>""",unsafe_allow_html=True)

    top_pcs_tbl=pc_df2.sort_values('total_units',ascending=False).head(8) if len(pc_df2) else pd.DataFrame()
    status_map=[(2000,'excellent','EXCELLENT'),(1000,'optimal','OPTIMAL'),(400,'expanding','EXPANDING'),(0,'stable','STABLE')]
    for _,r2 in top_pcs_tbl.iterrows():
        pc_col=get_party_color(r2.get('party',''))
        u=r2['total_units']
        sclass,slabel='stable','STABLE'
        for thresh,sc,sl in status_map:
            if u>thresh: sclass,slabel=sc,sl; break
        abbr=get_party_abbr(r2.get('party',''))
        state_short=str(r2.get('state','')).replace('Uttar Pradesh','UP').replace('Maharashtra','MH').replace('West Bengal','WB').replace('Tamil Nadu','TN').replace('Karnataka','KA').replace('Andhra Pradesh','AP').replace('Bihar','BR')
        st.markdown(
            '<div class="tbl-row">'
            '<div style="flex:1;min-width:0">'
            '<div style="font-size:12px;font-weight:600;color:#1E293B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+str(r2.get('pc_name',''))+'</div>'
            '<div style="font-size:10px;font-weight:600;color:'+pc_col+'">'+abbr+' · '+state_short+'</div>'
            '</div>'
            '<div style="width:55px;text-align:right;font-size:13px;font-weight:700;font-family:JetBrains Mono,monospace;color:#1E293B">'+f"{u:,}"+'</div>'
            '<div style="width:70px;text-align:right"><span class="status-pill '+sclass+'">'+slabel+'</span></div>'
            '</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>',unsafe_allow_html=True)

    # Selected district detail (click from map)
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
    sorted_filtered=filtered.sort_values('total_units',ascending=False)

    sel_row=None
    if map_data and map_data.get('last_object_clicked'):
        clicked=map_data['last_object_clicked']
        clat2,clon2=clicked.get('lat'),clicked.get('lng')
        if clat2 and clon2:
            dists=filtered.apply(lambda r:get_dist_km(clat2,clon2,r['lat'],r['lon']),axis=1)
            if len(dists)>0: sel_row=filtered.loc[dists.idxmin()]

    if sel_row is not None:
        st.markdown('<div class="panel">',unsafe_allow_html=True)
        district_name=str(sel_row['district'])
        state_name=str(sel_row['state'])
        total=int(sel_row['total_units'])
        st.markdown(
            '<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:12px;margin-bottom:10px">'
            '<div style="font-size:15px;font-weight:700;color:#1E293B">'+district_name+'</div>'
            '<div style="font-size:11px;color:#64748B">'+state_name+'</div>'
            '<div style="font-size:26px;font-weight:800;color:#1D4ED8;margin-top:4px;font-family:JetBrains Mono,monospace">'+f"{total:,}"+'</div>'
            '<div style="font-size:10px;color:#94A3B8;text-transform:uppercase;letter-spacing:.8px">industrial units</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if sel_row.get('matched_pc'):
            pc_c=get_party_color(sel_row.get('party',''))
            st.markdown(
                '<div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:12px;margin-bottom:10px">'
                '<div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">🗳 PC Details</div>'
                '<div style="font-weight:700;color:#15803D;font-size:13px">'+str(sel_row.get('pc_name',''))+'</div>'
                '<div style="font-size:12px;color:#1E293B;margin-top:4px">🏆 '+str(sel_row.get('winner',''))+'</div>'
                '<div style="font-size:11px;font-weight:600;color:'+pc_c+';margin-top:2px">'+str(sel_row.get('party',''))+'</div>'
                '<div style="font-size:10px;color:#64748B;margin-top:2px">Margin: '+str(sel_row.get('margin',0))+'</div>'
                '</div>',
                unsafe_allow_html=True
            )
        if sel_row['industries']:
            st.markdown('<div style="font-size:10px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid #E8ECF0">🏭 Top Industries</div>',unsafe_allow_html=True)
            top_inds=sorted(sel_row['industries'].items(),key=lambda x:-x[1])
            max_val=top_inds[0][1] if top_inds else 1
            for iname,cnt in top_inds[:8]:
                pct=cnt/max_val; c=ind_color_map.get(iname,'#3B82F6')
                short=iname[:24]+'…' if len(iname)>24 else iname
                st.markdown(
                    '<div style="margin-bottom:6px">'
                    '<div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px">'
                    '<span style="color:#374151">'+short+'</span>'
                    '<span style="color:'+c+';font-family:JetBrains Mono,monospace;font-weight:600">'+str(cnt)+'</span>'
                    '</div>'
                    '<div style="background:#F1F5F9;border-radius:3px;height:5px">'
                    '<div style="background:'+c+';width:'+str(int(pct*100))+'%;height:5px;border-radius:3px"></div>'
                    '</div></div>',
                    unsafe_allow_html=True
                )
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)

    # District list
    st.markdown('<div class="panel">',unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📋 Top Districts by Units</div>',unsafe_allow_html=True)
    for _,row in sorted_filtered.head(15).iterrows():
        is_pc=row.get('matched_pc',False)
        top_ind=max(row['industries'],key=row['industries'].get) if row['industries'] else '—'
        top_short=top_ind[:20]+'…' if len(top_ind)>20 else top_ind
        border='3px solid #22C55E' if is_pc else '1px solid #E8ECF0'
        bg='#F0FDF4' if is_pc else '#FFFFFF'
        party_html=''
        if is_pc:
            pc_c=get_party_color(row.get('party',''))
            party_html='<span style="font-size:9px;font-weight:700;color:'+pc_c+';background:'+pc_c+'22;padding:1px 6px;border-radius:10px">'+get_party_abbr(row.get('party',''))+'</span>'
        st.markdown(
            '<div style="background:'+bg+';border-left:'+border+';border-top:1px solid #E8ECF0;border-right:1px solid #E8ECF0;border-bottom:1px solid #E8ECF0;border-radius:8px;padding:8px 10px;margin-bottom:6px">'
            '<div style="display:flex;justify-content:space-between;align-items:flex-start">'
            '<div style="flex:1;min-width:0">'
            '<div style="font-weight:600;font-size:12px;color:#1E293B;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+str(row['district'])+'</div>'
            '<div style="color:#64748B;font-size:10px">'+str(row['state'])+'</div>'
            '<div style="color:#94A3B8;font-size:9.5px;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+top_short+'</div>'
            +party_html+
            '</div>'
            '<div style="text-align:right;flex-shrink:0;margin-left:6px">'
            '<div style="color:#1D4ED8;font-weight:700;font-size:13px;font-family:JetBrains Mono,monospace">'+f"{row['total_units']:,}"+'</div>'
            '<div style="color:#94A3B8;font-size:9px">units</div>'
            '</div></div></div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>',unsafe_allow_html=True)

# ── Bottom Tabs ──────────────────────────────────────────────────────────
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
tab1,tab2,tab3=st.tabs(["📊 Data Table","🗳 Principal Constituency Analysis","🏭 Industry Summary"])

with tab1:
    dcols=['state','district','lat','lon','total_units','matched_pc']
    if 'pc_name' in filtered.columns: dcols+=['pc_name','winner','party','margin']
    disp=filtered[dcols].copy(); disp.columns=[c.replace('_',' ').title() for c in dcols]
    disp=disp.sort_values('Total Units',ascending=False)
    ca,cb=st.columns([3,1])
    with cb: st.download_button("⬇️ Download CSV",disp.to_csv(index=False),"manufacturing_clusters.csv","text/csv")
    st.dataframe(disp,use_container_width=True,height=320)

with tab2:
    st.markdown("### 🗳 Principal Constituency Analysis")
    pc_df3=filtered[filtered['matched_pc']==True].copy() if 'matched_pc' in filtered.columns else pd.DataFrame()
    if len(pc_df3)>0 and 'party' in pc_df3.columns:
        ps=(pc_df3.groupby('party').agg(constituencies=('pc_name','count'),total_units=('total_units','sum'),avg_units=('total_units','mean')).reset_index().sort_values('total_units',ascending=False))
        pp1,pp2=st.columns(2)
        with pp1:
            st.markdown("**Party-wise Industrial Strength**")
            tot2=ps['total_units'].sum()
            for _,pr in ps.iterrows():
                c=get_party_color(pr['party']); pct=pr['total_units']/tot2 if tot2 else 0
                st.markdown(
                    '<div style="margin-bottom:10px">'
                    '<div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;align-items:center">'
                    '<span style="color:'+c+';font-weight:700">'+get_party_abbr(pr['party'])+'</span>'
                    '<span style="font-size:10px;color:#64748B">'+str(pr['party'])[:20]+'</span>'
                    '<span style="color:#1D4ED8;font-family:JetBrains Mono,monospace;font-size:11px">'+f"{int(pr['total_units']):,}"+'</span>'
                    '</div>'
                    '<div style="background:#F1F5F9;border-radius:3px;height:7px">'
                    '<div style="background:'+c+';width:'+str(int(pct*100))+'%;height:7px;border-radius:3px"></div>'
                    '</div>'
                    '<div style="color:#94A3B8;font-size:10px;margin-top:2px">'+str(int(pr['constituencies']))+' seats · avg '+f"{int(pr['avg_units']):,}"+'/seat</div>'
                    '</div>',unsafe_allow_html=True)
        with pp2:
            st.markdown("**Top Principal Constituencies**")
            for _,pr in pc_df3.sort_values('total_units',ascending=False).head(15).iterrows():
                c=get_party_color(pr.get('party',''))
                st.markdown(
                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;'
                    'padding:7px 10px;background:#FFFFFF;border-radius:8px;border-left:3px solid '+c+';'
                    'box-shadow:0 1px 3px rgba(0,0,0,0.05)">'
                    '<div><div style="font-size:12px;font-weight:600;color:#1E293B">'+str(pr.get('pc_name',''))+'</div>'
                    '<div style="font-size:10px;color:'+c+';font-weight:600">'+get_party_abbr(pr.get('party',''))+' · '+str(pr.get('state',''))+'</div></div>'
                    '<div style="color:#1D4ED8;font-weight:700;font-family:JetBrains Mono,monospace;font-size:13px">'+f"{pr['total_units']:,}"+'</div>'
                    '</div>',unsafe_allow_html=True)
    else:
        st.info("No Principal Constituency-matched districts in current filter.")

with tab3:
    st.markdown("### 🏭 Industry Sector Summary")
    ia={}
    for _,row in filtered.iterrows():
        for ind,cnt in row['industries'].items(): ia[ind]=ia.get(ind,0)+cnt
    isr=sorted(ia.items(),key=lambda x:-x[1]); ti=sum(v for _,v in isr)
    ci1,ci2=st.columns(2)
    with ci1:
        st.markdown("**All Industry Sectors**")
        for ind,cnt in isr:
            pct=cnt/ti if ti else 0; c=ind_color_map.get(ind,'#3B82F6')
            st.markdown(
                '<div style="margin-bottom:7px">'
                '<div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:2px">'
                '<span style="color:#1E293B;font-weight:500">'+str(ind[:38])+'</span>'
                '<span style="color:'+c+';font-family:JetBrains Mono,monospace;font-weight:700">'+f"{cnt:,}"+'</span>'
                '</div>'
                '<div style="background:#F1F5F9;border-radius:3px;height:5px">'
                '<div style="background:'+c+';width:'+str(int(pct*100))+'%;height:5px;border-radius:3px"></div>'
                '</div>'
                '<div style="color:#94A3B8;font-size:10px;margin-top:1px">'+f"{pct*100:.1f}"+'% of total</div>'
                '</div>',unsafe_allow_html=True)
    with ci2:
        st.markdown("**State-wise Distribution**")
        if sel_industry!='All Industries' and sel_state=='All States':
            sdf=filtered.copy(); sdf['su']=sdf['industries'].apply(lambda x:x.get(sel_industry,0))
            sg=sdf.groupby('state')['su'].sum().sort_values(ascending=False).head(20)
            mx=sg.max() if len(sg) else 1
            for state,val in sg.items():
                if val>0:
                    st.markdown(
                        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">'
                        '<div style="width:120px;font-size:11px;color:#374151;font-weight:500">'+str(state[:18])+'</div>'
                        '<div style="flex:1;background:#F1F5F9;border-radius:3px;height:6px">'
                        '<div style="background:#1D4ED8;width:'+str(int(val/mx*100))+'%;height:6px;border-radius:3px"></div>'
                        '</div>'
                        '<div style="font-size:11px;color:#1D4ED8;font-family:JetBrains Mono,monospace;width:40px;text-align:right">'+f"{val:,}"+'</div>'
                        '</div>',unsafe_allow_html=True)
        else:
            st.info("Select a specific Industry Sector to see state-wise distribution.")

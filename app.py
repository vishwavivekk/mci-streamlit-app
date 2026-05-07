import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

# ─── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Manufacturing Cluster Intelligence",
    page_icon="🏭",
    layout="wide"
)

# ─── CLEAN UI CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #F0F4F8;
    color: #1E293B;
}

/* remove header */
header, #MainMenu, footer {visibility:hidden;}
[data-testid="stToolbar"] {display:none;}

/* remove black code block */
pre, code, [data-testid="stCodeBlock"] {
    background:#F8FAFC !important;
    color:#1E293B !important;
    border:1px solid #E2E8F0;
    border-radius:8px;
}

/* header */
.dash-header {
    background: linear-gradient(135deg,#1E40AF,#2563EB);
    padding:16px;
    border-radius:12px;
    color:white;
    margin-bottom:12px;
}

/* card grid */
.card-grid {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:12px;
}

/* card */
.district-card {
    background:white;
    border:1px solid #E2E8F0;
    border-radius:12px;
    padding:14px;
    height:120px;
    box-shadow:0 2px 6px rgba(0,0,0,0.05);
}

.district-card:hover {
    box-shadow:0 6px 16px rgba(37,99,235,0.15);
}

.dc-title {font-size:14px;font-weight:700;}
.dc-sub {font-size:11px;color:#64748B;}
.dc-units {font-size:20px;font-weight:700;color:#2563EB;}
.dc-pc {
    font-size:11px;
    color:#059669;
    margin-top:4px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "Annexure_with_3digit_Sheet1_.csv"))
    df = df.iloc[1:].reset_index(drop=True)

    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    industry_cols = [c for c in df.columns if c not in ['State','District','Latitude','Longitude']]

    def safe(v):
        try:
            return int(float(str(v).replace(',','')))
        except:
            return 0

    records = []
    for _, r in df.iterrows():
        if pd.isna(r['Latitude']): continue
        industries = {c:safe(r[c]) for c in industry_cols if safe(r[c])>0}
        records.append({
            "state":r['State'],
            "district":r['District'],
            "lat":r['Latitude'],
            "lon":r['Longitude'],
            "total_units":sum(industries.values()),
            "industries":industries
        })

    df2 = pd.DataFrame(records)

    lok = pd.read_excel(os.path.join(BASE_DIR,"Lok_Sabha_Elections_Winners_2024.xlsx"))

    lok_dict = {}
    for _, r in lok.iterrows():
        lok_dict[str(r['PC Name']).upper()] = {
            "pc_name":r['PC Name'],
            "party":r['Winning Party']
        }

    for i, row in df2.iterrows():
        key = row['district'].upper()
        if key in lok_dict:
            df2.loc[i,'pc_name'] = lok_dict[key]['pc_name']
            df2.loc[i,'party'] = lok_dict[key]['party']
            df2.loc[i,'matched_pc'] = True
        else:
            df2.loc[i,'matched_pc'] = False

    return df2

df = load_data()

# ─── HEADER ─────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
<h3>🏭 Manufacturing Cluster Intelligence</h3>
<span>Lok Sabha × Industrial Units</span>
</div>
""", unsafe_allow_html=True)

# ─── MAP ─────────────────────────────────────────────
m = folium.Map(location=[22.5,80], zoom_start=5)

for _, r in df.iterrows():
    folium.CircleMarker(
        location=[r['lat'], r['lon']],
        radius=max(5, math.sqrt(r['total_units']+1)),
        color="#2563EB",
        fill=True,
        fill_opacity=0.7,
        popup=f"{r['district']} - {r['total_units']}"
    ).add_to(m)

st.markdown("#### 🗺️ Interactive Map")
st_folium(m, height=520)

# ─── DISTRICT CARDS ─────────────────────────────────────────────
st.markdown("## 📋 District Detail")
st.markdown("### 🏆 Top Districts by Units")

top_df = df.sort_values('total_units', ascending=False).head(12)

html = '<div class="card-grid">'

for _, r in top_df.iterrows():
    pc = r.get('pc_name','No PC Data')

    html += f"""
    <div class="district-card">
        <div class="dc-title">{r['district']}</div>
        <div class="dc-sub">{r['state']}</div>

        <div style="margin-top:6px">
            <div class="dc-units">{r['total_units']:,}</div>
            <div style="font-size:10px;color:#94A3B8">units</div>
        </div>

        <div class="dc-pc">{pc}</div>
    </div>
    """

html += "</div>"

st.markdown(html, unsafe_allow_html=True)

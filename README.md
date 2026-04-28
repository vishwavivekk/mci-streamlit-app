# 🏭 Manufacturing Cluster Intelligence
### Lok Sabha 2024 × Industrial Units — Interactive Analysis Dashboard

A Streamlit-based geo-intelligence dashboard that maps **India's industrial unit clusters** against **2024 Lok Sabha Parliamentary Constituencies**, enabling analysis of which industry clusters fall within which PC, their proximity, winning party, and election margins.

---

## 📦 Data Sources
| File | Description |
|------|-------------|
| `Annexure_with_3digit_Sheet1_.csv` | District-wise industrial units by NIC 3-digit sector (704 districts, 38 sectors) |
| `Lok_Sabha_Elections_Winners_2024.xlsx` | 2024 Lok Sabha election results — winners, parties, margins (293 PCs) |

---

## 🚀 Quick Start

### Local
```bash
git clone https://github.com/YOUR_USERNAME/manufacturing-cluster-intelligence
cd manufacturing-cluster-intelligence
pip install -r requirements.txt
streamlit run app.py
```

### Deploy on Streamlit Cloud
1. Push this repo to GitHub (include both data files)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → select `app.py` → Deploy

---

## ✨ Features

### 🗺️ Interactive Map
- **Units Count mode** — bubble size + color shows industrial density
- **Top Industry mode** — each district colored by its dominant sector
- **Winning Party mode** — PC-matched districts colored by winning party
- PC-matched districts highlighted with white border ring
- Click any marker for full district + PC popup

### 🔍 Filters
- State, Industry Sector, Winning Party
- Minimum units threshold slider
- PC Matched / Non-matched toggle

### 📍 Radius Search
- Enter any lat/lon as center point
- Slider for 10–300km radius
- Instantly filters map + results to districts within radius

### 📊 Analysis Tabs
- **Data Table** — filterable, downloadable CSV
- **PC Analysis** — party-wise industrial strength, top constituencies
- **Industry Summary** — all 38 sectors ranked, state-wise breakdown

---

## 🗂️ Project Structure
```
├── app.py                                  # Main Streamlit app
├── requirements.txt                        # Python dependencies
├── Annexure_with_3digit_Sheet1_.csv        # Units data
├── Lok_Sabha_Elections_Winners_2024.xlsx   # Election data
└── README.md
```

---

## 🔧 Configuration

All configuration is handled via the Streamlit sidebar. No environment variables required.

For Streamlit Cloud, create `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 50

[theme]
base = "dark"
primaryColor = "#00d4ff"
backgroundColor = "#0a0e1a"
secondaryBackgroundColor = "#111827"
textColor = "#e2e8f0"
```

---

## 📝 Notes
- 182 of 293 PC constituencies directly matched to district names
- Remaining districts shown on map but without PC election overlay
- Use Radius Search to find PCs near any industrial cluster
- Data reflects NIC 2008 classification (3-digit level)

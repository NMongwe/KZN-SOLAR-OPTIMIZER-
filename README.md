# ☀️ ModelForge Hub - KZN Solar Optimization Tool

**From Equation to Impact | University of Zululand**

Live Demo: https://kznsolaroptimizer.streamlit.app/
Logo: ![logo](logo.jpg)

### The Problem
Most solar calculators use national averages. In KZN, Durban is not Newcastle. A generic 32° tilt costs rural homes 12-18% yield. We built a town-specific optimizer for all 32 major KZN towns.

### What This App Does
1.  **Fetches Real NASA POWER Data:** Live call to NASA POWER API for `ALLSKY_SFC_SW_DWN`. 20-year climatology. Falls back to KZN average if offline.
2.  **Two Yield Models:** Max Yield (Adjustable) vs Realistic Yield (Fixed) corrected by `cos(fixed - optimal)` for cosine loss.
3.  **Inputs:** System size (kWp) and Performance Ratio (0.6-0.9)
4.  **Visuals:** NASA GHI chart, Optimal Tilt by month, Monthly Yield comparison

### Supported Towns (32 KZN Nodes)
Richards Bay, Empangeni, Eshowe, Nkandla, Ulundi, Nongoma, Pongola, Vryheid, Mkuze, Hluhluwe, Mtubatuba, St Lucia, Jozini, Durban, Pinetown, Umlazi, KwaDukuza, Ballito, Mandeni, Pietermaritzburg, Howick, Mooi River, Estcourt, Ladysmith, Newcastle, Dundee, Bergville, Underberg, Port Shepstone, Margate, Kokstad, Ixopo

### Physics Model
`tilt = |lat| + declination * 0.5` clamped 5°-45° | `monthly_kwh = GHI * days * system_kw * PR`

### Roadmap - The Hexagon System
V1.1: Solar Tilt + NASA (NOW - Node 1) | V1.2: Battery Sizing | V1.3: Prepaid Checker | V1.4: JoJo + Solar Hybrid

### Founders
**Ntusani Mongwe** - BSc in Applied Mathematics and Physics, University of Zululand | Model Development & App Architecture
**Nontando Tsewu** - BSc in Applied Mathematics and Computer Science, University of Zululand | Data & Validation, Nongoma Field Testing

### How to Run Locally
pip install -r requirements.txt
streamlit run app.py

© 2026 ModelForge Hub | Built by Ntusani Mongwe & Nontando Tsewu | University of Zululand
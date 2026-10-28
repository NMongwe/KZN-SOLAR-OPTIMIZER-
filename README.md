# ☀️ ModelForge Hub - KZN Solar Optimization Tool

**From Equation to Impact | Built by Ntusani & Nontando | University of Zululand**

Live Demo: https://kznsolaroptimizer.streamlit.app/
Logo: ![logo](logo.jpg)

### Why This Tool?
Most solar calculators use US/EU data. Wrong for KZN latitude. Homes in Richards Bay, Durban, and Nongoma need local tilt.

### Data Source: Real NASA Data
We use **NASA POWER API** (Prediction Of Worldwide Energy Resources)
- Parameter: `ALLSKY_SFC_SW_DWN` - All-Sky Surface Shortwave Downward Irradiance
- 20-year climatology (2001-2020)
- Free, no API key required: `https://power.larc.nasa.gov/api/temporal/climatology/point`
- Fallback to KZN average if offline

### Physics Model
Optimal Tilt = f(latitude, solar declination, month)
Formula: `tilt = |lat| + declination * 0.5` clamped to 5°-45° for Southern Hemisphere
Implemented in `app.py` -> `calc_optimal_tilt()`

### Locations Supported
- Richards Bay (-28.78, 32.09)
- Durban (-29.85, 31.02)
- Nongoma (Rural) (-27.89, 31.64) - our home test case
- Esikhaleni, Empangeni, Custom

### Stack
Python, Streamlit, Matplotlib, Requests, NASA POWER

### ModelForge Hub Roadmap
- V1.1: Solar Tilt + NASA (NOW)
- V1.2: Battery Sizing Calculator (Jan 2027)
- V1.3: Prepaid Checker (Feb 2027)
- V1.4: JoJo + Solar Hybrid (with first years)

### Founders
Ntusani - CS, Model Development 

Nontando - Data & Validation

### How to Run Locally
pip install -r requirements.txt
streamlit run app.py

Built for KZN, by KZN students.

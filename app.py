import streamlit as st
import requests
import math
import matplotlib.pyplot as plt

import streamlit as st

st.image("logo.jpg", width=350)  # or your logo name
st.title("KZN Solar Optimization - NASA POWER")

st.set_page_config(page_title="ModelForge Hub - KZN Solar", page_icon="☀️", layout="wide")

# Your KZN locations - add Nongoma!
LOCATIONS = {
    "Richards Bay": (-28.78, 32.09),
    "Durban": (-29.85, 31.02),
    "Nongoma (Rural)": (-27.89, 31.64),
    "Esikhaleni": (-28.83, 31.90),
    "Empangeni": (-28.72, 31.88),
    "Custom": (None, None)
}

def fetch_nasa_data(lat, lon):
    """Fetch real NASA irradiance data - no key needed"""
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        monthly = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        # monthly is dict JAN-DEC, values are kWh/m2/day
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        values = [monthly[m] for m in months]
        return values
    except:
        return None # will fallback

def calc_optimal_tilt(lat, month):
    # Physics: tilt = latitude +/- declination
    declinations = [-20.9,-13.0,-2.4,9.4,18.8,23.1,21.2,13.5,2.2,-9.6,-18.9,-23.0]
    tilt = abs(lat) + declinations[month] * 0.5  # simplified for Southern Hemisphere
    return max(5, min(45, tilt))

# UI
st.title("☀️ ModelForge Hub - KZN Solar Optimization")
st.caption("From Equation to Impact | By Ntusani & Nontando - UniZulu | Data: NASA POWER")

col1, col2 = st.columns([1,2])

with col1:
    loc_name = st.selectbox("Choose location", list(LOCATIONS.keys()))
    if loc_name == "Custom":
        lat = st.number_input("Latitude", -30.5, -27.0, -28.78)
        lon = st.number_input("Longitude", 30.5, 33.0, 32.09)
    else:
        lat, lon = LOCATIONS[loc_name]
    
    st.metric("Latitude", f"{lat:.2f}°")
    st.metric("Longitude", f"{lon:.2f}°")

    if st.button("Fetch NASA Data & Calculate", type="primary"):
        with st.spinner("Contacting NASA POWER..."):
            nasa_data = fetch_nasa_data(lat, lon)
        
        st.session_state['nasa'] = nasa_data
        st.session_state['lat'] = lat
        st.session_state['loc'] = loc_name

with col2:
    if 'nasa' in st.session_state:
        nasa = st.session_state['nasa']
        lat = st.session_state['lat']
        
        if nasa is None:
            st.warning("NASA offline - using estimated KZN average (5.2 kWh/m2/day). Try again on WiFi.")
            nasa = [5.8,5.9,5.5,4.8,4.2,3.9,4.0,4.6,5.2,5.6,5.7,5.9]
        else:
            st.success("Real NASA data loaded! 20-year climatology (2001-2020)")

        # Calculate tilt per month
        tilts = [calc_optimal_tilt(lat, i) for i in range(12)]
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        
        # Chart 1: NASA Irradiance
        fig, ax = plt.subplots()
        ax.bar(month_names, nasa, color="#FF6A00")
        ax.set_ylabel("Solar Energy (kWh/m2/day)")
        ax.set_title(f"NASA Real Data for {st.session_state['loc']}")
        st.pyplot(fig)

        # Chart 2: Tilt
        fig2, ax2 = plt.subplots()
        ax2.plot(month_names, tilts, marker='o', color="#0A1931", linewidth=3)
        ax2.set_ylabel("Optimal Tilt (°)")
        ax2.set_title("Optimal Panel Tilt by Month (Your Physics Model)")
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

        # Table
        st.dataframe({
            "Month": month_names,
            "NASA Sun (kWh/m2/day)": [f"{v:.2f}" for v in nasa],
            "Optimal Tilt (°)": [f"{t:.1f}" for t in tilts],
            "Est. Yield (x tilt gain)": [f"{v * (1+ (t-20)*0.005):.2f}" for v,t in zip(nasa, tilts)]
        })

        annual_tilt = sum(tilts)/12
        st.info(f"**Recommendation for {st.session_state['loc']}: Set fixed tilt at {annual_tilt:.1f}° facing North. Best months: Sep-Feb with {max(nasa):.1f} kWh/m2/day. Source: NASA POWER ALLSKY_SFC_SW_DWN**")
    else:
        st.info("👈 Select location and click to fetch real NASA data. Built for Nongoma, Richards Bay, Durban.")

st.divider()
st.caption("Data: NASA POWER Prediction Of Worldwide Energy Resources, Parameter ALLSKY_SFC_SW_DWN【2827723908692436784†L107-L109】. No API key required【2827723908692436784†L51-L53】. Model: ModelForge Hub V1.1 - From Equation to Impact.")

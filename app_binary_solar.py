import streamlit as st
import requests
import math
import matplotlib.pyplot as plt
import calendar

st.set_page_config(page_title="ModelForge - Binary Solar Model", layout="wide")

try:
    st.image("logo.jpg", width=120)
except:
    st.markdown("### 🌌 ModelForge")

st.title("🌌 ModelForge - KZN Binary Solar Model V1.1")
st.markdown("**App 2 of ModelForge Hub | What if KZN had two suns?**")
st.info("**Disclaimer:** Earth has ONE Sun. This is a hypothetical educational simulator using Stefan-Boltzmann Law L=4πR²σT⁴, inspired by real binary systems like Kepler-16b & Alpha Centauri. For teaching astrophysics + solar engineering.")

TOWNS = {
    "Richards Bay": (-28.78, 32.09), "Empangeni": (-28.76, 31.89), "Eshowe": (-28.89, 31.47),
    "Nkandla": (-28.62, 31.09), "Ulundi": (-28.34, 31.42), "Nongoma": (-27.89, 31.64),
    "Pongola": (-27.36, 31.61), "Vryheid": (-27.77, 30.79), "Mkuze": (-27.62, 32.03),
    "Hluhluwe": (-28.02, 32.27), "Mtubatuba": (-28.41, 32.18), "St Lucia": (-28.37, 32.41),
    "Jozini": (-27.43, 32.07), "Durban": (-29.85, 31.02), "Pinetown": (-29.82, 30.85),
    "Umlazi": (-29.96, 30.92), "KwaDukuza": (-29.35, 31.21), "Ballito": (-29.54, 31.21),
    "Mandeni": (-29.15, 31.39), "Pietermaritzburg": (-29.60, 30.38), "Howick": (-29.48, 30.22),
    "Mooi River": (-29.21, 29.99), "Estcourt": (-29.00, 29.87), "Ladysmith": (-28.55, 29.78),
    "Newcastle": (-27.75, 29.93), "Dundee": (-28.16, 30.23), "Bergville": (-28.72, 29.36),
    "Underberg": (-29.79, 29.49), "Port Shepstone": (-30.74, 30.45), "Margate": (-30.85, 30.37),
    "Kokstad": (-30.54, 29.42), "Ixopo": (-30.15, 30.06)
}

st.sidebar.header("System Config")
town = st.sidebar.selectbox("Select KZN Town (32 Nodes)", list(TOWNS.keys()), index=13)
system_kw = st.sidebar.slider("System Size (kWp)", 0.5, 10.0, 3.0)
pr = st.sidebar.slider("Performance Ratio", 0.6, 0.9, 0.75)

st.sidebar.markdown("---")
st.sidebar.header("🌌 Binary Star Config (App 2 Exclusive)")
companion = st.sidebar.selectbox("Companion Star Type", 
    ["None - Single Sun (Real Earth)", "Red Dwarf - 3000K", "Blue Giant - 15000K", "White Dwarf - 8000K", "Sun-like Twin - 5800K"])

ratios = {
    "None - Single Sun (Real Earth)": 0.0,
    "Red Dwarf - 3000K": 0.08,
    "Blue Giant - 15000K": 2.5,
    "White Dwarf - 8000K": 0.5,
    "Sun-like Twin - 5800K": 1.0
}
temps = {
    "None - Single Sun (Real Earth)": 5800,
    "Red Dwarf - 3000K": 3000,
    "Blue Giant - 15000K": 15000,
    "White Dwarf - 8000K": 8000,
    "Sun-like Twin - 5800K": 5800
}
l_ratio = ratios[companion]
T_comp = temps[companion]

def get_nasa_ghi(lat, lon):
    try:
        url = f"https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude={lon}&latitude={lat}&format=JSON"
        r = requests.get(url, timeout=10).json()
        data = r["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        monthly = [data[m] for m in ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]]
        return monthly
    except:
        return [5.8, 5.6, 5.2, 4.6, 4.0, 3.7, 3.9, 4.5, 5.1, 5.5, 5.7, 5.9]

def calc_optimal_tilt(lat, month_idx):
    declinations = [-20.9,-13.0,-2.4,9.4,18.8,23.1,21.2,13.5,2.2,-9.6,-18.9,-23.0]
    tilt = abs(lat) + declinations[month_idx] * 0.5
    # Binary shift: second sun pulls optimal toward equator slightly
    if l_ratio > 0:
        tilt = tilt - (l_ratio * 2)  # Blue giant pulls -5°, Red dwarf -0.16°
    return max(5, min(45, tilt))

lat, lon = TOWNS[town]
monthly_ghi_single = get_nasa_ghi(lat, lon)
monthly_ghi_binary = [g * (1 + l_ratio * 0.3) for g in monthly_ghi_single]

months = list(calendar.month_abbr)[1:]
tilts_single = [abs(lat) + d*0.5 for d in [-20.9,-13.0,-2.4,9.4,18.8,23.1,21.2,13.5,2.2,-9.6,-18.9,-23.0]]
tilts_single = [max(5,min(45,t)) for t in tilts_single]
tilts_binary = [calc_optimal_tilt(lat, i) for i in range(12)]

monthly_yield_single = []
monthly_yield_binary = []
for i in range(12):
    days = [31,28,31,30,31,30,31,31,30,31,30,31][i]
    monthly_yield_single.append(monthly_ghi_single[i] * days * system_kw * pr)
    monthly_yield_binary.append(monthly_ghi_binary[i] * days * system_kw * pr)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Town", town)
col2.metric("Real GHI Avg", f"{sum(monthly_ghi_single)/12:.2f} kWh")
col3.metric(f"Binary GHI Avg ({companion})", f"{sum(monthly_ghi_binary)/12:.2f} kWh", f"+{l_ratio*30:.0f}%")
col4.metric("Stefan-Boltzmann", f"L ∝ {T_comp}⁴")

# Charts
fig, ax = plt.subplots(2, 1, figsize=(11, 8))

ax[0].plot(months, monthly_ghi_single, marker='o', linestyle='--', linewidth=2, label='Single Sun - Real Earth (NASA)')
ax[0].plot(months, monthly_ghi_binary, marker='s', linewidth=2, label=f'Binary - {companion}')
ax[0].set_title(f"GHI Comparison: Single vs Binary Sun for {town} | L=4πR²σT⁴")
ax[0].set_ylabel("GHI kWh/m²/day")
ax[0].legend()
ax[0].grid(True)

ax[1].plot(months, tilts_single, marker='o', linestyle='--', label='Single Sun Optimal Tilt')
ax[1].plot(months, tilts_binary, marker='s', label=f'Binary Optimal Tilt ({companion})')
ax[1].set_title("Optimal Tilt Shift - Two Suns Pull Tilt Toward Barycenter")
ax[1].set_ylabel("Tilt °")
ax[1].set_xlabel("Month")
ax[1].legend()
ax[1].grid(True)

st.pyplot(fig)

st.markdown("### 📊 System Sizing Impact")
annual_single = sum(monthly_yield_single)
annual_binary = sum(monthly_yield_binary)
col_a, col_b = st.columns(2)
col_a.metric("Annual Yield Single Sun", f"{annual_single:.0f} kWh")
col_b.metric("Annual Yield Binary Sun", f"{annual_binary:.0f} kWh", f"+{annual_binary-annual_single:.0f} kWh")

st.markdown("---")
st.markdown("**Equation:** `GHI_binary = GHI_NASA * (1 + 0.3 * L_comp/L_sun)` where `L ∝ T⁴` | **Barycenter Shift:** `tilt_binary = tilt_single - 2*L_ratio`")
st.markdown("© 2026 ModelForge Hub | App 2 - Binary Solar Model | Built by Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS) | UniZulu")
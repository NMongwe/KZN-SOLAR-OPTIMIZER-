import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
import math

st.set_page_config(page_title="ModelForge Hub - KZN Solar", page_icon="☀️", layout="wide")

try:
    st.image("logo.jpg", width=350)
except:
    pass

st.title("☀️ ModelForge Hub - KZN Solar Optimization")
st.caption("From Equation to Impact | By Ntusani & Nontando - UniZulu | Data: NASA POWER")

KZN_TOWNS = {
    "Richards Bay": (-28.7807, 32.0383), "Empangeni": (-28.7672, 31.8927),
    "Eshowe": (-28.8946, 31.4637), "Nkandla": (-28.6270, 31.0898),
    "Ulundi": (-28.3351, 31.4162), "Nongoma": (-27.8900, 31.6461),
    "Pongola": (-27.3638, 31.6211), "Vryheid": (-27.7692, 30.7912),
    "Mkuze": (-27.6249, 32.0314), "Hluhluwe": (-28.0207, 32.2676),
    "Mtubatuba": (-28.3593, 32.1847), "St Lucia": (-28.3813, 32.4194),
    "Jozini": (-27.4320, 32.0687), "Durban": (-29.8587, 31.0218),
    "Pinetown": (-29.8211, 30.8669), "Umlazi": (-29.9663, 30.9007),
    "KwaDukuza (Stanger)": (-29.3568, 31.2354), "Ballito": (-29.5391, 31.2136),
    "Mandeni": (-29.1593, 31.3938), "Pietermaritzburg": (-29.6006, 30.3794),
    "Howick": (-29.4789, 30.2178), "Mooi River": (-29.2081, 30.0024),
    "Estcourt": (-28.9973, 29.8757), "Ladysmith": (-28.5597, 29.7803),
    "Newcastle": (-27.7573, 29.9318), "Dundee": (-28.1643, 30.2344),
    "Bergville": (-28.7289, 29.3608), "Underberg": (-29.7929, 29.4992),
    "Port Shepstone": (-30.7415, 30.4439), "Margate": (-30.8577, 30.3688),
    "Kokstad": (-30.5478, 29.4255), "Ixopo": (-30.1585, 30.0608),
}

def fetch_nasa_data(lat, lon):
    url = f"https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {"parameters": "ALLSKY_SFC_SW_DWN", "community": "RE", "longitude": lon, "latitude": lat, "format": "JSON"}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        monthly = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        values = [monthly[m] for m in months]
        return values
    except:
        return None

def calc_optimal_tilt(lat, month):
    declinations = [-20.9,-13.0,-2.4,9.4,18.8,23.1,21.2,13.5,2.2,-9.6,-18.9,-23.0]
    tilt = abs(lat) + declinations[month] * 0.5
    return max(5, min(45, tilt))

# --- SIDEBAR ---
with st.sidebar:
    town = st.selectbox("📍 Select KZN Town", sorted(KZN_TOWNS.keys()), index=sorted(KZN_TOWNS.keys()).index("Nongoma") if "Nongoma" in KZN_TOWNS else 0)
    lat, lon = KZN_TOWNS[town]
    st.caption(f"Using NASA POWER data for {town} ({lat}, {lon})")
    system_kw = st.number_input("System Size (kWp)", value=5.0, min_value=1.0, max_value=100.0)
    pr = st.slider("Performance Ratio (losses)", 0.6, 0.9, 0.8)

col1, col2 = st.columns([1,2])

with col1:
    st.metric("Latitude", f"{lat:.2f}°")
    st.metric("Longitude", f"{lon:.2f}°")
    if st.button("Fetch NASA Data & Calculate", type="primary"):
        with st.spinner(f"Contacting NASA for {town}..."):
            nasa_data = fetch_nasa_data(lat, lon)
        st.session_state['nasa'] = nasa_data
        st.session_state['lat'] = lat
        st.session_state['loc'] = town

with col2:
    if 'nasa' in st.session_state:
        nasa = st.session_state['nasa']
        lat_s = st.session_state['lat']

        if nasa is None:
            st.warning("NASA offline - using KZN average")
            nasa = [5.8,5.9,5.5,4.8,4.2,3.9,4.0,4.6,5.2,5.6,5.7,5.9]
        else:
            st.success(f"Real NASA data loaded for {st.session_state['loc']}!")

        tilts = [calc_optimal_tilt(lat_s, i) for i in range(12)]
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]

        # === YEARLY CALC - BOTH FIXED AND ADJUSTABLE ===
        monthly_kwh_optimal = [ghi * days * system_kw * pr for ghi, days in zip(nasa, days_in_month)]
        yearly_optimal = sum(monthly_kwh_optimal)
        
        # Fixed tilt is average of all tilts
        fixed_tilt = sum(tilts)/12
        # Cosine loss if fixed vs optimal each month
        monthly_kwh_fixed = [
            ghi * days * system_kw * pr * math.cos(math.radians(fixed_tilt - opt_tilt))
            for ghi, days, opt_tilt in zip(nasa, days_in_month, tilts)
        ]
        yearly_fixed = sum(monthly_kwh_fixed)
        loss_pct = (yearly_optimal - yearly_fixed) / yearly_optimal * 100

        # Two metrics side by side
        m1, m2 = st.columns(2)
        m1.metric(f"Max Yield (Adjust Monthly)", f"{yearly_optimal:,.0f} kWh/year", f"{yearly_optimal/12:,.0f} /month avg")
        m2.metric(f"Realistic Yield (Fixed {fixed_tilt:.1f}°)", f"{yearly_fixed:,.0f} kWh/year", f"-{loss_pct:.1f}% vs adjustable", delta_color="off")

        st.caption(f"ℹ️ You caught it: Adjustable = if you re-tilt every month. Fixed = one angle on roof forever (realistic). Difference is cosine loss.")

        fig, ax = plt.subplots()
        ax.bar(month_names, nasa, color="#FF6A00")
        ax.set_ylabel("kWh/m2/day")
        ax.set_title(f"NASA Irradiance - {st.session_state['loc']}")
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.plot(month_names, tilts, marker='o', color="#0A1931", linewidth=3)
        ax2.axhline(fixed_tilt, linestyle='--', color='red', label=f'Fixed Avg {fixed_tilt:.1f}°')
        ax2.set_ylabel("Optimal Tilt (°)")
        ax2.set_title("Optimal Tilt by Month")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

        fig3, ax3 = plt.subplots()
        ax3.bar(month_names, monthly_kwh_optimal, color="#2E8B57", alpha=0.6, label="Optimal Tilt")
        ax3.bar(month_names, monthly_kwh_fixed, color="#0A1931", alpha=0.9, label=f"Fixed {fixed_tilt:.1f}°")
        ax3.set_ylabel("kWh")
        ax3.set_title(f"Monthly Yield: Optimal vs Fixed ({system_kw}kWp)")
        ax3.legend()
        st.pyplot(fig3)

        st.dataframe({
            "Month": month_names,
            "GHI (kWh/m2/day)": [f"{v:.2f}" for v in nasa],
            "Optimal Tilt (°)": [f"{t:.1f}" for t in tilts],
            "Optimal kWh": [f"{k:.0f}" for k in monthly_kwh_optimal],
            f"Fixed {fixed_tilt:.1f}° kWh": [f"{k:.0f}" for k in monthly_kwh_fixed]
        })

        st.info(f"Recommendation: Fixed tilt {fixed_tilt:.1f}° facing North for {st.session_state['loc']}. Fixed Yield: {yearly_fixed:,.0f} kWh/year | Max if adjustable: {yearly_optimal:,.0f} kWh/year")
    else:
        st.info("👈 Select town in sidebar and click Calculate. Built for all KZN towns.")

st.divider()
st.caption("Data: NASA POWER ALLSKY_SFC_SW_DWN. ModelForge Hub V1.3 | Fixed tilt uses cos(fixed-optimal) correction") 
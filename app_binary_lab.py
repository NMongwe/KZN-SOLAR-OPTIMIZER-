import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ModelForge - Binary Stars Lab V2.0",
    page_icon="🪐",
    layout="wide"
)

# --- HEADER ---
col1, col2 = st.columns([1, 5])
with col1:
    try:
        st.image("logo.jpg", width=350)
    except:
        st.markdown("### 🪐")
with col2:
    st.title("ModelForge Hub - Binary Stars Lab V2.2")
    st.markdown("** | Kepler + Barycenter + Habitable Zone | Nongoma Home Edition - Whole SA**")

st.warning("⚠️ **HYPOTHETICAL:** Real SA has ONE Sun. This is a theoretical Binary System Lab for Applied Maths & Physics (UniZulu).")

# --- WHOLE SOUTH AFRICA TOWNS ---
sa_towns = {
    "Nongoma": (-27.89, 31.64, 4.85, "KZN"),
    "Ulundi": (-28.35, 31.42, 4.74, "KZN"),
    "Durban": (-29.85, 31.02, 4.65, "KZN"),
    "Pietermaritzburg": (-29.60, 30.38, 4.80, "KZN"),
    "Newcastle": (-27.75, 29.93, 5.10, "KZN"),
    "Richards Bay": (-28.78, 32.09, 4.70, "KZN"),
    "Ladysmith": (-28.55, 29.78, 5.05, "KZN"),
    "Vryheid": (-27.77, 30.79, 5.00, "KZN"),
    "Hluhluwe": (-28.02, 32.27, 4.75, "KZN"),
    "Mtubatuba": (-28.43, 32.19, 4.72, "KZN"),
    "Empangeni": (-28.75, 31.90, 4.68, "KZN"),
    "Eshowe": (-28.89, 31.46, 4.60, "KZN"),
    "Port Shepstone": (-30.74, 30.45, 4.55, "KZN"),
    "Kokstad": (-30.55, 29.42, 4.90, "KZN"),
    "Underberg": (-29.79, 29.49, 5.15, "KZN"),
    "Mkuze": (-27.62, 32.03, 4.85, "KZN"),
    "Jozini": (-27.43, 32.06, 4.90, "KZN"),
    "Pongola": (-27.36, 31.61, 4.95, "KZN"),
    # SA MAJORS
    "Upington": (-28.45, 21.24, 6.20, "Northern Cape"),
    "De Aar": (-30.64, 24.01, 5.90, "Northern Cape"),
    "Kimberley": (-28.72, 24.76, 5.80, "Northern Cape"),
    "Johannesburg": (-26.20, 28.04, 5.20, "Gauteng"),
    "Pretoria": (-25.74, 28.22, 5.25, "Gauteng"),
    "Polokwane": (-23.90, 29.45, 5.50, "Limpopo"),
    "Nelspruit": (-25.47, 30.96, 5.10, "Mpumalanga"),
    "Bloemfontein": (-29.08, 26.15, 5.60, "Free State"),
    "Cape Town": (-33.92, 18.42, 5.40, "Western Cape"),
    "Gqeberha (PE)": (-33.96, 25.60, 4.90, "Eastern Cape"),
    "East London": (-33.01, 27.90, 4.75, "Eastern Cape"),
}

# --- SIDEBAR ---
st.sidebar.header("🌟 Binary Star Controls")
st.sidebar.subheader("Star 1 - Primary")
M1 = st.sidebar.slider("Mass M1 (Msun)", 0.5, 3.0, 1.0, 0.1)
T1 = st.sidebar.slider("Temp T1 (K)", 3000, 10000, 5778, 100)
R1 = st.sidebar.slider("Radius R1 (Rsun)", 0.5, 5.0, 1.0, 0.1)

st.sidebar.subheader("Star 2 - Companion")
star_types = {
    "Red Dwarf (3000K, 0.3 Msun)": (0.3, 3000, 0.5),
    "Yellow Sun (5778K, 1.0 Msun)": (1.0, 5778, 1.0),
    "Blue Giant (15000K, 5.0 Msun)": (5.0, 15000, 3.0),
    "Blue Extreme (30000K, 10 Msun)": (10.0, 30000, 5.0)
}
choice = st.sidebar.selectbox("Preset Companion", list(star_types.keys()), index=2)
M2_preset, T2_preset, R2_preset = star_types[choice]

M2 = st.sidebar.slider("Mass M2 (Msun)", 0.1, 10.0, M2_preset, 0.1)
T2 = st.sidebar.slider("Temp T2 (K)", 3000, 30000, T2_preset, 100)
R2 = st.sidebar.slider("Radius R2 (Rsun)", 0.1, 8.0, R2_preset, 0.1)

st.sidebar.subheader("Orbit")
a = st.sidebar.slider("Semi-major axis a (AU)", 0.5, 10.0, 2.0, 0.1)
e = st.sidebar.slider("Eccentricity e", 0.0, 0.8, 0.3, 0.05)
planet_dist = st.sidebar.slider("Planet Distance (AU)", 0.5, 5.0, 1.0, 0.1)

# --- LOCATION SELECTOR ---
st.subheader("📍 Select SA Location for Impact Study")
c_loc1, c_loc2 = st.columns([1,2])
with c_loc1:
    region_filter = st.radio("Filter", ["Whole South Africa", "KZN Only", " Nongoma & Neighbours", "High GHI Belt (>5.5)"], index=0)
    if region_filter == "KZN Only":
        town_list = [k for k,v in sa_towns.items() if "KZN" in v[3]]
    elif region_filter == " Nongoma & Neighbours":
        town_list = ["Nongoma ", "Ulundi", "Vryheid", "Pongola", "Mkuze", "Hluhluwe", "Mtubatuba"]
    elif region_filter == "High GHI Belt (>5.5)":
        town_list = [k for k,v in sa_towns.items() if v[2] >= 5.5]
    else:
        town_list = list(sa_towns.keys())
    # Default to Nongoma
    default_index = 0
    if "Nongoma " in town_list:
        default_index = town_list.index("Nongoma")
    town = st.selectbox("Town/City", town_list, index=default_index)

with c_loc2:
    lat, lon, ghi_real, province = sa_towns[town]
    if "HOME" in town:
        st.success(f"**{town}** | {province} | Lat {lat}, Lon {lon} | NASA GHI **{ghi_real} kWh/m²/day** | **Nongoma TOWN - Zululand**")
    else:
        st.info(f"**{town}** | {province} | Lat {lat}, Lon {lon} | NASA GHI **{ghi_real} kWh/m²/day**")

# --- PHYSICS ---
T_sun = 5778
def luminosity(R, T):
    return (R**2) * ((T / T_sun)**4)

L1 = luminosity(R1, T1)
L2 = luminosity(R2, T2)
L_total = L1 + L2

M_total = M1 + M2
r1 = a * M2 / M_total
r2 = a * M1 / M_total

P = math.sqrt((a**3) / M_total)
P_days = P * 365.25

HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67

stable_limit = a * 2.5
is_stable = planet_dist > stable_limit
is_habitable = HZ_inner <= planet_dist <= HZ_outer

yield_single = ghi_real * 365 * 0.18 * 5.5
yield_binary = yield_single * (1 + 0.3 * L2)

# --- METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total L", f"{L_total:.2f} L☉", f"L2={L2:.2f}")
c2.metric("Period P", f"{P_days:.1f} days", f"P²=a³/M")
c3.metric("Barycenter", f"r1={r1:.2f}, r2={r2:.2f} AU", f"M={M_total}")
c4.metric(f"{town} Yield", f"{yield_binary:.0f} kWh/yr", f"+{yield_binary-yield_single:.0f} vs single")

# --- GRAPHS ---
left, right = st.columns(2)

with left:
    st.subheader(f"🪐 Orbit + HZ | {town}")
    st.latex(r"P^2 = \frac{a^3}{M_1+M_2} \quad | \quad L \propto R^2T^4")
    
    fig, ax = plt.subplots(figsize=(6,6))
    ax.plot(0,0,'k+', markersize=15, label="Barycenter")
    
    theta = np.linspace(0, 2*np.pi, 200)
    x1_orbit = -r1 * np.cos(theta)
    y1_orbit = -r1 * np.sin(theta) * np.sqrt(1-e**2)
    x2_orbit = r2 * np.cos(theta)
    y2_orbit = r2 * np.sin(theta) * np.sqrt(1-e**2)
    
    ax.plot(x1_orbit, y1_orbit, 'y--', alpha=0.5)
    ax.plot(x2_orbit, y2_orbit, 'b--', alpha=0.5)
    ax.plot(x1_orbit[0], y1_orbit[0], 'yo', markersize=18, label=f"S1 {T1}K")
    ax.plot(x2_orbit[0], y2_orbit[0], 'bo', markersize=18*(R2/R1 if R2/R1<2 else 2), label=f"S2 {T2}K")
    
    planet_theta = np.linspace(0, 2*np.pi, 200)
    planet_x = planet_dist * np.cos(planet_theta)
    planet_y = planet_dist * np.sin(planet_theta) * 0.9
    color = 'green' if is_stable and is_habitable else 'orange' if is_stable else 'red'
    ax.plot(planet_x, planet_y, color=color, linewidth=2, label=f"Planet {planet_dist} AU")
    
    ax.add_artist(plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':', label=f"HZ {HZ_inner:.2f} AU"))
    ax.add_artist(plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--', label=f"HZ {HZ_outer:.2f} AU"))
    
    ax.set_aspect('equal')
    ax.set_xlabel("AU")
    ax.set_ylabel("AU")
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title(f"a={a} AU e={e} | {town}")
    st.pyplot(fig)

with right:
    st.subheader("📊 SA GHI Ranking")
    
    fig2, ax2 = plt.subplots(figsize=(8,4.5))
    sorted_towns = sorted(sa_towns.items(), key=lambda x: x[1][2])
    names = [k.replace(" Nongoma","") for k,_ in sorted_towns]
    ghs = [v[2] for _,v in sorted_towns]
    colors = ['red' if 'Nongoma' in k else 'gold' if 'KZN' in v[3] else 'dodgerblue' if v[2]>=5.5 else 'gray' for k,v in sorted_towns]
    ax2.barh(names, ghs, color=colors)
    ax2.set_xlabel("GHI kWh/m2/day")
    ax2.axvline(ghi_real, color='red', linestyle='--', label=f"Selected {town}")
    ax2.legend(fontsize=8)
    ax2.set_title("Red=Nongoma , Gold=KZN, Blue=High-GHI >5.5")
    st.pyplot(fig2)
    
    st.subheader(f"📐 Impact for {town}")
    st.write(f"""
    - **Real Single Sun:** {ghi_real} kWh → **{yield_single:.0f} kWh/yr** (5.5kWp)
    - **Binary {T2}K Companion:** L2={L2:.2f} Lsun
    - **Binary Yield:** **{yield_binary:.0f} kWh/yr** (+{((yield_binary/yield_single)-1)*100:.0f}%)
    """)
    
    if "Nongoma" in town:
        st.success(f" **Nongoma :** {yield_single:.0f} kWh real → {yield_binary:.0f} kWh binary! Zululand shines!")
    
    if is_stable:
        st.success(f"✅ Stable: {planet_dist} AU > {stable_limit:.1f} AU")
    else:
        st.error(f"❌ Unstable: {planet_dist} AU < {stable_limit:.1f} AU")
    
    if is_habitable:
        st.success(f"✅ Habitable Zone: {HZ_inner:.2f}-{HZ_outer:.2f} AU")
    else:
        st.warning(f"⚠️ Outside HZ. Go to {HZ_inner:.2f}-{HZ_outer:.2f} AU")

# --- FOOTER WITH NAMES & LICENSE ---
st.divider()
st.markdown("### 🧮 Core Equations")
st.latex(r"L \propto R^2T^4 \quad | \quad P^2 = \frac{a^3}{M_1+M_2} \quad | \quad r_b = a\frac{M_2}{M_1+M_2}")

st.markdown("---")
st.markdown("""
### 👥 Authors & License

- **Ntusani Mongwe** — Applied Mathematics & Physics (UniZulu) — Founder, ModelForge Hub — 
- **Nontando Tsewu** — Applied Mathematics & Computer Science (UniZulu) — Co-Developer

**© 2026 ModelForge Hub. All Rights Reserved.**

**Licensed under MIT License** — Open for education & research. Commercial use with attribution.

**Contact:** ModelForge Hub | University of Zululand | KwaDlangezwa

**Acknowledgement:** NASA POWER GHI Data | Zululand District 

*From Equation to Impact*
""")
st.caption("App 3 - Binary Stars V2.0| 2026")
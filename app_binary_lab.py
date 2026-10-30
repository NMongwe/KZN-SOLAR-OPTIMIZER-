import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ModelForge - Binary Star Lab V2.0",
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
    st.title("ModelForge Hub - Binary Star Lab V2.0")
    st.markdown("**| Kepler + Barycenter + Habitable Zone | KZN Dual-Sun Simulation**")

st.warning("⚠️ **HYPOTHETICAL SIMULATION:** Real KZN has ONE Sun. This is a theoretical Binary System Lab for Applied Maths & Physics (UniZulu). Not NASA official data.")

# --- SIDEBAR - STAR CONTROLS ---
st.sidebar.header("🌟 Binary Star Controls")

st.sidebar.subheader("Star 1 - Primary (Yellow Sun)")
M1 = st.sidebar.slider("Mass M1 (Solar Mass)", 0.5, 3.0, 1.0, 0.1)
T1 = st.sidebar.slider("Temp T1 (K)", 3000, 10000, 5778, 100)
R1 = st.sidebar.slider("Radius R1 (Solar Radius)", 0.5, 5.0, 1.0, 0.1)

st.sidebar.subheader("Star 2 - Companion")
star_types = {
    "Red Dwarf (3000K, 0.3 Msun)": (0.3, 3000, 0.5),
    "Yellow Sun (5778K, 1.0 Msun)": (1.0, 5778, 1.0),
    "Blue Giant (15000K, 5.0 Msun)": (5.0, 15000, 3.0),
    "Blue Giant Extreme (30000K, 10 Msun)": (10.0, 30000, 5.0)
}
choice = st.sidebar.selectbox("Preset Companion", list(star_types.keys()), index=2)
M2_preset, T2_preset, R2_preset = star_types[choice]

M2 = st.sidebar.slider("Mass M2 (Solar Mass)", 0.1, 10.0, M2_preset, 0.1)
T2 = st.sidebar.slider("Temp T2 (K)", 3000, 30000, T2_preset, 100)
R2 = st.sidebar.slider("Radius R2 (Solar Radius)", 0.1, 8.0, R2_preset, 0.1)

st.sidebar.subheader("Orbit")
a = st.sidebar.slider("Semi-major axis a (AU)", 0.5, 10.0, 2.0, 0.1) # distance between stars
e = st.sidebar.slider("Eccentricity e", 0.0, 0.8, 0.3, 0.05)
planet_dist = st.sidebar.slider("Planet Distance from Barycenter (AU)", 0.5, 5.0, 1.0, 0.1)

# --- PHYSICS CALCULATIONS ---
# Stefan-Boltzmann: L = 4πR²σT⁴ => L/L_sun = (R/R_sun)² * (T/T_sun)⁴
T_sun = 5778
def luminosity(R, T):
    return (R**2) * ((T / T_sun)**4)

L1 = luminosity(R1, T1)
L2 = luminosity(R2, T2)
L_total = L1 + L2

# Barycenter: r1 = a * M2/(M1+M2), r2 = a * M1/(M1+M2)
M_total = M1 + M2
r1 = a * M2 / M_total
r2 = a * M1 / M_total

# Kepler's Third Law: P² = a³ / (M1+M2) where P in years, a in AU, M in Msun
P = math.sqrt((a**3) / M_total) # orbital period in years
P_days = P * 365.25

# Habitable Zone: approx sqrt(L) * (0.95 to 1.67 AU for Sun)
# For binary, use L_total
HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67

# Stability: Planet is stable if > 2-3 * a (P-type) - simplified
stable_limit = a * 2.5
is_stable = planet_dist > stable_limit
is_habitable = HZ_inner <= planet_dist <= HZ_outer

# --- TOP METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Luminosity", f"{L_total:.2f} L☉", f"L1={L1:.2f}, L2={L2:.2f}")
c2.metric("Orbital Period P", f"{P_days:.1f} days", f"{P:.2f} yrs | Kepler P²=a³/M")
c3.metric("Barycenter", f"r1={r1:.2f} AU, r2={r2:.2f} AU", f"M1+M2={M_total} Msun")
c4.metric("Habitable Zone", f"{HZ_inner:.2f} - {HZ_outer:.2f} AU", f"Planet at {planet_dist} AU")

# --- ROW 1: ORBIT ANIMATION + LUMINOSITY ---
left, right = st.columns(2)

with left:
    st.subheader(f"🪐 Binary Orbit | L ∝ R²T⁴")
    st.latex(r"L = 4\pi R^2 \sigma T^4 \quad | \quad P^2 = \frac{a^3}{M_1+M_2}")
    
    fig, ax = plt.subplots(figsize=(6,6))
    # Barycenter at 0,0
    ax.plot(0,0,'k+', markersize=15, label="Barycenter")
    
    # Orbit ellipses
    theta = np.linspace(0, 2*np.pi, 200)
    # Star 1 orbit around barycenter
    x1_orbit = -r1 * np.cos(theta) * (1) # simplified circular for visualization, eccentricity for distance
    y1_orbit = -r1 * np.sin(theta) * np.sqrt(1-e**2)
    # Star 2 orbit
    x2_orbit = r2 * np.cos(theta)
    y2_orbit = r2 * np.sin(theta) * np.sqrt(1-e**2)
    
    ax.plot(x1_orbit, y1_orbit, 'y--', alpha=0.5, label=f"Star1 M1={M1}")
    ax.plot(x2_orbit, y2_orbit, 'b--', alpha=0.5, label=f"Star2 M2={M2}")
    
    # Current positions
    ax.plot(x1_orbit[0], y1_orbit[0], 'yo', markersize=20, label=f"Star1 {T1}K")
    ax.plot(x2_orbit[0], y2_orbit[0], 'bo', markersize=20* (R2/R1), label=f"Star2 {T2}K")
    
    # Planet orbit
    planet_theta = np.linspace(0, 2*np.pi, 200)
    planet_x = planet_dist * np.cos(planet_theta)
    planet_y = planet_dist * np.sin(planet_theta) * 0.9
    color = 'green' if is_stable and is_habitable else 'orange' if is_stable else 'red'
    ax.plot(planet_x, planet_y, color=color, linestyle='-', linewidth=2, label=f"Planet at {planet_dist} AU")
    
    # Habitable zone
    hz_inner_circle = plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':', label=f"HZ Inner {HZ_inner:.2f} AU")
    hz_outer_circle = plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--', label=f"HZ Outer {HZ_outer:.2f} AU")
    ax.add_artist(hz_inner_circle)
    ax.add_artist(hz_outer_circle)
    
    ax.set_aspect('equal')
    ax.set_xlabel("AU")
    ax.set_ylabel("AU")
    ax.legend(fontsize=7, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Binary System: a={a} AU, e={e} | Planet {'STABLE & HABITABLE' if is_stable and is_habitable else 'UNSTABLE' if not is_stable else 'STABLE but not HZ'}")
    st.pyplot(fig)

with right:
    st.subheader("📊 Stefan-Boltzmann Luminosity Comparison")
    
    fig2, ax2 = plt.subplots()
    stars = ['Star 1\n(Yellow)', 'Star 2\n(Blue/Red)', 'Total Binary']
    lum = [L1, L2, L_total]
    colors = ['gold', 'dodgerblue', 'orangered']
    ax2.bar(stars, lum, color=colors)
    ax2.set_ylabel("Luminosity (L_sun)")
    ax2.set_title(f"L1={L1:.2f}, L2={L2:.2f} | L ∝ T⁴ => {T2}K is {(T2/T_sun)**4:.1f}x Sun")
    for i, v in enumerate(lum):
        ax2.text(i, v+0.1, f"{v:.2f}", ha='center')
    st.pyplot(fig2)
    
    st.subheader("📐 System Sizing Impact for KZN")
    st.write(f"""
    **If this binary was over Ulundi (4.74 kWh baseline):**
    - Real Sun yield: **3885 kWh/year**
    - Binary boost factor: **{L_total:.2f}x**
    - With 0.3x scaling for realism: **{3885 * (1+0.3*(L2/1)):.0f} kWh** (+{0.3*L2/1*100:.0f}%)
    - Tilt shift toward barycenter: **{-2*(L2/L_total):.1f}°**
    """)
    
    if is_stable:
        st.success(f"✅ Planet at {planet_dist} AU is STABLE (>{stable_limit:.1f} AU limit for P-type)")
    else:
        st.error(f"❌ Planet at {planet_dist} AU is UNSTABLE (<{stable_limit:.1f} AU, will be ejected)")
    
    if is_habitable:
        st.success(f"✅ Planet is in HABITABLE ZONE ({HZ_inner:.2f} - {HZ_outer:.2f} AU)")
    else:
        st.warning(f"⚠️ Planet outside HZ. Move to {HZ_inner:.2f}-{HZ_outer:.2f} AU for liquid water.")

# --- EQUATIONS FOOTER ---
st.divider()
st.markdown("### 🧮 Core Equations Used")
st.latex(r"""
\begin{aligned}
L &\propto R^2 T^4 \quad \text{(Stefan-Boltzmann)}\\
P^2 &= \frac{a^3}{M_1+M_2} \quad \text{(Kepler's 3rd Law)}\\
r_{bary} &= a \frac{M_2}{M_1+M_2} \quad \text{(Barycenter)}\\
HZ &\approx \sqrt{L_{total}} \times [0.95, 1.67] \text{ AU}
\end{aligned}
""")

st.markdown("---")
st.caption("© 2026 ModelForge Hub | App 3 - Binary Star Lab V2.0 | Built by Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS) | UniZulu | Physics: Stefan-Boltzmann, Kepler, Barycenter")
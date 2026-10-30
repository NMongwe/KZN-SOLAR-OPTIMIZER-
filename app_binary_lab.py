import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

st.set_page_config(page_title="ModelForge - Multi-Sun V3.5", page_icon="🌍", layout="wide")

try:
    st.image("logo.png", width=180)
except:
    st.markdown("## 🌍 ModelForge Hub")

st.title("ModelForge - Solar System Multi-Sun Lab V3.5")
st.caption("What if our Solar System orbited 2,3,4,5 Suns? | Planets Only Edition")
st.warning("⚠️ HYPOTHETICAL: Real system has 1 Sun. This explores how YEARS change with N suns.")

planets = {
    "Mercury": (0.39, 88, 167),
    "Venus": (0.72, 225, 464),
    "Earth": (1.0, 365, 15),
    "Mars": (1.52, 687, -65),
    "Jupiter": (5.2, 4333, -110),
    "Saturn": (9.58, 10759, -140),
}

st.sidebar.header("🌞 Multi-Sun Controls")
num_suns = st.sidebar.slider("Number of Suns (N)", 1, 5, 3, 1)
M_each = st.sidebar.slider("Mass per Sun (Msun)", 0.3, 5.0, 1.0, 0.1)
T_each = st.sidebar.slider("Temp per Sun (K)", 3000, 30000, 5778, 100)
R_each = st.sidebar.slider("Radius per Sun (Rsun)", 0.5, 5.0, 1.0, 0.1)
a_stars = st.sidebar.slider("Distance Between Suns (AU)", 0.1, 5.0, 0.5, 0.1)
selected_planets = st.sidebar.multiselect("Select Planets", list(planets.keys()), default=["Earth","Jupiter","Mars"])

T_sun = 5778
def lum(R,T): return (R**2)*((T/T_sun)**4)
L_each = lum(R_each, T_each)
L_total = L_each * num_suns
M_total = M_each * num_suns
HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67
earth_new_year = math.sqrt((1**3)/M_total)*365.25

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Mass", f"{M_total:.1f} Msun")
c2.metric("Total Light", f"{L_total:.2f} Lsun", f"{L_each:.2f} each")
c3.metric("New HZ", f"{HZ_inner:.2f}-{HZ_outer:.2f} AU")
c4.metric("Earth New Year", f"{earth_new_year:.0f} d", f"{earth_new_year-365:.0f} d", delta_color="inverse")

fig, ax = plt.subplots(figsize=(10,4))
x = np.arange(len(selected_planets))
real_years = [planets[p][1] for p in selected_planets]
new_years = [math.sqrt((planets[p][0]**3)/M_total)*365.25 for p in selected_planets]
width=0.35
ax.bar(x-width/2, real_years, width, label='Real 1 Sun', color='gray', alpha=0.6)
ax.bar(x+width/2, new_years, width, label=f'{num_suns} Suns', color='dodgerblue')
ax.set_xticks(x)
ax.set_xticklabels(selected_planets)
ax.set_ylabel("Year (days) log")
ax.set_yscale('log')
ax.legend()
for i,v in enumerate(new_years):
    ax.text(i+width/2, v, f"{v:.0f}d", ha='center', va='bottom', fontweight='bold')
st.pyplot(fig)

rows=[]
for p in selected_planets:
    a_p, real_d, temp = planets[p]
    new_d = math.sqrt((a_p**3)/M_total)*365.25
    change = new_d - real_d
    hab = "HABITABLE" if HZ_inner <= a_p <= HZ_outer else "NOT HABITABLE"
    rows.append([p, f"{a_p} AU", f"{real_d} d", f"{new_d:.0f} d", f"{change:.0f} d", hab])

df = pd.DataFrame(rows, columns=["Planet","Distance","Real Year","New Year","Change","Status"])
st.dataframe(df, use_container_width=True)

fig2, ax2 = plt.subplots(figsize=(6,6))
ax2.plot(0,0,'k+', markersize=20)
for i in range(num_suns):
    ang=2*math.pi*i/num_suns
    ax2.plot(a_stars*0.5*math.cos(ang), a_stars*0.5*math.sin(ang), 'yo', markersize=14+R_each*2)
for p in selected_planets:
    a_p=planets[p][0]
    th=np.linspace(0,2*np.pi,100)
    ax2.plot(a_p*np.cos(th), a_p*np.sin(th)*0.9, label=f"{p}")
ax2.add_artist(plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':', label=f"HZ Inner {HZ_inner:.2f}"))
ax2.add_artist(plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--', label=f"HZ Outer {HZ_outer:.2f}"))
ax2.set_aspect('equal')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)
ax2.set_title(f"{num_suns} Suns | HZ {HZ_inner:.2f}-{HZ_outer:.2f} AU | Earth {earth_new_year:.0f}d")
st.pyplot(fig2)

# --- NEW: WHAT DOES HABITABLE MEAN? ---
st.divider()
st.subheader("🌍 What Does HABITABLE vs NOT HABITABLE Mean?")

col_hab, col_nothab = st.columns(2)
with col_hab:
    st.success(f"""
    ### ✅ HABITABLE - Inside {HZ_inner:.2f} - {HZ_outer:.2f} AU
    
    **Meaning:** Liquid water can exist on surface
    
    **With {num_suns} Suns ({L_total:.2f}x light):**
    - Temperature: 0°C to 100°C (water not frozen/boiled)
    - A planet here could have oceans, lakes, rain
    - Could support life like Earth
    
    **Example Now:** 
    - {"Earth at 1.0 AU - STILL habitable!" if HZ_inner <=1.0<=HZ_outer else f"Mars at 1.52 AU - BECOMES new Earth! (was cold at -65°C, now warmer)" if HZ_inner <=1.52<=HZ_outer else f"No inner planet - Need to move to {HZ_inner:.2f} AU"}
    """)

with col_nothab:
    st.error(f"""
    ### ❌ NOT HABITABLE - Outside {HZ_inner:.2f} - {HZ_outer:.2f} AU
    
    **TOO CLOSE (< {HZ_inner:.2f} AU):**
    - Too hot: {L_total:.2f}x sun light → water boils → 200°C+
    - Oceans evaporate, atmosphere lost
    - Like Venus: 464°C, no life
    
    **TOO FAR (> {HZ_outer:.2f} AU):**
    - Too cold: light too weak → water freezes → -100°C
    - Ice planet, no liquid water
    - Like Mars/Jupiter now: -65°C to -140°C
    
    **Example Now:**
    - {"Earth at 1.0 AU - TOO HOT! Burns! Must move to "+f"{HZ_inner:.2f} AU" if 1.0 < HZ_inner else "Jupiter at 5.2 AU - TOO COLD! Frozen!" if 5.2 > HZ_outer else ""}
    """)

st.info(f"""
**🔬 Summary for {num_suns} Suns:**
- **Light:** {L_total:.2f}x brighter → HZ moves OUT from 0.95-1.67 AU → {HZ_inner:.2f}-{HZ_outer:.2f} AU
- **Mass:** {M_total:.1f}x heavier → Years SHORTER: Earth 365d → {earth_new_year:.0f}d
- **Best New Home:** Planet closest to { (HZ_inner+HZ_outer)/2 :.2f} AU (middle of HZ) has best chance for life
- **Science:** `HZ ∝ sqrt(L_total)` - More suns = brighter = habitable zone farther away
""")

# --- FOOTER ---
st.divider()
st.caption(f"Equation: P_new = sqrt(a^3 / (N*M)) * 365.25 | L_total = N * R^2 * (T/5778)^4 | HZ = sqrt(L_total) * [0.95-1.67]")
st.caption(f"© 2026 ModelForge Hub | App 3 - Solar System Multi-Sun Lab V3.5 | Built by Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS) | UniZulu")
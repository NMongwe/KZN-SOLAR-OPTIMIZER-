import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="ModelForge - Solar System Multi-Sun V3.2", page_icon="🌍", layout="wide")

st.title("🌍 ModelForge - Solar System Multi-Sun Lab V2.0")
st.markdown(" | What if our Solar System orbited 2,3,4,5 Suns? | Planets Only Edition**")
st.warning("⚠️ HYPOTHETICAL PLANETARY SCIENCE: Real Solar System has 1 Sun. This lab explores how YEARS change with N suns.")

# --- PLANETS DATA ONLY ---
planets = {
    "Mercury": (0.39, 88, 0.24),
    "Venus": (0.72, 225, 0.62),
    "Earth": (1.0, 365, 1.0),
    "Mars": (1.52, 687, 1.88),
    "Jupiter": (5.2, 4333, 11.86),
    "Saturn": (9.58, 10759, 29.46),
    "Uranus": (19.18, 30687, 84.01),
    "Neptune": (30.07, 60190, 164.8),
}

# --- SIDEBAR ---
st.sidebar.header("🌞 Multi-Sun Controls")
num_suns = st.sidebar.slider("Number of Suns (N)", 1, 5, 2, 1)
M_each = st.sidebar.slider("Mass per Sun (Msun)", 0.3, 5.0, 1.0, 0.1)
T_each = st.sidebar.slider("Temp per Sun (K)", 3000, 30000, 5778, 100)
R_each = st.sidebar.slider("Radius per Sun (Rsun)", 0.5, 5.0, 1.0, 0.1)
a_stars = st.sidebar.slider("Distance Between Suns (AU)", 0.1, 5.0, 0.5, 0.1)

selected_planets = st.sidebar.multiselect("Select Planets to Compare", list(planets.keys()), default=["Mercury","Venus","Earth","Mars","Jupiter"])

# --- PHYSICS ---
T_sun = 5778
def lum(R,T): return (R**2)*((T/T_sun)**4)
L_each = lum(R_each, T_each)
L_total = L_each * num_suns
M_total = M_each * num_suns

HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67

# --- TOP METRICS ---
st.subheader(f"📅 What Happens to YEAR with {num_suns} Suns? (M_total={M_total} Msun)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Mass", f"{M_total:.1f} Msun", f"{num_suns} x {M_each}")
c2.metric("Total Light", f"{L_total:.2f} Lsun", f"{L_each:.2f} each")
c3.metric("Habitable Zone", f"{HZ_inner:.2f} - {HZ_outer:.2f} AU", f"Was 0.95-1.67 AU")
earth_new_year = math.sqrt((1**3)/M_total)*365.25
c4.metric("Earth's New Year", f"{earth_new_year:.0f} days", f"{earth_new_year-365:+.0f} vs 365")

# --- MAIN GRAPH ---
st.subheader(f"📊 Year Length: Real (1 Sun) vs New ({num_suns} Suns)")
fig, ax = plt.subplots(figsize=(12,5))
x = np.arange(len(selected_planets))
real_years = [planets[p][1] for p in selected_planets]
new_years = [math.sqrt((planets[p][0]**3)/M_total)*365.25 for p in selected_planets]

width = 0.35
bars1 = ax.bar(x - width/2, real_years, width, label='Real 1 Sun (days)', color='gray', alpha=0.6)
bars2 = ax.bar(x + width/2, new_years, width, label=f'{num_suns} Suns - NEW Year', color='dodgerblue')

ax.set_xticks(x)
ax.set_xticklabels(selected_planets)
ax.set_ylabel("Year Length (days) - log scale")
ax.set_yscale('log')
ax.set_title(f"Kepler P² = a³ / M_total | More Mass = Shorter Year")
ax.legend()
for i, v in enumerate(new_years):
    ax.text(i+width/2, v, f"{v:.0f}d", ha='center', va='bottom', fontweight='bold', fontsize=9)
st.pyplot(fig)

# --- TABLE ---
st.subheader(f"📋 Detailed Comparison Table — {num_suns} Suns")
rows = []
for p in selected_planets:
    a_p, real_d, real_y = planets[p]
    new_d = math.sqrt((a_p**3)/M_total)*365.25
    new_y = new_d/365.25
    diff = real_d - new_d
    hab = "✅ HABITABLE" if HZ_inner <= a_p <= HZ_outer else "❌"
    rows.append([p, f"{a_p} AU", f"{real_d} d ({real_y} yr)", f"{new_d:.0f} d ({new_y:.2f} yr)", f"{diff:+.0f} d ({diff/real_d*100:+.0f}%)", hab])

# Display as table
import pandas as pd
df = pd.DataFrame(rows, columns=["Planet","Distance from Barycenter","Real Year (1 Sun)","New Year (%s Suns)" % num_suns,"Change","In New HZ?"])
st.dataframe(df, use_container_width=True)

# --- SECOND ROW ---
left, right = st.columns(2)
with left:
    st.subheader(f"🪐 Orbits with {num_suns} Suns")
    fig2, ax2 = plt.subplots(figsize=(6,6))
    ax2.plot(0,0,'k+', markersize=20, label="Barycenter")
    for i in range(num_suns):
        ang = 2*math.pi*i/num_suns
        xs = a_stars*0.5*math.cos(ang)
        ys = a_stars*0.5*math.sin(ang)
        ax2.plot(xs, ys, 'yo', markersize=14+R_each*2)
    for p in selected_planets:
        a_p = planets[p][0]
        th = np.linspace(0,2*np.pi,100)
        ax2.plot(a_p*np.cos(th), a_p*np.sin(th)*0.9, label=f"{p} {a_p}AU")
    ax2.add_artist(plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':', label=f"HZ {HZ_inner:.2f}"))
    ax2.add_artist(plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--', label=f"HZ {HZ_outer:.2f}"))
    ax2.set_aspect('equal')
    ax2.legend(fontsize=7, loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel("AU")
    ax2.set_title(f"{num_suns} Suns | HZ {HZ_inner:.2f}-{HZ_outer:.2f} AU | Earth {earth_new_year:.0f}d")
    st.pyplot(fig2)

with right:
    st.subheader("💡 What This Means")
    st.write(f"""
    **With {num_suns} Suns ({M_total} Msun):**
    - Earth year: **365d → {earth_new_year:.0f}d** — birthday every {earth_new_year/30:.1f} months!
    - Light: **{L_total:.2f}x** brighter → Earth burns at 1 AU if L>1.5
    - New Habitable Zone: **{HZ_inner:.2f} - {HZ_outer:.2f} AU** (was 0.95-1.67)
    - Mars (1.52 AU): {'**becomes new Earth!** ✅' if HZ_inner <=1.52<=HZ_outer else 'still cold/hot ❌'}
    - Jupiter year: 11.8yr → {math.sqrt((5.2**3)/M_total):.2f}yr
    """)
    if HZ_inner <=1.0<=HZ_outer:
        st.success(f"✅ Earth STILL habitable with {num_suns} suns")
    else:
        st.error(f"❌ Earth NOT habitable — must move to {HZ_inner:.2f} AU. Mars might be new home.")

st.divider()
st.latex(r"P_{new}= \sqrt{\frac{a^3}{N\cdot M}}\times365.25 \quad | \quad L_{tot}=N\cdot R^2T^4 \quad | \quad HZ\propto\sqrt{L_{tot}}")
st.markdown("""
### 👥 Authors & License
- **Ntusani Mongwe** — Applied Mathematics & Physics (UniZulu)
- **Nontando Tsewu** — Applied Mathematics & Computer Science (UniZulu)
**© 2026 ModelForge Hub. All Rights Reserved. | MIT License** | Planets Only Edition
*From Equation to Impact — What if Earth had 5 Suns?*
""")
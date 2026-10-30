import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

st.set_page_config(page_title="ModelForge - Solar System Multi-Sun V3.3", page_icon="🌍", layout="wide")
try:
 st.image("logo.jpg", width=350)
except:
    pass
st.title("🌍 ModelForge - Solar System Multi-Sun Lab V3.3")
st.markdown(" | What if our Solar System orbited 2,3,4,5 Suns? | Planets Only**")
st.warning("⚠️ HYPOTHETICAL: Real Solar System has 1 Sun. This explores how YEARS change with N suns.")

planets = {
    "Mercury": (0.39, 88),
    "Venus": (0.72, 225),
    "Earth": (1.0, 365),
    "Mars": (1.52, 687),
    "Jupiter": (5.2, 4333),
    "Saturn": (9.58, 10759),
    "Uranus": (19.18, 30687),
    "Neptune": (30.07, 60190),
}

st.sidebar.header("🌞 Multi-Sun Controls")
num_suns = st.sidebar.slider("Number of Suns (N)", 1, 5, 2, 1)
M_each = st.sidebar.slider("Mass per Sun (Msun)", 0.3, 5.0, 1.0, 0.1)
T_each = st.sidebar.slider("Temp per Sun (K)", 3000, 30000, 5778, 100)
R_each = st.sidebar.slider("Radius per Sun (Rsun)", 0.5, 5.0, 1.0, 0.1)
a_stars = st.sidebar.slider("Distance Between Suns (AU)", 0.1, 5.0, 0.5, 0.1)
selected_planets = st.sidebar.multiselect("Select Planets", list(planets.keys()), default=["Mercury","Venus","Earth","Mars"])

T_sun = 5778
def lum(R,T): return (R**2)*((T/T_sun)**4)
L_each = lum(R_each, T_each)
L_total = L_each * num_suns
M_total = M_each * num_suns
HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67
earth_new_year = math.sqrt((1**3)/M_total)*365.25

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Mass", f"{M_total:.1f} Msun", f"{num_suns} x {M_each}")
c2.metric("Total Light", f"{L_total:.2f} Lsun", f"{L_each:.2f} each")
c3.metric("HZ", f"{HZ_inner:.2f}-{HZ_outer:.2f} AU", "was 0.95-1.67")
c4.metric("Earth New Year", f"{earth_new_year:.0f} days", f"{earth_new_year-365:+.0f}")

fig, ax = plt.subplots(figsize=(12,4))
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
ax.set_title(f"P²=a³/M_total | Year shortens with more suns")
ax.legend()
for i,v in enumerate(new_years):
    ax.text(i+width/2, v, f"{v:.0f}d", ha='center', va='bottom', fontweight='bold')
st.pyplot(fig)

rows=[]
for p in selected_planets:
    a_p, real_d = planets[p]
    new_d = math.sqrt((a_p**3)/M_total)*365.25
    hab = "✅ HABITABLE" if HZ_inner <= a_p <= HZ_outer else "❌"
    rows.append([p, f"{a_p} AU", f"{real_d} d", f"{new_d:.0f} d", f"{real_d-new_d:+.0f} d", hab])
df = pd.DataFrame(rows, columns=["Planet","Distance","Real Year","New Year","Change","HZ"])
st.dataframe(df, use_container_width=True)

left,right = st.columns(2)
with left:
    fig2, ax2 = plt.subplots(figsize=(6,6))
    ax2.plot(0,0,'k+', markersize=20)
    for i in range(num_suns):
        ang=2*math.pi*i/num_suns
        ax2.plot(a_stars*0.5*math.cos(ang), a_stars*0.5*math.sin(ang), 'yo', markersize=14+R_each*2)
    for p in selected_planets:
        a_p=planets[p][0]
        th=np.linspace(0,2*np.pi,100)
        ax2.plot(a_p*np.cos(th), a_p*np.sin(th)*0.9, label=f"{p}")
    ax2.add_artist(plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':'))
    ax2.add_artist(plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--'))
    ax2.set_aspect('equal')
    ax2.legend(fontsize=7)
    ax2.grid(True, alpha=0.3)
    ax2.set_title(f"{num_suns} Suns | Earth {earth_new_year:.0f}d | HZ {HZ_inner:.2f}-{HZ_outer:.2f}")
    st.pyplot(fig2)
with right:
    st.write(f"**With {num_suns} Suns:** Earth 365→{earth_new_year:.0f}d, Light {L_total:.2f}x, Mars new Earth: {'YES' if HZ_inner<=1.52<=HZ_outer else 'NO'}")
    if HZ_inner<=1.0<=HZ_outer:
        st.success("Earth habitable")
    else:
        st.error(f"Earth not habitable, move to {HZ_inner:.2f} AU")

# --- FOOTER ---
st.divider()
st.markdown(f"""
**Equation:** `P_new = sqrt(a^3 / (N*M_sun)) * 365.25` where `L ∝ T^4` | **Barycenter Shift:** `r = a * M2/(M1+M2)` | **HZ:** `HZ ∝ sqrt(N*L)` | **Year:** `Year_N = Year_1 / sqrt(N)`

© 2026 ModelForge Hub |  Solar System Multi-Sun Lab | Built by Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS) | UniZulu
""")
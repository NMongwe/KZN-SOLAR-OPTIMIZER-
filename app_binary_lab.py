import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd

st.set_page_config(page_title="ModelForge - Multi-Sun ", page_icon="🌍", layout="wide")

# --- LOGO ---
try:
    st.image("logo.png", width=200)
except:
    st.markdown("### 🌍 ModelForge Hub")

st.title("ModelForge - Solar System Multi-Sun Lab V3.6")
st.caption(" | What if our Solar System orbited 2,3,4,5 Suns? | Planets Only")
st.warning("⚠️ HYPOTHETICAL: Real system has 1 Sun. This explores how YEARS change with N suns.")

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
selected_planets = st.sidebar.multiselect("Select Planets", list(planets.keys()), default=["Earth","Mars"])

# --- PHYSICS ---
T_sun = 5778
def lum(R,T): return (R**2)*((T/T_sun)**4)
L_each = lum(R_each, T_each)
L_total = L_each * num_suns
M_total = M_each * num_suns
HZ_inner = math.sqrt(L_total) * 0.95
HZ_outer = math.sqrt(L_total) * 1.67
earth_new_year = math.sqrt((1**3)/M_total)*365.25

# --- METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Mass", f"{M_total:.1f} Msun", f"{num_suns} x {M_each}")
c2.metric("Total Light", f"{L_total:.2f} Lsun", f"{L_each:.2f} each")
c3.metric("New HZ", f"{HZ_inner:.2f}-{HZ_outer:.2f} AU", "was 0.95-1.67 AU")
c4.metric("Earth New Year", f"{earth_new_year:.0f} days", f"{earth_new_year-365:.0f} d", delta_color="inverse")

# --- FIXED GRAPH: Linear for few planets, log for many ---
st.subheader(f"📊 Year Length: 1 Sun vs {num_suns} Suns")
fig, ax = plt.subplots(figsize=(10,5))
x = np.arange(len(selected_planets))
real_years = [planets[p][1] for p in selected_planets]
new_years = [math.sqrt((planets[p][0]**3)/M_total)*365.25 for p in selected_planets]
width=0.35

if len(selected_planets) <= 3:
    ax.bar(x-width/2, real_years, width, label='Real 1 Sun', color='#BDBDBD')
    ax.bar(x+width/2, new_years, width, label=f'{num_suns} Suns', color='#2196F3')
    ax.set_ylabel("Year (days)")
    for i,(r,n) in enumerate(zip(real_years,new_years)):
        ax.text(i-width/2, r*1.02, f"{r}d", ha='center', va='bottom', fontweight='bold', fontsize=10)
        ax.text(i+width/2, n*1.02, f"{n:.0f}d", ha='center', va='bottom', fontweight='bold', fontsize=10, color='blue')
else:
    ax.bar(x-width/2, real_years, width, label='Real 1 Sun', color='#BDBDBD')
    ax.bar(x+width/2, new_years, width, label=f'{num_suns} Suns', color='#2196F3')
    ax.set_ylabel("Year (days) log")
    ax.set_yscale('log')
    for i,v in enumerate(new_years):
        ax.text(i+width/2, v*1.1, f"{v:.0f}d", ha='center', va='bottom', fontweight='bold', fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels(selected_planets, fontsize=11)
ax.set_title(f"P²=a³/M_total | Earth 365d → {earth_new_year:.0f}d | M_total={M_total} Msun")
ax.legend()
plt.tight_layout()
st.pyplot(fig)


st.subheader("📋 Comparison Table")
rows=[]
for p in selected_planets:
    a_p, real_d = planets[p]
    new_d = math.sqrt((a_p**3)/M_total)*365.25
    change = new_d - real_d  # FIXED: now -107 for Earth with 2 Suns
    pct = (change/real_d)*100
    hab = "HABITABLE" if HZ_inner <= a_p <= HZ_outer else "NOT HABITABLE"
    rows.append([p, f"{a_p} AU", f"{real_d} d", f"{new_d:.0f} d", f"{change:+.0f} d ({pct:+.0f}%)", hab])

df = pd.DataFrame(rows, columns=["Planet","Distance","Real Year (1 Sun)",f"New Year ({num_suns} Suns)","Change","Status"])
st.dataframe(df, use_container_width=True)

# --- ORBIT PLOT ---
st.subheader(f"🪐 Orbits | {num_suns} Suns | HZ {HZ_inner:.2f}-{HZ_outer:.2f} AU | Earth {earth_new_year:.0f}d")
fig2, ax2 = plt.subplots(figsize=(7,7))
ax2.plot(0,0,'k+', markersize=20, label="Barycenter")
for i in range(num_suns):
    ang=2*math.pi*i/num_suns
    ax2.plot(a_stars*0.5*math.cos(ang), a_stars*0.5*math.sin(ang), 'yo', markersize=14+R_each*3, markeredgecolor='orange', markeredgewidth=1)
for p in selected_planets:
    a_p=planets[p][0]
    th=np.linspace(0,2*np.pi,200)
    ax2.plot(a_p*np.cos(th), a_p*np.sin(th)*0.9, label=f"{p} {a_p}AU", linewidth=2)
ax2.add_artist(plt.Circle((0,0), HZ_inner, color='green', fill=False, linestyle=':', linewidth=2))
ax2.add_artist(plt.Circle((0,0), HZ_outer, color='green', fill=False, linestyle='--', linewidth=2))
ax2.add_artist(plt.Rectangle((-0.1,-0.1),0.2,0.2, color='green', alpha=0.1, label=f"HZ {HZ_inner:.2f}-{HZ_outer:.2f}"))
ax2.set_aspect('equal')
ax2.legend(fontsize=8, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_xlabel("AU")
ax2.set_ylabel("AU")
ax2.set_title(f"{num_suns} Suns | Earth {earth_new_year:.0f}d | HZ {HZ_inner:.2f}-{HZ_outer:.2f} AU")
plt.tight_layout()
st.pyplot(fig2)

# --- NEW: WHAT HABITABLE MEANS ---
st.divider()
st.subheader("🌍 What Does HABITABLE vs NOT HABITABLE Mean?")

col_hab, col_nothab = st.columns(2)
with col_hab:
    st.success(f"""
    #### ✅ HABITABLE - Inside {HZ_inner:.2f} - {HZ_outer:.2f} AU
    **Meaning:** Liquid water can exist on surface
    
    **With {num_suns} Suns ({L_total:.2f}x light):**
    - Temp: 0°C to 100°C (water not frozen/boiled)
    - Can have oceans, lakes, rain
    - Could support life like Earth
    
    **Example Now:**
    - Mars at 1.52 AU - {"BECOMES new Earth! ✅ (was -65°C, now warmer)" if HZ_inner <=1.52<=HZ_outer else "Still too cold/ hot"}
    - Earth at 1.0 AU - {"Still habitable! ✅" if HZ_inner <=1.0<=HZ_outer else f"NOT habitable - too hot! Must move to {HZ_inner:.2f} AU"}
    """)

with col_nothab:
    st.error(f"""
    #### ❌ NOT HABITABLE - Outside {HZ_inner:.2f} - {HZ_outer:.2f} AU
    
    **TOO CLOSE (< {HZ_inner:.2f} AU):**
    - Too hot: {L_total:.2f}x sun light → water boils → 200°C+
    - Oceans evaporate, like Venus 464°C
    
    **TOO FAR (> {HZ_outer:.2f} AU):**
    - Too cold: light too weak → water freezes → -100°C
    - Ice planet, like Mars/Jupiter
    
    **Result:** No liquid water = No life as we know it
    """)

st.info(f"🔬 **Summary for {num_suns} Suns:** Light {L_total:.2f}x → HZ moves OUT 0.95-1.67 → {HZ_inner:.2f}-{HZ_outer:.2f} AU | Mass {M_total:.1f}x → Years shorter 365→{earth_new_year:.0f}d | Best home: {(HZ_inner+HZ_outer)/2:.2f} AU")

# --- FOOTER + FIX FOR MANAGE APP BUTTON ---
st.divider()
st.caption(f"Equation: P_new = sqrt(a³ / (N*M)) × 365.25 | L_total = N × R² × (T/5778)⁴ | HZ ∝ sqrt(L_total) | r = a×M2/(M1+M2)")
st.caption(f"© 2026 ModelForge Hub | App 3 - Solar System Multi-Sun Lab V3.6 | Built by Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS) | UniZulu")
# Extra space so "Manage app" button on mobile doesn't cover text
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
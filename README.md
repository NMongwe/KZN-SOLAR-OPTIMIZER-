<p align="center">
  <img src="logo.jpg" width="250" alt="ModelForge Hub Logo"/>
</p>

<h1 align="center">🌌 ModelForge Hub - KZN Solar & Binary Star Systems</h1>

### UniZulu BSc Applied Maths & Physics / CS Final Year Project
**Authors:** Ntusani Mongwe (Applied Maths & Physics) & Nontando Tsewu (Applied Maths & CS)

A unified hub of solar optimization models, bridging solar engineering and astrophysics education for KZN's 32 nodes.

---

### 🌐 Live Apps (Same Repo, Multiple Deployments)

| App | File | Description | Link |
|---|---|---|---|
| **App 1: KZN Solar Optimizer V1.0** | `app.py` | Stable single-sun model. Fetches NASA GHI for 32 KZN towns, calculates optimal tilt =|lat| + dec*0.5, compares fixed vs adjustable yield. For assessment. | https://kznsolaroptimizer.streamlit.app/|
| **App 2: KZN Binary Solar Model V1.1** | `app_binary_solar.py` | **NEW** - Hypothetical binary sun extension. Adds second sun using Stefan-Boltzmann Law L=4πR²σT⁴. Shows GHI boost and tilt shift toward barycenter. Educational simulator inspired by Kepler-16b. | https://binarysolar.streamlit.app/ |
| **App 3: Binary Star Lab V2.0** | `app_binary_lab.py` | **COMING** - Pure astrophysics simulator. Calculates Kepler's Third Law P²=a³/(M1+M2), barycenter, light curves. | [kznbinarystars.streamlit.app] |

All apps deploy from this single repository by selecting different main files on Streamlit Cloud.

---

### 📖 App 2 - Detailed Explanation

**Problem:**
- Earth has one Sun, but >50% of Milky Way systems are binary.
- Standard solar calculators cannot answer: "What if a KZN town had two suns?"
- Need to teach L ∝ T⁴ interactively.

**Solution:**
- Toggle companion star: Red Dwarf (3000K), White Dwarf (8000K), Blue Giant (15000K), Twin Sun (5800K)
- Physics: `GHI_binary = GHI_NASA * (1 + 0.3 * L_ratio)` and `tilt_binary = tilt_single - 2*L_ratio`

**Disclaimer:**
> Earth has ONE Sun. App 2 is hypothetical educational simulator using Stefan-Boltzmann Law. Inspired by Kepler-16b.

---

### 🚀 Deploy Multiple Apps from One Repo
1. Push all `app_*.py` files + `logo.jpg` to this repo
2. share.streamlit.io → New App → Select repo → Change Main file path to `app.py` or `app_binary_solar.py`
3. Deploy → 3 URLs from 1 repo

### 🧪 Tech Stack
Python, Streamlit, NASA POWER API, Matplotlib

### 📜 License
Educational Use - University of Zululand 2026

<p align="center">
  <img src="logo.jpg" width="120" alt="ModelForge Logo Footer"/>
</p>
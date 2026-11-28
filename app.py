# app.py
# Install: pip install streamlit pandas numpy requests plotly
# Run: streamlit run app.py

import csv
import io
import math
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="ModelForge Hub Solar Planner",
    page_icon="☀️",
    layout="wide",
)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_DAYS = [17, 47, 75, 105, 135, 162, 198, 228, 258, 288, 318, 344]
FALLBACK = [5.93, 5.80, 5.18, 4.22, 3.75, 3.31,
            3.55, 4.06, 4.64, 4.96, 5.40, 5.85]




NASA_KEYS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
             "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def money(value):
    return f"R{value:,.0f}"


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_nasa(latitude, longitude):
    """Return average daily horizontal irradiation in kWh/m²/day."""
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    response = requests.get(
        url,
        params={
            "parameters": "ALLSKY_SFC_SW_DWN",
            "community": "RE",
            "longitude": longitude,
            "latitude": latitude,
            "format": "JSON",
        },
        timeout=12,
    )
    response.raise_for_status()
    data = response.json()["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    values = [float(data[key]) for key in NASA_KEYS]
    if any(not math.isfinite(v) or not 0 < v <= 15 for v in values):
        raise ValueError("NASA POWER returned incomplete monthly irradiation.")
    return values


def solar_geometry(latitude, month_index):
    """Representative-day sun vectors, integrated in two-degree hour-angle steps.

    Coordinate axes are east, north, up. Each sample's integration weight
    is its hour-angle width; the extraterrestrial integral has kWh/m²/day units.
    """
    phi = math.radians(latitude)
    n = MID_DAYS[month_index]
    declination = math.radians(
        23.45 * math.sin(2 * math.pi * (284 + n) / 365)
    )
    step = math.radians(2)
    samples = []
    horizontal_integral = 0.0
    daylight_hours = 0.0
    for h in np.arange(-math.pi, math.pi, step):
        hour_angle = float(h + step / 2)
        east = -math.cos(declination) * math.sin(hour_angle)
        north = (
            math.cos(phi) * math.sin(declination)
            - math.sin(phi) * math.cos(declination) * math.cos(hour_angle)
        )
        up = (
            math.sin(phi) * math.sin(declination)
            + math.cos(phi) * math.cos(declination) * math.cos(hour_angle)
        )
        if up > 0:
            samples.append((east, north, up, step))
            horizontal_integral += up * step
            daylight_hours += step * 12 / math.pi
    extraterrestrial = (
        1.367
        * (1 + 0.033 * math.cos(2 * math.pi * n / 365))
        * 12 / math.pi
        * horizontal_integral
    )
    return samples, horizontal_integral, extraterrestrial, daylight_hours


def diffuse_fraction(clearness):
    """Erbs-style diffuse fraction approximation, bounded to physical limits."""
    k = min(1.0, max(0.0, clearness))
    if k <= 0.22:
        fraction = 1 - 0.09 * k
    elif k <= 0.8:
        fraction = (
            0.9511 - 0.1604 * k + 4.388 * k**2
            - 16.638 * k**3 + 12.336 * k**4
        )
    else:
        fraction = 0.165
    return min(1.0, max(0.08, fraction))


def tilted_daily(ghi, geometry, tilt_degrees, azimuth_degrees):
    """Transpose NASA horizontal daily kWh/m² to an approximate panel plane.

    Azimuth is clockwise from north. Beam is normalized to the supplied
    horizontal beam resource; diffuse sky is isotropic and albedo is 0.20.
    """
    samples, horizontal, extraterrestrial, _ = geometry
    beta = math.radians(tilt_degrees)
    azimuth = math.radians(azimuth_degrees)
    diffuse = ghi * diffuse_fraction(ghi / max(extraterrestrial, 0.001))
    horizontal_beam = max(0.0, ghi - diffuse)
    normal_east = math.sin(beta) * math.sin(azimuth)
    normal_north = math.sin(beta) * math.cos(azimuth)
    normal_up = math.cos(beta)
    incidence_integral = sum(
        max(0.0, east * normal_east + north * normal_north + up * normal_up)
        * step
        for east, north, up, step in samples
    )
    plane_beam = horizontal_beam * incidence_integral / max(horizontal, 0.001)
    sky = diffuse * (1 + math.cos(beta)) / 2
    ground = ghi * 0.20 * (1 - math.cos(beta)) / 2
    return max(0.0, plane_beam + sky + ground)


def energy_flow(monthly_generation, monthly_use, daytime_share,
                battery_kwh, battery_efficiency, days):
    """Daily-average AC-side allocation, returned as monthly kWh."""
    produced = monthly_generation / days
    daily_use = monthly_use / days
    daytime_demand = daily_use * daytime_share
    nighttime_demand = daily_use - daytime_demand
    direct = min(produced, daytime_demand)
    surplus = max(0.0, produced - direct)
    charged = min(
        surplus, battery_kwh * 0.80, nighttime_demand / battery_efficiency
    )
    delivered = charged * battery_efficiency
    exported = max(0.0, surplus - charged)
    return {
        "Direct kWh": direct * days,
        "Charged kWh": charged * days,
        "Delivered kWh": delivered * days,
        "Export kWh": exported * days,
        "Grid offset kWh": (direct + delivered) * days,
    }


def read_monthly_csv(upload):
    """Accept precisely 12 nonnegative kWh values, optionally month-labelled."""
    if upload is None:
        return None
    if upload.size > 100_000:
        raise ValueError("CSV must be 100 KB or smaller.")
    text = upload.getvalue().decode("utf-8-sig")
    rows = [
        [cell.strip() for cell in row]
        for row in csv.reader(io.StringIO(text))
        if any(cell.strip() for cell in row)
    ]
    if rows and rows[0][-1].lower() in {"kwh", "energy", "estimate"}:
        rows.pop(0)
    if len(rows) != 12:
        raise ValueError("CSV must contain exactly 12 monthly values, Jan–Dec.")
    values = []
    for i, row in enumerate(rows):
        if len(row) not in (1, 2):
            raise ValueError(f"Row {i + 1}: use kWh or month,kWh.")
        if len(row) == 2 and row[0].lower() not in {
            MONTHS[i].lower(), MONTH_NAMES[i].lower()
        }:
            raise ValueError(f"Row {i + 1}: expected {MONTH_NAMES[i]}.")
        try:
            value = float(row[-1])
        except ValueError as exc:
            raise ValueError(f"Row {i + 1}: kWh must be numeric.") from exc
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Row {i + 1}: kWh must be finite and nonnegative.")
        values.append(value)
    return values


def relative_difference(other, baseline):
    if baseline == 0:
        return "N/A (zero baseline)"
    return f"{(other - baseline) / baseline * 100:+.1f}%"


st.markdown(
    """
    <style>
    .block-container {max-width: 1250px; padding-top: 1.5rem;}
    .mf-header {background:#173958;color:white;border-radius:20px;
      padding:24px 28px;margin-bottom:18px;}
    .mf-header h1 {color:white;margin:0;font-size:clamp(1.7rem,4vw,2.7rem);}
    .mf-header p {color:#d7e4ee;margin:8px 0 0;}
    .mf-brand {font-weight:800;letter-spacing:.01em;color:#173958;
      font-size:1.45rem;margin-bottom:12px;}
    .mf-brand span {color:#d96735;}
    .mf-attribution {color:#64748b;font-size:.8rem;margin-top:24px;}
    @media(max-width:650px) {
      .mf-header {padding:20px 18px;}
      .block-container {padding-left:1rem;padding-right:1rem;}
    }
    </style>
    <div class="mf-brand">⌁ <span>ModelForge</span> Hub
    <small style="display:block;font-size:.72rem;font-weight:500;
    letter-spacing:.12em">FROM EQUATION TO IMPACT</small></div>
    <div class="mf-header"><h1>Your solar plan, from roof to return.</h1>
    <p>South African solar production, household use, battery backup
    and financial planning. A useful starting point—not an installation
    design.</p></div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Location")
    province = st.selectbox(
        "Province", list(PLACES), index=list(PLACES).index("KwaZulu-Natal")
    )
    towns = list(PLACES[province])
    town = st.selectbox(
        "Town", towns,
        index=towns.index("Ulundi") if "Ulundi" in towns else 0,
    )
    custom = st.checkbox("Use custom coordinates")
    selected_lat, selected_lon = PLACES[province][town]
    if custom:
        latitude = st.number_input(
            "Latitude (°)", min_value=-35.0, max_value=-22.0,
            value=float(selected_lat), step=0.0001, format="%.4f",
        )
        longitude = st.number_input(
            "Longitude (°)", min_value=16.0, max_value=33.0,
            value=float(selected_lon), step=0.0001, format="%.4f",
        )
        location_name = "Custom coordinates"
    else:
        latitude, longitude = selected_lat, selected_lon
        location_name = f"{town}, {province}"
        st.caption(f"Latitude {latitude:.2f}° · Longitude {longitude:.2f}°")

    st.header("Your system")
    system_kw = st.number_input(
        "Entered system size (kW DC)", 0.1, 160.0, 5.0, 0.1
    )
    panel_watts = st.number_input(
        "Panel wattage (W)", 100, 800, 500, 5
    )
    inverter_kw = st.number_input(
        "Inverter AC rating (kW)", 0.1, 160.0, 5.0, 0.1
    )
    roof_tilt = st.number_input(
        "Roof pitch / panel tilt (°)", 0, 60, 28, 1
    )
    azimuth = st.number_input(
        "Roof azimuth (°; 0 north, 90 east)", 0, 359, 0, 1
    )
    shading = st.slider("Horizon / shading loss (%)", 0, 80, 10)
    temperature = st.slider("Temperature loss (%)", 0, 40, 8)
    soiling = st.slider("Soiling loss (%)", 0, 40, 3)
    mismatch = st.slider("Mismatch loss (%)", 0, 30, 2)
    wiring = st.slider("Wiring loss (%)", 0, 30, 2)
    inverter_eff = st.slider("Inverter efficiency (%)", 70, 100, 96)

    st.header("Household & battery")
    monthly_use = st.number_input(
        "Monthly electricity use (kWh)", 1.0, 20000.0, 650.0, 1.0
    )
    daytime_pct = st.slider("Daytime use share (%)", 0, 100, 45)
    battery_kwh = st.number_input(
        "Battery capacity (kWh)", 0.0, 500.0, 5.0, 0.5
    )
    battery_eff_pct = st.slider(
        "Battery round-trip efficiency (%)", 50, 100, 90
    )
    backup_target = st.number_input(
        "Backup target (hours)", 0.5, 72.0, 4.0, 0.5
    )

    st.header("Costs & outlook")
    tariff = st.number_input(
        "Electricity tariff (R/kWh)", 0.0, 30.0, 3.50, 0.01
    )
    export_rate = st.number_input(
        "Export compensation (R/kWh)", 0.0, 30.0, 0.0, 0.01
    )
    installed_cost = st.number_input(
        "Installed cost (R)", 0.0, 10_000_000.0, 110_000.0, 1000.0
    )
    escalation_pct = st.number_input(
        "Tariff escalation (%/year)", 0.0, 30.0, 7.0, 0.1
    )
    degradation_pct = st.number_input(
        "Panel degradation (%/year)", 0.0, 5.0, 0.5, 0.1
    )
    st.caption(
        "Inputs recalculate automatically. NASA POWER requests are cached "
        "for 24 hours; unavailable data use an illustrative fallback."
    )

try:
    solar = fetch_nasa(round(latitude, 4), round(longitude, 4))
    source = "NASA POWER monthly climatology"
    fallback_used = False
except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
    solar = FALLBACK.copy()
    source = "Illustrative fallback—not location-specific"
    fallback_used = True
    st.warning(
        "NASA POWER is unavailable or incomplete. Illustrative, "
        "non-location-specific irradiation is being used. "
        f"Technical detail: {type(exc).__name__}."
    )

geometries = [solar_geometry(latitude, i) for i in range(12)]
dc_retention = math.prod(
    1 - loss / 100
    for loss in (shading, temperature, soiling, mismatch, wiring)
)
combined_ac_factor = dc_retention * inverter_eff / 100


def monthly_ac(plane_daily, month_index):
    """Approximate AC kWh with a daily energy-only inverter cap."""
    uncapped = (
        plane_daily * DAYS[month_index] * system_kw * combined_ac_factor
    )
    equivalent_hours = min(
        9.0, max(1.0, geometries[month_index][3] * 0.65)
    )
    cap = inverter_kw * equivalent_hours * DAYS[month_index]
    return min(uncapped, cap)


rows = []
for i, ghi in enumerate(solar):
    plane = tilted_daily(ghi, geometries[i], roof_tilt, azimuth)
    fixed = monthly_ac(plane, i)
    candidates = [
        monthly_ac(tilted_daily(ghi, geometries[i], angle, azimuth), i)
        for angle in range(61)
    ]
    optimal_tilt = int(np.argmax(candidates))
    flow = energy_flow(
        fixed, monthly_use, daytime_pct / 100,
        battery_kwh, battery_eff_pct / 100, DAYS[i]
    )
    rows.append({
        "Month": MONTHS[i],
        "Horizontal kWh/m²/day": ghi,
        "Tilted plane kWh/m²/day": plane,
        "Optimal tilt °": optimal_tilt,
        "Fixed AC kWh": fixed,
        "Adjusted AC kWh": candidates[optimal_tilt],
        **flow,
    })

monthly = pd.DataFrame(rows)
fixed_annual = float(monthly["Fixed AC kWh"].sum())
adjusted_annual = float(monthly["Adjusted AC kWh"].sum())
best_fixed_by_angle = [
    sum(
        monthly_ac(
            tilted_daily(solar[i], geometries[i], angle, azimuth), i
        )
        for i in range(12)
    )
    for angle in range(61)
]
best_fixed_tilt = int(np.argmax(best_fixed_by_angle))
best_fixed_energy = best_fixed_by_angle[best_fixed_tilt]
direct_annual = float(monthly["Direct kWh"].sum())
charged_annual = float(monthly["Charged kWh"].sum())
delivered_annual = float(monthly["Delivered kWh"].sum())
export_annual = float(monthly["Export kWh"].sum())
offset_annual = direct_annual + delivered_annual
grid_value = offset_annual * tariff
export_credit = export_annual * export_rate
annual_benefit = grid_value + export_credit
payback = installed_cost / annual_benefit if annual_benefit > 0 and installed_cost > 0 else None
panel_count = max(1, round(system_kw * 1000 / panel_watts))
whole_panel_kw = panel_count * panel_watts / 1000
dc_ac_ratio = system_kw / inverter_kw
average_load_kw = monthly_use * 12 / (365 * 24)
backup_hours = battery_kwh * 0.80 / average_load_kw

energy_20 = 0.0
benefit_20 = 0.0
for year in range(20):
    production_factor = (1 - degradation_pct / 100) ** year
    price_factor = (1 + escalation_pct / 100) ** year
    for i, first_year_generation in enumerate(monthly["Fixed AC kWh"]):
        generation = float(first_year_generation) * production_factor
        flow = energy_flow(
            generation, monthly_use, daytime_pct / 100,
            battery_kwh, battery_eff_pct / 100, DAYS[i]
        )
        energy_20 += generation
        benefit_20 += (
            flow["Grid offset kWh"] * tariff
            + flow["Export kWh"] * export_rate
        ) * price_factor

st.caption(
    f"{location_name} · {latitude:.2f}° latitude, {longitude:.2f}° longitude "
    f"· Solar resource: {source}"
)
warnings = []
if not 0.8 <= dc_ac_ratio <= 1.5:
    warnings.append(
        f"DC/AC ratio {dc_ac_ratio:.2f} is outside a common planning "
        "range of 0.8–1.5. Check inverter sizing and clipping."
    )
if abs(whole_panel_kw - system_kw) / system_kw > 0.05:
    warnings.append(
        f"{panel_count} whole panels give {whole_panel_kw:.2f} kW DC, "
        "over 5% from the entered capacity. Calculations retain the "
        "entered system size."
    )
if export_rate > tariff and tariff > 0:
    warnings.append("Export compensation exceeds the retail tariff; verify it.")
if export_rate > 0:
    warnings.append(
        "Export credit requires utility permission, metering and an "
        "applicable compensation agreement."
    )
if daytime_pct in (0, 100):
    warnings.append("The daytime-use share is an extreme load assumption.")
if battery_kwh * 0.8 > monthly_use * 12 / 365:
    warnings.append(
        "Usable battery capacity exceeds average daily demand; review sizing."
    )
if roof_tilt == 0 and azimuth != 0:
    warnings.append("Azimuth has no effect on a horizontal array.")
if installed_cost == 0:
    warnings.append("Installed cost is zero; payback is not meaningful.")
if fallback_used:
    warnings.append(
        "Fallback irradiation is illustrative and not specific to this site."
    )
for message in warnings:
    st.warning(message)

st.header("Your planning snapshot")
a, b, c = st.columns(3)
a.metric("Entered DC system", f"{system_kw:.2f} kW")
b.metric("Fixed-roof generation", f"{fixed_annual:,.0f} kWh/year")
c.metric("Monthly-adjusted advisory", f"{adjusted_annual:,.0f} kWh/year")
a, b, c = st.columns(3)
a.metric("Estimated annual benefit", money(annual_benefit))
b.metric(
    "Simple payback",
    f"{payback:.1f} years" if payback is not None else "Not available",
)
c.metric("Energy-only backup", f"{backup_hours:.1f} hours")

st.info(
    f"At {roof_tilt}° tilt and {azimuth}° azimuth (clockwise from north), "
    f"the fixed-roof estimate is {fixed_annual:,.0f} kWh/year. "
    f"The model's best fixed tilt at this azimuth is {best_fixed_tilt}° "
    f"({best_fixed_energy:,.0f} kWh/year). The monthly-adjusted comparison "
    f"is {adjusted_annual:,.0f} kWh/year and may not be physically practical."
)
st.caption(
    f"Approximately {panel_count} × {panel_watts} W panels = "
    f"{whole_panel_kw:.2f} kW DC. Calculations use the entered "
    f"{system_kw:.2f} kW DC. DC/AC ratio: {dc_ac_ratio:.2f}. "
    f"Backup {'meets' if backup_hours >= backup_target else 'falls below'} "
    f"the {backup_target:.1f}-hour energy target at average household load; "
    "it does not establish inverter power capability or critical-load runtime."
)

st.subheader("Household energy and value")
metrics = [
    ("Direct self-consumption", f"{direct_annual:,.0f} kWh"),
    ("Battery charged", f"{charged_annual:,.0f} kWh"),
    ("Battery delivered", f"{delivered_annual:,.0f} kWh"),
    ("Grid offset", f"{offset_annual:,.0f} kWh"),
    ("Grid export", f"{export_annual:,.0f} kWh"),
    ("Grid offset value", money(grid_value)),
    ("Export credit", money(export_credit)),
]
for start in range(0, len(metrics), 3):
    columns = st.columns(3)
    for column, (label, value) in zip(columns, metrics[start:start + 3]):
        column.metric(label,value)

st.subheader("Fixed vs adjustable tilt")
chart_a, chart_b = st.columns(2)
with chart_a:
    generation_chart = monthly.melt(
        id_vars="Month",
        value_vars=["Fixed AC kWh", "Adjusted AC kWh"],
        var_name="Scenario",
        value_name="Energy (kWh)",
    )
    st.plotly_chart(
        px.bar(
            generation_chart, x="Month", y="Energy (kWh)",
            color="Scenario", barmode="group",
            category_orders={"Month": MONTHS},
            color_discrete_sequence=["#254b78", "#e28a39"],
        ),
        use_container_width=True,
    )
with chart_b:
    tilt_chart = monthly[["Month", "Optimal tilt °"]].copy()
    tilt_chart["Roof tilt °"] = roof_tilt
    st.plotly_chart(
        px.line(
            tilt_chart, x="Month",
            y=["Optimal tilt °", "Roof tilt °"],
            markers=True, category_orders={"Month": MONTHS},
            color_discrete_sequence=["#254b78", "#e28a39"],
        ),
        use_container_width=True,
    )
st.caption(
    "Suggested monthly tilt is theoretical. Roof geometry and mounting "
    "hardware may prevent adjustment."
)

st.subheader("20-year outlook")
a, b, c = st.columns(3)
a.metric("Projected production", f"{energy_20:,.0f} kWh")
b.metric("Projected gross benefit", money(benefit_20))
c.metric(
    "Monthly adjustment gain",
    f"{adjusted_annual - fixed_annual:+,.0f} kWh/year",
)
st.caption(
    "Projection degrades generation annually, recalculates daily household "
    "allocation, and escalates retail and export rates together. It excludes "
    "maintenance, financing, replacements, taxes, fixed charges and incentives."
)

st.subheader("Monthly breakdown")
display_columns = [
    "Month", "Horizontal kWh/m²/day", "Tilted plane kWh/m²/day",
    "Optimal tilt °", "Fixed AC kWh", "Adjusted AC kWh",
    "Direct kWh", "Charged kWh", "Delivered kWh",
    "Export kWh", "Grid offset kWh",
]
st.dataframe(
    monthly[display_columns].style.format({
        column: "{:,.2f}"
        for column in display_columns
        if column not in ("Month", "Optimal tilt °")
    }),
    use_container_width=True,
    hide_index=True,
)

st.header("Model Comparison and Validation")
st.write(
    "These are transparent methodology benchmarks, not an accuracy ranking. "
    "All modelled scenarios use the same entered DC size and NASA horizontal "
    "resource (or the labelled fallback). Differences below are benchmark "
    "minus ModelForge fixed-roof AC generation."
)
comparison_a, comparison_b, comparison_c = st.columns(3)
with comparison_a:
    benchmark_pr = st.number_input(
        "Fixed performance ratio (%)", 0.0, 100.0, 80.0, 1.0
    )
    st.caption("Horizontal irradiation × DC kW × performance ratio.")
with comparison_b:
    external_annual = st.number_input(
        "Installer / external-tool annual kWh (optional)",
        min_value=0.0, value=None, step=100.0,
        placeholder="No external estimate",
    )
with comparison_c:
    upload = st.file_uploader(
        "External monthly estimates CSV (optional)", type=["csv"]
    )
    st.caption("Exactly 12 nonnegative Jan–Dec kWh values; optional month,kWh.")

external_monthly = None
if upload is not None:
    try:
        external_monthly = read_monthly_csv(upload)
    except (UnicodeDecodeError, csv.Error, ValueError) as exc:
        st.error(f"External CSV not used: {exc}")

simple_monthly = [
    solar[i] * DAYS[i] * system_kw for i in range(12)
]
simple_annual = sum(simple_monthly)
pr_monthly = [value * benchmark_pr / 100 for value in simple_monthly]
comparison_series = [
    ("ModelForge enhanced fixed-roof", fixed_annual,
     "Panel-plane geometry, separate losses and daily inverter cap."),
    ("Original simple NASA horizontal", simple_annual,
     "Horizontal irradiation × days × DC kW; no tilt, losses or clipping."),
    (f"Fixed performance ratio ({benchmark_pr:.0f}%)", sum(pr_monthly),
     "Horizontal resource with one combined ratio; no explicit tilt or clipping."),
]
if external_annual is not None:
    comparison_series.append(
        ("Installer / external annual (user input)", external_annual,
         "Check that location, sizing, time period and assumptions match.")
    )
if external_monthly is not None:
    comparison_series.append(
        ("Uploaded external monthly total", sum(external_monthly),
         "Sum of the 12 user-supplied monthly estimates.")
    )

comparison = pd.DataFrame([
    {
        "Approach": label,
        "Annual kWh": value,
        "Average monthly kWh": value / 12,
        "Difference kWh": value - fixed_annual,
        "Difference %": relative_difference(value, fixed_annual),
        "Why it differs": reason,
    }
    for label, value, reason in comparison_series
])
st.dataframe(
    comparison.style.format({
        "Annual kWh": "{:,.1f}",
        "Average monthly kWh": "{:,.1f}",
        "Difference kWh": "{:+,.1f}",
    }),
    hide_index=True,
    use_container_width=True,
)
st.caption(
    "The original simple NASA estimate is monthly horizontal "
    "kWh/m²/day × days × entered DC kW. The fixed-PR benchmark multiplies "
    "that estimate by the selected ratio. Neither is independent validation."
)

benchmark_monthly = pd.DataFrame({
    "Month": MONTHS,
    "ModelForge fixed AC kWh": monthly["Fixed AC kWh"].tolist(),
    "Simple NASA horizontal kWh": simple_monthly,
    "Fixed PR kWh": pr_monthly,
})
if external_monthly is not None:
    benchmark_monthly["External kWh"] = external_monthly
    benchmark_monthly["External difference kWh"] = [
        value - base
        for value, base in zip(
            external_monthly, monthly["Fixed AC kWh"]
        )
    ]
    benchmark_monthly["External difference %"] = [
        relative_difference(value, base)
        for value, base in zip(
            external_monthly, monthly["Fixed AC kWh"]
        )
    ]

st.subheader("Monthly comparison")
monthly_chart_columns = [
    "ModelForge fixed AC kWh", "Simple NASA horizontal kWh",
    "Fixed PR kWh",
]
if external_monthly is not None:
    monthly_chart_columns.append("External kWh")
st.plotly_chart(
    px.bar(
        benchmark_monthly.melt(
            id_vars="Month",
            value_vars=monthly_chart_columns,
            var_name="Scenario", value_name="kWh",
        ),
        x="Month", y="kWh", color="Scenario", barmode="group",
        category_orders={"Month": MONTHS},
        color_discrete_sequence=["#254b78", "#93a9ba", "#e28a39", "#b8344d"],
    ),
    use_container_width=True,
)
monthly_comparison = benchmark_monthly.copy()
for column in monthly_chart_columns[1:]:
    monthly_comparison[column.replace(" kWh", " difference kWh")] = (
        monthly_comparison[column]
        - monthly_comparison["ModelForge fixed AC kWh"]
    )
    monthly_comparison[column.replace(" kWh", " difference %")] = [
        relative_difference(value, base)
        for value, base in zip(
            monthly_comparison[column],
            monthly_comparison["ModelForge fixed AC kWh"],
        )
    ]
st.dataframe(
    monthly_comparison.round(2),
    hide_index=True,
    use_container_width=True,
)
st.caption(
    "Annual and monthly percentage differences are relative to the "
    "ModelForge baseline. A percentage is unavailable when that baseline is zero."
)

st.subheader("Honest benchmark scorecard")
scorecard = pd.DataFrame([
    ("Solar resource", "Included / fallback labelled",
     "NASA POWER monthly climatology, not roof-level measured data."),
    ("Plane-of-array geometry", "Approximate",
     "Latitude-aware representative-day beam, isotropic diffuse and ground reflection."),
    ("Shading", "User assumption",
     "Flat loss percentage; no obstruction or terrain survey."),
    ("System losses", "Separate assumptions",
     "Temperature, soiling, mismatch, wiring and inverter efficiency."),
    ("Inverter clipping", "Approximate",
     "Daily energy cap; no hourly inverter simulation."),
    ("Load and battery", "Approximate",
     "Daily-average allocation; no hourly dispatch or power limits."),
    ("External comparison", "Only when supplied",
     "User annual value and/or validated 12-month CSV; not independently verified."),
    ("Site-specific accuracy", "Not established",
     "Requires roof survey, equipment design and measured conditions."),
], columns=["Aspect", "Status", "What is considered"])
st.dataframe(scorecard, hide_index=True, use_container_width=True)
st.info(
    "NASA POWER is climatological rather than roof-level measured data. "
    "Other tools may differ in weather data, time resolution, equipment "
    "libraries, terrain, shading and site surveys. Align location, DC size, "
    "tilt, azimuth, losses and reporting period before comparing results. "
    "Agreement alone does not prove accuracy."
)

with st.expander("Methods, units and limitations"):
    st.markdown(
        """
        - **Resource:** NASA `ALLSKY_SFC_SW_DWN` monthly climatology is
          average **daily horizontal irradiation**, in kWh/m²/day.
          Multiplication by calendar days yields monthly horizontal kWh/m².
        - **Panel plane:** A representative day for each month integrates
          sun positions at the selected latitude. Estimated diffuse fraction
          splits horizontal irradiation into beam and diffuse components.
          Beam incidence is projected onto the selected tilt and azimuth;
          isotropic sky diffuse and 0.20-albedo ground reflection are added.
          This is not an hourly weather or obstruction simulation.
        - **AC generation:** Panel-plane kWh/m²/day × days × entered kW DC ×
          remaining fractions for shading, temperature, soiling, mismatch,
          wiring and inverter efficiency. An approximate daily inverter
          energy cap is applied; real hourly clipping may differ.
        - **Tilt:** Fixed optimisation tests 0–60° in one-degree steps at
          the chosen azimuth. Monthly advisory tilt independently searches
          the same range; changing a roof's tilt may be impossible.
        - **Household:** Daily generation first serves daytime demand.
          Remaining AC energy charges at most 80% of battery nameplate per
          day and no more than nighttime demand requires after round-trip
          losses. Battery delivery is charged energy × efficiency; the
          remainder is potential export. Grid offset is direct use plus
          delivered battery energy.
        - **Finance:** First-year benefit = grid offset × retail tariff +
          export × compensation. Simple payback divides installed cost by
          first-year benefit. The 20-year projection applies annual panel
          degradation and tariff escalation while holding demand and export
          rules fixed. It omits maintenance, financing, replacements, fixed
          charges, taxes and incentives.
        - **Backup:** 80% of battery nameplate divided by average household
          kW is an energy-only estimate—not critical-load sizing, usable
          power verification, or a guarantee during an outage.
        """
    )

report_lines = [
    "MODELFORGE HUB — PRELIMINARY SOLAR PLANNING REPORT",
    "ModelForge Hub · Founded by Ntusani Mongwe",
    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    f"Location: {location_name} ({latitude:.4f}°, {longitude:.4f}°)",
    f"Resource: {source}",
    "",
    "SYSTEM AND ASSUMPTIONS",
    f"Entered DC: {system_kw:.2f} kW; {panel_count} × {panel_watts} W "
    f"panels imply {whole_panel_kw:.2f} kW DC.",
    f"Inverter: {inverter_kw:.2f} kW AC; DC/AC ratio: {dc_ac_ratio:.2f}.",
    f"Tilt: {roof_tilt}°; azimuth: {azimuth}° clockwise from north.",
    f"Losses: shading {shading}%; temperature {temperature}%; "
    f"soiling {soiling}%; mismatch {mismatch}%; wiring {wiring}%; "
    f"inverter efficiency {inverter_eff}%.",
    f"Battery: {battery_kwh:.1f} kWh; round-trip efficiency "
    f"{battery_eff_pct}%; energy-only backup {backup_hours:.1f} hours.",
    f"Use: {monthly_use:,.0f} kWh/month; daytime share {daytime_pct}%.",
    f"Tariff: R{tariff:.2f}/kWh; export: R{export_rate:.2f}/kWh; "
    f"installed cost: {money(installed_cost)}.",
    f"Escalation: {escalation_pct:.1f}%/year; degradation: "
    f"{degradation_pct:.1f}%/year.",
    "",
    "FIRST-YEAR RESULTS",
    f"Fixed AC: {fixed_annual:,.1f} kWh; monthly-adjusted advisory: "
    f"{adjusted_annual:,.1f} kWh.",
    f"Best fixed tilt: {best_fixed_tilt}°; output: "
    f"{best_fixed_energy:,.1f} kWh.",
    f"Direct: {direct_annual:,.1f} kWh; battery charged: "
    f"{charged_annual:,.1f} kWh; delivered: {delivered_annual:,.1f} kWh.",
    f"Grid offset: {offset_annual:,.1f} kWh; export: "
    f"{export_annual:,.1f} kWh.",
    f"Offset value: {money(grid_value)}; export credit: "
    f"{money(export_credit)}; annual benefit: {money(annual_benefit)}.",
    f"Simple payback: {f'{payback:.1f} years' if payback is not None else 'not available'}.",
    f"20-year production: {energy_20:,.1f} kWh; gross benefit: "
    f"{money(benefit_20)}.",
    "",
    "MONTHLY RESULTS (kWh except resource in kWh/m²/day and tilt in degrees)",
    monthly[display_columns].round(2).to_csv(index=False).strip(),
    "",
    "MODEL COMPARISON — METHODOLOGY BENCHMARKS",
    comparison.round(2).to_csv(index=False).strip(),
    "",
    "MONTHLY MODEL COMPARISON",
    monthly_comparison.round(2).to_csv(index=False).strip(),
    "",
    "WARNINGS",
    *(warnings or ["None flagged by input checks."]),
    "",
    "LIMITATIONS",
    "NASA POWER climatology is not roof-level measured data. Other tools "
    "can differ in weather data, time resolution, equipment libraries, "
    "terrain, shading and site surveys. These preliminary estimates are "
    "not a structural, electrical, grid-connection or installation design. "
    "Have a qualified professional assess the site and equipment.",
]
report = "\n".join(report_lines)
st.download_button(
    "Download summary report (.txt)",
    data=report.encode("utf-8"),
    file_name="modelforge_solar_planning_report.txt",
    mime="text/plain",
)
st.warning(
    "Professional-installation limitation: these are preliminary planning "
    "estimates, not a final structural, electrical or grid-connection design. "
    "Confirm roof condition, shading, loads, equipment, applicable standards "
    "and utility permissions with a qualified professional before purchasing "
    "or connecting a system."
)
st.markdown(
    '<div class="mf-attribution">Solar resource: NASA POWER '
    'ALLSKY_SFC_SW_DWN monthly climatology when available. '
    'ModelForge Hub · Founded by Ntusani Mongwe</div>',
    unsafe_allow_html=True,
)

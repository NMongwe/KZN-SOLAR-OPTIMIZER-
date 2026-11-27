import streamlit as st
import requests
import math
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(page_title="ModelForge Hub - SA Solar Optimizer", page_icon="☀️", layout="wide")

st.markdown("""
<style>
img {image-rendering: -webkit-optimize-contrast;}
</style>
""", unsafe_allow_html=True)

try:
    logo = Image.open("logo.jpg")
    w, h = logo.size
    logo_hd = logo.resize((w*3, h*3), Image.LANCZOS)
    st.image(logo_hd, width=350)
except:
    st.write("☀️ ModelForge Hub")

st.title("☀️ ModelForge Hub - SA Solar Optimizer")
st.caption("From Equation to Impact | By Ntusani & Nontando - UniZulu | Data: NASA POWER")

# --- ALL PROVINCES + TOWNS (KEEP YOUR VERSION) ---

PROVINCES = {
    "KwaZulu-Natal": {
        "Durban": (-29.85, 31.02), "Pietermaritzburg": (-29.60, 30.38),
        "Richards Bay": (-28.78, 32.09), "Nongoma": (-27.89, 31.64),
        "Esikhaleni": (-28.83, 31.90), "Empangeni": (-28.72, 31.88),
        "Newcastle": (-27.75, 29.93), "Ladysmith": (-28.55, 29.78),
        "Port Shepstone": (-30.74, 30.44), "Margate": (-30.85, 30.37),
        "Stanger / KwaDukuza": (-29.33, 31.29), "Tongaat": (-29.57, 31.12),
        "Verulam": (-29.64, 31.05), "Phoenix": (-29.70, 31.03),
        "Chatsworth": (-29.90, 30.90), "Umlazi": (-29.96, 30.89),
        "Pinetown": (-29.82, 30.85), "Umhlanga": (-29.72, 31.08),
        "Ballito": (-29.54, 31.21), "Hluhluwe": (-27.93, 32.27),
        "Mtubatuba": (-28.42, 32.19), "Hlabisa": (-28.14, 31.87),
        "Ulundi": (-28.30, 31.42), "Vryheid": (-27.77, 30.79),
        "Dundee": (-28.16, 30.23), "Greytown": (-29.06, 30.59),
        "Howick": (-29.48, 30.23), "Mooi River": (-29.21, 29.99),
        "Estcourt": (-29.00, 29.87), "Bergville": (-28.73, 29.36),
        "Kokstad": (-30.55, 29.42), "Matatiele": (-30.35, 28.80),
        "Ixopo": (-30.15, 30.06), "Underberg": (-29.79, 29.50),
        "Harding": (-30.58, 29.88), "Scottburgh": (-30.28, 30.75),
        "Amanzimtoti": (-30.05, 30.88), "Hibberdene": (-30.57, 30.57),
        "Eshowe": (-28.89, 31.46), "Melmoth": (-28.58, 31.39),
        "Nkandla": (-28.62, 31.08), "Manguzi / Kosi Bay": (-26.88, 32.89),
        "Jozini": (-27.43, 32.07), "Pongola": (-27.38, 31.61),
        "Paulpietersburg": (-27.42, 30.82), "Utrecht": (-27.66, 30.32),
        "Ixopo": (-30.15, 30.06), "Muden": (-28.99, 30.38),
    },
    "Limpopo": {
        "Polokwane": (-23.90, 29.45), "Thohoyandou": (-23.06, 30.38),
        "Tzaneen": (-23.83, 30.16), "Mokopane": (-24.19, 29.01),
        "Musina": (-22.34, 30.04), "Phalaborwa": (-23.94, 31.14),
        "Lebowakgomo": (-24.31, 29.56), "Giyani": (-23.31, 30.68),
        "Louis Trichardt / Makhado": (-23.05, 29.90), "Lephalale / Ellisras": (-23.67, 27.75),
        "Bela-Bela": (-24.88, 28.29), "Modimolle": (-24.70, 28.41),
        "Thabazimbi": (-24.59, 27.41), "Groblersdal": (-25.16, 29.39),
        "Marble Hall": (-24.96, 29.29), "Burgersfort": (-24.67, 30.32),
        "Hoedspruit": (-24.35, 30.95), "Letsitele": (-23.87, 30.40),
        "Dendron": (-23.37, 29.32), "Seshego": (-23.85, 29.39),
        "Mankweng": (-23.88, 29.82), "Boyne": (-23.90, 29.72),
        "Sibasa": (-23.03, 30.40), "Malamulele": (-23.00, 30.68),
        "Nzhelele": (-22.95, 30.20), "Alldays": (-22.68, 29.11),
        "Vivo": (-23.04, 29.27), "Dzanani": (-23.02, 30.08),
        "Elim": (-23.16, 30.06), "Nkowankowa": (-23.88, 30.29),
        "Lenyenye": (-23.86, 30.29), "Senwabarwana / Bochum": (-23.27, 29.12),
        "Taaiboschgroet": (-23.10, 29.20), "Vhembe": (-23.00, 30.50),
    },
    "Gauteng": {
        "Johannesburg": (-26.20, 28.04), "Pretoria": (-25.74, 28.18),
        "Soweto": (-26.26, 27.85), "Centurion": (-25.86, 28.18),
        "Sandton": (-26.10, 28.05), "Midrand": (-25.99, 28.13),
        "Vereeniging": (-26.67, 27.93), "Vanderbijlpark": (-26.70, 27.84),
        "Meyerton": (-26.55, 28.02), "Heidelberg": (-26.50, 28.35),
        "Nigel": (-26.42, 28.47), "Springs": (-26.25, 28.44),
        "Benoni": (-26.18, 28.32), "Boksburg": (-26.21, 28.26),
        "Germiston": (-26.22, 28.17), "Alberton": (-26.27, 28.12),
        "Kempton Park": (-26.10, 28.23), "Edenvale": (-26.14, 28.15),
        "Randburg": (-26.09, 28.00), "Roodepoort": (-26.16, 27.87),
        "Krugersdorp": (-26.09, 27.77), "Randfontein": (-26.18, 27.70),
        "Westonaria": (-26.31, 27.65), "Carletonville": (-26.36, 27.40),
        "Bronkhorstspruit": (-25.80, 28.73), "Cullinan": (-25.67, 28.52),
        "Hammanskraal": (-25.40, 28.27), "Soshanguve": (-25.54, 28.10),
        "Mamelodi": (-25.71, 28.39), "Atteridgeville": (-25.77, 28.07),
        "Ga-Rankuwa": (-25.62, 27.99), "Mabopane": (-25.51, 28.08),
        "Tembisa": (-26.00, 28.21), "Alexandra": (-26.10, 28.09),
        "Diepsloot": (-25.93, 28.01), "Fourways": (-26.02, 28.00),
    },
    "Western Cape": {
        "Cape Town": (-33.92, 18.42), "Stellenbosch": (-33.93, 18.86),
        "Paarl": (-33.73, 19.00), "George": (-33.96, 22.46),
        "Knysna": (-34.03, 23.05), "Hermanus": (-34.42, 19.23),
        "Somerset West": (-34.08, 18.85), "Strand": (-34.11, 18.82),
        "Gordon's Bay": (-34.16, 18.86), "Fish Hoek": (-34.14, 18.43),
        "Muizenberg": (-34.11, 18.47), "Khayelitsha": (-34.04, 18.68),
        "Mitchells Plain": (-34.05, 18.62), "Bellville": (-33.90, 18.62),
        "Parow": (-33.90, 18.70), "Goodwood": (-33.91, 18.72),
        "Kuils River": (-33.93, 18.68), "Brackenfell": (-33.87, 18.70),
        "Durbanville": (-33.83, 18.64), "Milnerton": (-33.87, 18.50),
        "Hout Bay": (-34.04, 18.35), "Constantia": (-34.03, 18.42),
        "Franschhoek": (-33.91, 19.11), "Wellington": (-33.64, 19.01),
        "Worcester": (-33.65, 19.44), "Robertson": (-33.80, 19.88),
        "Montagu": (-33.78, 20.12), "Tulbagh": (-33.28, 19.14),
        "Ceres": (-33.37, 19.31), "Wolseley": (-33.41, 19.20),
        "Swellendam": (-34.02, 20.44), "Riversdale": (-34.09, 21.26),
        "Mossel Bay": (-34.18, 22.14), "Oudtshoorn": (-33.59, 22.20),
        "Beaufort West": (-32.35, 22.58), "Prince Albert": (-33.22, 22.03),
        "Caledon": (-34.23, 19.43), "Bredasdorp": (-34.53, 20.04),
        "Swartland / Malmesbury": (-33.46, 18.73), "Saldanha": (-33.01, 17.94),
        "Vredenburg": (-32.91, 17.99), "Langebaan": (-33.09, 18.04),
        "Paternoster": (-32.81, 17.88), "Clanwilliam": (-32.18, 18.89),
        "Citrusdal": (-32.59, 19.01), "Ladismith": (-33.49, 21.26),
        "Calitzdorp": (-33.53, 21.68), "Plettenberg Bay": (-34.05, 23.37),
    },
    "Eastern Cape": {
        "Gqeberha": (-33.96, 25.60), "East London": (-33.01, 27.91),
        "Mthatha": (-31.58, 28.78), "Makhanda": (-33.30, 26.52),
        "Queenstown": (-31.90, 26.88), "Uitenhage / Kariega": (-33.76, 25.40),
        "Despatch": (-33.80, 25.47), "Port Elizabeth": (-33.96, 25.60),
        "King William's Town": (-32.88, 27.39), "Bhisho": (-32.85, 27.44),
        "Mdantsane": (-32.95, 27.74), "Duncan Village": (-33.01, 27.90),
        "Butterworth": (-32.33, 28.14), "Idutywa": (-32.10, 28.30),
        "Centane": (-32.50, 28.30), "Willowvale": (-32.30, 28.50),
        "Engcobo": (-31.67, 28.00), "Umtata": (-31.58, 28.78),
        "Qumbu": (-31.16, 28.86), "Mount Frere": (-30.90, 28.99),
        "Mount Ayliff": (-30.80, 29.36), "Flagstaff": (-31.08, 29.50),
        "Lusikisiki": (-31.36, 29.59), "Port St Johns": (-31.62, 29.53),
        "Bizana": (-30.85, 29.85), "Libode": (-31.53, 28.97),
        "Ngqeleni": (-31.67, 29.03), "Port Alfred": (-33.60, 26.88),
        "Bathurst": (-33.49, 26.82), "Kent-on-Sea": (-33.68, 26.68),
        "Jeffreys Bay": (-34.04, 24.92), "Humansdorp": (-34.03, 24.77),
        "St Francis Bay": (-34.16, 24.83), "Kareedouw": (-33.95, 24.29),
        "Joubertina": (-33.82, 23.84), "Cradock": (-32.16, 25.61),
        "Graaff-Reinet": (-32.25, 24.54), "Somerset East": (-32.72, 25.58),
        "Fort Beaufort": (-32.78, 26.63), "Alice": (-32.79, 26.83),
        "Adelaide": (-32.70, 26.29), "Bedford": (-32.67, 26.08),
        "Tarkastad": (-32.01, 26.26), "Molteno": (-31.39, 26.36),
        "Burgersdorp": (-30.99, 26.32), "Aliwal North": (-30.69, 26.71),
        "Sterkstroom": (-31.55, 26.55), "Elliot": (-31.33, 27.85),
        "Maclear": (-31.07, 28.35), "Tsolo": (-31.28, 28.74),
        "Ugie": (-31.20, 28.24), "Mthatha": (-31.58, 28.78),
    },
    "Free State": {
        "Bloemfontein": (-29.12, 26.21), "Welkom": (-27.97, 26.73),
        "Bethlehem": (-28.23, 28.31), "Sasolburg": (-26.81, 27.82),
        "Kroonstad": (-27.65, 27.23), "Parys": (-26.90, 27.45),
        "Virginia": (-28.10, 26.87), "Odendaalsrus": (-27.87, 26.70),
        "Hennenman": (-27.97, 27.03), "Ventersburg": (-28.08, 27.14),
        "Winburg": (-28.52, 27.01), "Senekal": (-28.32, 27.61),
        "Ficksburg": (-28.87, 27.88), "Clocolan": (-28.91, 27.57),
        "Fouriesburg": (-28.58, 28.21), "Harrismith": (-28.27, 29.12),
        "Warden": (-27.85, 28.98), "Vrede": (-27.43, 29.16),
        "Memel": (-27.68, 29.57), "Frankfort": (-27.28, 28.51),
        "Villiers": (-27.03, 28.60), "Vredefort": (-26.99, 27.38),
        "Koppies": (-27.23, 27.57), "Heilbron": (-27.28, 27.97),
        "Lindley": (-27.88, 28.11), "Reitz": (-27.80, 28.42),
        "Petrus Steyn": (-27.65, 28.13), "Tweeling": (-27.55, 28.51),
        "Edenville": (-27.55, 27.69), "Steynsrus": (-27.95, 27.55),
        "Bothaville": (-27.38, 25.60), "Viljoenskroon": (-27.21, 26.95),
        "Wesselsbron": (-27.85, 25.61), "Hoopstad": (-27.83, 25.91),
        "Bultfontein": (-28.28, 25.73), "Theunissen": (-28.40, 26.72),
        "Brandfort": (-28.70, 26.46), "Dewetsdorp": (-29.59, 26.66),
        "Wepener": (-29.73, 27.03), "Zastron": (-30.30, 27.08),
        "Smithfield": (-30.21, 26.53), "Rouxville": (-30.42, 26.83),
        "Ladybrand": (-29.19, 27.46), "Excelsior": (-28.94, 27.07),
        "Marquard": (-28.66, 27.43), "Clocolan": (-28.91, 27.57),
        "Thaba Nchu": (-29.21, 26.83), "Botshabelo": (-29.23, 26.71),
        "Mangaung": (-29.12, 26.21), "Fauresmith": (-29.75, 25.31),
        "Jagersfontein": (-29.76, 25.42), "Koffiefontein": (-29.40, 25.00),
        "Philippolis": (-30.26, 25.27), "Trompsburg": (-30.01, 25.78),
        "Edenburg": (-29.51, 25.93), "Reddersburg": (-29.65, 26.16),
    },
    "Mpumalanga": {
        "Mbombela": (-25.47, 30.97), "eMalahleni": (-25.87, 29.23),
        "Secunda": (-26.55, 29.17), "Middelburg": (-25.77, 29.46),
        "Nelspruit": (-25.47, 30.97), "White River": (-25.33, 31.01),
        "Hazyview": (-25.03, 31.13), "Barberton": (-25.79, 31.05),
        "Lydenburg": (-25.10, 30.45), "Sabie": (-25.10, 30.78),
        "Graskop": (-24.93, 30.84), "Pilgrim's Rest": (-24.90, 30.76),
        "Bushbuckridge": (-24.84, 31.07), "Acornhoek": (-24.60, 31.08),
        "Thulamahashe": (-24.73, 31.19), "Mkhuhlu": (-24.96, 31.25),
        "Kanyamazane": (-25.45, 31.17), "KaNyamazane": (-25.45, 31.17),
        "Kabokweni": (-25.35, 31.14), "Nsikazi": (-25.40, 31.10),
        "Standerton": (-26.93, 29.24), "Bethal": (-26.45, 29.46),
        "Ermelo": (-26.53, 29.98), "Piet Retief": (-27.01, 30.80),
        "Volksrust": (-27.37, 29.88), "Amersfoort": (-26.99, 29.87),
        "Carolina": (-26.06, 30.11), "Badplaas": (-25.95, 30.57),
        "Machadodorp": (-25.67, 30.25), "Waterval Boven": (-25.64, 30.33),
        "Dullstroom": (-25.42, 30.11), "Belfast": (-25.69, 29.99),
        "Delmas": (-26.14, 28.68), "Ogies": (-26.05, 29.05),
        "Kriel": (-26.25, 29.25), "Kinross": (-26.42, 29.09),
        "Evander": (-26.48, 29.10), "Leandra": (-26.37, 28.92),
        "Balfor": (-26.67, 28.69), "Greylingstad": (-26.75, 28.77),
        "Komatipoort": (-25.43, 31.95), "Malelane": (-25.48, 31.52),
        "Hectorspruit": (-25.43, 31.68), "Marloth Park": (-25.35, 31.78),
        "Skukuza": (-24.99, 31.59), "Kruger National Park": (-24.99, 31.59),
    },
    "North West": {
        "Mahikeng": (-25.86, 25.64), "Rustenburg": (-25.66, 27.24),
        "Klerksdorp": (-26.85, 26.66), "Potchefstroom": (-26.71, 27.10),
        "Brits": (-25.63, 27.78), "Hartbeespoort": (-25.75, 27.90),
        "Mooinooi": (-25.73, 27.56), "Marikana": (-25.70, 27.47),
        "Mogwase": (-25.27, 27.18), "Phokeng": (-25.58, 27.17),
        "Sun City": (-25.34, 27.09), "Swartruggens": (-25.69, 26.69),
        "Zeerust": (-25.54, 26.08), "Lichtenburg": (-26.15, 25.80),
        "Coligny": (-26.33, 25.68), "Delareyville": (-26.68, 25.46),
        "Schweizer-Reneke": (-27.18, 25.33), "Wolmaransstad": (-26.88, 25.60),
        "Bloemhof": (-27.65, 25.60), "Christiana": (-27.92, 25.16),
        "Vryburg": (-26.95, 24.73), "Taung": (-27.53, 24.77),
        "Ganyesa": (-26.59, 24.16), "Tosca": (-25.88, 23.99),
        "Stella": (-26.55, 25.20), "Setlagole": (-26.28, 25.27),
        "Madikwe": (-24.76, 26.47), "Groot Marico": (-25.58, 26.40),
        "Ventersdorp": (-26.32, 26.81), "Fochville": (-26.49, 27.49),
        "Carletonville": (-26.36, 27.40), "Orkney": (-26.98, 26.67),
        "Stilfontein": (-26.84, 26.76), "Hartbeesfontein": (-26.74, 25.93),
        "Ottosdal": (-26.82, 25.96), "Koster": (-25.86, 26.89),
        "Sannieshof": (-26.53, 25.80), "Mafikeng": (-25.86, 25.64),
    },
    "Northern Cape": {
        "Kimberley": (-28.73, 24.76), "Upington": (-28.45, 21.25),
        "Springbok": (-29.66, 17.88), "De Aar": (-30.65, 24.01),
        "Kuruman": (-27.45, 23.43), "Kathu": (-27.70, 23.05),
        "Postmasburg": (-28.33, 23.07), "Danielskuil": (-28.19, 23.54),
        "Olifantshoek": (-27.96, 22.73), "Hotazel": (-27.20, 22.96),
        "Black Rock": (-27.12, 22.85), "Van Zylsrus": (-26.87, 22.05),
        "Kakamas": (-28.78, 20.61), "Keimoes": (-28.70, 20.97),
        "Augrabies": (-28.66, 20.42), "Pofadder": (-29.12, 19.39),
        "Aggeneys": (-29.28, 18.84), "Kleinzee": (-29.68, 17.06),
        "Port Nolloth": (-29.25, 16.87), "Alexander Bay": (-28.58, 16.48),
        "Hondeklip Bay": (-30.32, 17.27), "Garies": (-30.56, 17.99),
        "Kamieskroon": (-30.20, 17.93), "Nababeep": (-29.60, 17.78),
        "Okiep": (-29.60, 17.80), "Carolusberg": (-29.62, 17.94),
        "Concordia": (-29.55, 17.94), "Steinkopf": (-29.26, 17.73),
        "Vioolsdrif": (-28.77, 17.63), "Noupoort": (-31.19, 24.95),
        "Colesberg": (-30.72, 25.10), "Hanover": (-30.93, 24.53),
        "Philipstown": (-30.43, 24.47), "Petrusville": (-30.08, 24.66),
        "Vanderkloof": (-29.99, 24.73), "Luckhoff": (-29.73, 24.78),
        "Fauresmith": (-29.75, 25.31), "Jagersfontein": (-29.76, 25.42),
        "Koffiefontein": (-29.40, 25.00), "Jacobsdal": (-29.12, 25.75),
        "Griekwastad": (-28.85, 23.25), "Campbell": (-28.80, 23.73),
        "Douglas": (-29.05, 23.77), "Barkly West": (-28.54, 24.52),
        "Delportshoop": (-28.42, 24.68), "Warrenton": (-28.11, 24.85),
        "Jan Kempdorp": (-27.91, 24.83), "Hartswater": (-27.75, 24.81),
        "Pampierstad": (-27.78, 24.70), "Magareng": (-27.90, 24.80),
        "Sutherland": (-32.39, 20.66), "Fraserburg": (-31.92, 21.51),
        "Williston": (-31.35, 21.26), "Carnarvon": (-30.97, 22.13),
        "Loxton": (-31.47, 22.35), "Victoria West": (-31.40, 23.12),
        "Britstown": (-30.59, 23.50), "Strydenburg": (-29.95, 23.67),
        "Hopetown": (-29.62, 24.08), "Orania": (-29.81, 24.41),
        "Prieska": (-29.67, 22.74), "Marydale": (-29.40, 22.11),
        "Groblershoop": (-28.90, 21.99), "Boegoeberg": (-28.98, 21.99),
    },
}

def fetch_nasa_data(lat, lon):
    url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
    params = {"parameters": "ALLSKY_SFC_SW_DWN","community": "RE","longitude": lon,"latitude": lat,"format": "JSON"}
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        monthly = data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
        return [monthly[m] for m in months]
    except:
        return None

def calc_optimal_tilt(lat, month):
    declinations = [-20.9,-13.0,-2.4,9.4,18.8,23.1,21.2,13.5,2.2,-9.6,-18.9,-23.0]
    tilt = abs(lat) + declinations[month] * 0.5
    return max(5, min(45, tilt))

# UI
col1, col2 = st.columns([1,2])

with col1:
    province = st.selectbox("1. Choose Province", list(PROVINCES.keys()))
    town = st.selectbox("2. Choose Town", list(PROVINCES[province].keys()))

    if st.checkbox("Use Custom Coordinates?"):
        lat = st.number_input("Latitude", -35.0, -22.0, -28.78)
        lon = st.number_input("Longitude", 16.0, 33.0, 32.09)
        loc_name = f"Custom ({lat:.2f}, {lon:.2f})"
    else:
        lat, lon = PROVINCES[province][town]
        loc_name = f"{town}, {province}"

    st.metric("Latitude", f"{lat:.2f}°")
    st.metric("Longitude", f"{lon:.2f}°")

    # NEW: SYSTEM SIZE
    st.divider()
    st.subheader("⚙️ Your System")
    system_kw = st.number_input("System Size (kW)", 1.0, 100.0, 5.0, step=0.5)
    st.caption("Example: 5kW = ~10 x 500W panels")
    panel_efficiency = st.slider("System Efficiency %", 70, 95, 85) / 100
    days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
    electricity_price = st.number_input("Eskom Price (R/kWh)", 1.0, 10.0, 3.50, step=0.1)

    if st.button("Fetch NASA Data & Calculate", type="primary"):
        with st.spinner("Contacting NASA POWER..."):
            nasa_data = fetch_nasa_data(lat, lon)
        st.session_state['nasa'] = nasa_data
        st.session_state['lat'] = lat
        st.session_state['loc'] = loc_name
        st.session_state['system_kw'] = system_kw
        st.session_state['eff'] = panel_efficiency
        st.session_state['price'] = electricity_price

with col2:
    if 'nasa' in st.session_state:
        nasa = st.session_state['nasa']
        lat = st.session_state['lat']
        system_kw = st.session_state.get('system_kw', 5.0)
        eff = st.session_state.get('eff', 0.85)
        price = st.session_state.get('price', 3.50)

        if nasa is None:
            st.warning("NASA offline - using estimated SA average.")
            nasa = [5.8,5.9,5.5,4.8,4.2,3.9,4.0,4.6,5.2,5.6,5.7,5.9]
        else:
            st.success("Real NASA data loaded!")

        tilts = [calc_optimal_tilt(lat, i) for i in range(12)]
        month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        days = [31,28,31,30,31,30,31,31,30,31,30,31]
        fixed_tilt = sum(tilts)/12

        # --- NEW: FIXED vs MONTHLY ADJUSTED CALCULATION ---
        # Physics: if your tilt is off by X degrees, you lose ~ 0.4% per degree squared (approx)
        # Adjusted = perfect tilt every month = 100% of NASA sun
        # Fixed = small loss when optimal tilt != fixed tilt

        fixed_yield = []
        adjusted_yield = []
        gain_kwh = []

        for i in range(12):
            # Adjusted: full NASA value
            adj_month = nasa[i] * system_kw * days[i] * eff
            # Fixed: loss factor based on tilt error
            tilt_error = abs(tilts[i] - fixed_tilt)
            loss_factor = 1 - (0.004 * tilt_error)  # ~0.4% loss per degree off
            # Also small winter penalty if tilt far off
            fixed_month = adj_month * loss_factor

            adjusted_yield.append(adj_month)
            fixed_yield.append(fixed_month)
            gain_kwh.append(adj_month - fixed_month)

        total_fixed = sum(fixed_yield)
        total_adjusted = sum(adjusted_yield)
        total_gain = total_adjusted - total_fixed
        gain_pct = (total_gain / total_fixed * 100) if total_fixed > 0 else 0
        rand_gain = total_gain * price

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fixed Tilt", f"{fixed_tilt:.1f}°")
        m2.metric("Fixed - Yearly", f"{total_fixed:,.0f} kWh")
        m3.metric("Adjusted - Yearly", f"{total_adjusted:,.0f} kWh")
        m4.metric("Extra by Adjusting", f"+{total_gain:,.0f} kWh / +{gain_pct:.1f}%")

        # Chart 1: NASA
        fig, ax = plt.subplots()
        ax.bar(month_names, nasa, color="#FF6A00")
        ax.set_ylabel("Solar Energy (kWh/m2/day)")
        ax.set_title(f"NASA Real Data for {st.session_state['loc']}")
        st.pyplot(fig)

        # Chart 2: Tilt
        fig2, ax2 = plt.subplots()
        ax2.plot(month_names, tilts, marker='o', color="#0A1931", linewidth=3)
        ax2.axhline(fixed_tilt, color="#FF6A00", linestyle="--", label=f"Fixed {fixed_tilt:.1f}°")
        ax2.set_ylabel("Optimal Tilt (°)")
        ax2.set_title("Optimal Tilt by Month vs Fixed Tilt")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)

        # Chart 3: NEW - Fixed vs Adjusted kWh per month
        fig3, ax3 = plt.subplots(figsize=(10,4))
        x = range(12)
        ax3.bar([i-0.2 for i in x], fixed_yield, width=0.4, label="Fixed Tilt", color="#0A1931")
        ax3.bar([i+0.2 for i in x], adjusted_yield, width=0.4, label="Monthly Adjusted", color="#FF6A00")
        ax3.set_xticks(list(x))
        ax3.set_xticklabels(month_names)
        ax3.set_ylabel(f"kWh per Month ({system_kw:.1f}kW system)")
        ax3.set_title("Fixed vs Monthly Adjusted - Energy You Actually Get")
        ax3.legend()
        st.pyplot(fig3)

        # NEW TABLE: Full Comparison
        st.subheader("📊 Fixed vs Adjusted - Full Breakdown")
        st.dataframe({
            "Month": month_names,
            "NASA Sun": [f"{v:.2f}" for v in nasa],
            "Optimal Tilt (°)": [f"{t:.1f}" for t in tilts],
            "Fixed kWh": [f"{v:,.0f}" for v in fixed_yield],
            "Adjusted kWh": [f"{v:,.0f}" for v in adjusted_yield],
            "Extra Gain (kWh)": [f"+{v:,.0f}" for v in gain_kwh],
        }, use_container_width=True)

        # NEW: RECOMMENDATION BOX
        st.divider()
        st.subheader("💡 Recommendation")
        if gain_pct < 2:
            rec = f"**Keep it FIXED at {fixed_tilt:.1f}°.** You only gain {total_gain:,.0f} kWh/year ({gain_pct:.1f}%) by adjusting every month — not worth climbing on the roof 12 times! Save time, keep fixed."
        elif gain_pct < 5:
            rec = f"**FIXED at {fixed_tilt:.1f}° is best for most people.** Adjusting gives you +{total_gain:,.0f} kWh/year (R{rand_gain:,.0f}/year). Only adjust 2x per year: Summer tilt {sum(tilts[9:]+tilts[:3])/6:.1f}° (Sep-Feb) and Winter tilt {sum(tilts[3:9])/6:.1f}° (Mar-Aug) to get most of the gain."
        else:
            rec = f"**Adjust if you can!** You gain +{total_gain:,.0f} kWh/year (R{rand_gain:,.0f}/year) by adjusting monthly. Best: Change tilt at start of each month to the value in the table."

        st.info(f"""
**For {st.session_state['loc']} with {system_kw:.1f}kW system:**

- **Fixed Tilt {fixed_tilt:.1f}° facing North:** {total_fixed:,.0f} kWh/year = R{total_fixed*price:,.0f} saved/year
- **Monthly Adjusted:** {total_adjusted:,.0f} kWh/year = R{total_adjusted*price:,.0f} saved/year
- **Difference:** +{total_gain:,.0f} kWh = +R{rand_gain:,.0f} every year

{rec}
""")
    else:
        st.info("👈 Select Province → Town → System Size and click to fetch real NASA data.")

st.divider()
st.caption("Data: NASA POWER ALLSKY_SFC_SW_DWN. Model: Fixed vs Adjusted calculation by ModelForge Hub V1.3 - From Equation to Impact.")
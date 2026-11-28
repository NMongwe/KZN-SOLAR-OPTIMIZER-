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

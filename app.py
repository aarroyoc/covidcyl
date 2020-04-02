
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import altair as alt
import datetime
import math
import tempfile
import requests
from pathlib import Path

# Get Data

DATA_URL = "https://analisis.datosabiertos.jcyl.es/explore/dataset/tasa-enfermos-acumulados-por-areas-de-salud/download/?format=csv&timezone=Europe/Berlin&lang=es&use_labels_for_header=true&csv_separator=%3B"

date = datetime.date.today()
tmp_dir = Path(tempfile.gettempdir())
tmp_file = tmp_dir / f"coronavirus-{date.year}-{date.month}-{date.day}.csv"
if not tmp_file.exists():
    r = requests.get(DATA_URL)
    if r.status_code != 200:
        print(f"ERROR: Invalid URL: {DATA_URL}")
    with tmp_file.open("wb") as f:
        f.write(r.content)

st.title("Casos sospechosos de coronavirus por centro de salud")

df = pd.read_csv(str(tmp_file), sep=";")
df["FECHA"] = pd.to_datetime(df["FECHA"])
centros = df["CENTRO"].unique().tolist()
centros.sort()
centro_salud = st.selectbox("Centro de Salud", centros)
filtered = df[df["CENTRO"] == centro_salud]
total = filtered["TOTALENFERMEDAD"].sum()
st.write(f"Casos totales: {total}")

filtered = filtered.sort_values(by="FECHA")
filtered["ACUMULADOS"] = filtered["TOTALENFERMEDAD"].cumsum()

st.write("Casos nuevos al día")
c = alt.Chart(filtered).mark_line().encode(
    x=alt.X('FECHA:T', axis = alt.Axis(title = 'Fecha', format = ("%-d/%-m"))),
    y=alt.Y('TOTALENFERMEDAD:Q', axis= alt.Axis(title = "Casos nuevos"))
)
st.altair_chart(c, use_container_width=True)

st.write("Casos acumulados")
d = alt.Chart(filtered).mark_line().encode(
    x=alt.X('FECHA:T', axis = alt.Axis(title = 'Fecha', format = ("%-d/%-m"))),
    y=alt.Y('ACUMULADOS', axis= alt.Axis(title = "Casos acumulados"))
)
st.altair_chart(d, use_container_width=True)

st.write("Centros de salud con más casos")
total_centros = df.groupby("CENTRO", as_index=False).sum()
top_centros = total_centros.nlargest(10, "TOTALENFERMEDAD")
st.write(top_centros[["CENTRO", "TOTALENFERMEDAD"]])

total_cyl = df["TOTALENFERMEDAD"].sum()
st.write(f"Casos sospechosos totales en Castilla y León: {total_cyl}")

a = df["FECHA"].max()
gdf = df[df["FECHA"] == a][["x_geo", "y_geo", "CENTRO"]]
gdf = pd.merge(gdf, total_centros, on="CENTRO", how="left")

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=41.65,
        longitude=-4.72,
        zoom=11,
        pitch=40,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            gdf,
            radius=500,
            extruded=True,
            elevation_scale=10,
            get_color_weight="TOTALENFERMEDAD",
            get_elevation_weight="TOTALENFERMEDAD",
            get_position='[x_geo_x, y_geo_x]'
        ),
    ],
))


st.markdown("Autor: [Adrián Arroyo Calle](https://blog.adrianistan.eu)")
st.write("Datos procedentes de la Junta de Castilla y León")
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

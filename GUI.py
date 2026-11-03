from main import calc_plot_values, analyse_height
import streamlit as st
import math as m
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go


#natuur constantes
gasconstante = 287.05 # joule per kilogram kelvin
valversnelling = 9.81 # meter per seconde kwadraat

# rocket setup
rocket_drag_coefficient = 0.5 # to be defined
parachute_drag_coefficient = 0.8 # approximatly

# locatie setup
def_lat = 52.36
def_lon = 4.92

if "marker_location" not in st.session_state:
    st.session_state.marker_location = [def_lat, def_lon]  # default
    st.session_state.zoom = 14  # default

st.set_page_config(layout="wide")

st.write("""
# R.A.T.S.
Rocket Altitude and Trajectory Simulation
""")

col1, col2 = st.columns([2, 1], gap="large")

# possible to make is seperate scroll: .container(height=500)
with col2:
    st.write("## Rocket Setup")

    rocket_weight = st.slider(
        "massa (Kg)",
        value=0.6, 
        on_change="rerun",
        min_value=0.01,
        max_value=3.0,
        step=0.01,
    )
    rocket_length = st.slider(
        "lengte (m)",
        value=0.69, 
        on_change="rerun",
        min_value=0.01,
        max_value=3.0,
        step=0.01,
    )
    rocket_d_mm = st.slider(
        "diameter (mm)",
        value=75,
        on_change="rerun",
        min_value=10,
        max_value=100,
        step=5,
    )

    rocket_diameter = rocket_d_mm / 1000

    rocket_surface = m.pi * (rocket_diameter/2)**2 # eerst 4.42e-3

    has_parachute = st.toggle(
        "Contains a parachute",
        on_change="rerun",
        value=True,
        disabled=False,
    )

    if has_parachute:
        parachute_diameter = st.slider(
            "diameter (m)",
            value=0.45,
            on_change="rerun",
            min_value=0.1,
            max_value=1.0,
            step=0.05,
        )
    else:
        parachute_diameter = st.slider(
            "diameter (m)",
            value=0.45,
            on_change="rerun",
            min_value=0.1,
            max_value=1.0,
            step=0.05,
            disabled=True,
        )


    parachute_surface = m.pi * (parachute_diameter/2)**2 # eerst 1.59e-1
    with st.expander("Moter settings"): #.popover() or .expander() ???
        fuel_weight = st.slider(
            "fuel weight (kg)",
            value=0.028,
            on_change="rerun",
            min_value=0.01,
            max_value=0.1,
            step=0.001,
        )
        brandtijd = st.slider(
            "burn time (s)",
            value=2.2,
            on_change="rerun",
            min_value=0.1,
            max_value=10.0,
            step=0.1,
        )
        if has_parachute:
            delaytime = st.slider(
                "delay time (s)",
                value=5.0,
                on_change="rerun",
                min_value=0.0,
                max_value=10.0,                    
                step=0.1,
            ) 
        else:
            delaytime = st.slider(
                "delay time (s)",
                value=5.0,
                on_change="rerun",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                disabled=True,
            )
        skip_lines = st.number_input(
            "skip lines in motor curve file",
            value=4,
            on_change="rerun",
            min_value=0,
            max_value=10,
            step=1,
        )

        motor_curve_file = st.file_uploader(
            "Upload Motor Curve File", 
            type="csv", 
            accept_multiple_files=False, 
            on_change="rerun", 
        )

        if motor_curve_file is None:
            motor_curve_file = "TSP_E20.csv" # default file if none is uploaded
            st.write("Using default: TSP_E20.csv")
        else:
            st.write("Using uploaded file:", motor_curve_file.name)

    with st.expander("Location settings"):
        m = folium.Map(location=st.session_state.marker_location, zoom_start=st.session_state.zoom)

        marker = folium.Marker(
            location=st.session_state.marker_location,
            draggable=False
        )
        marker.add_to(m)

        map = st_folium(m, width=400, height=400, key="folium_map", wrap_longitude=True)

        if map.get("last_clicked"):
            lat = (map["last_clicked"]["lat"])
            lng = (map["last_clicked"]["lng"])
            st.session_state.marker_location = [lat, lng]
            st.session_state.latitude = lat
            st.session_state.longitude = lng
            st.session_state.zoom = map["zoom"]

            m = folium.Map(location=st.session_state.marker_location, zoom_start=st.session_state.zoom)
            folium.Marker(
                location=st.session_state.marker_location,
                draggable=False
            ).add_to(m)
            map = st_folium(m, width=400, height= 400, key="folium_map", wrap_longitude=True)

        if "longitude" in st.session_state:
            latitude, longitude = st.session_state.marker_location
        else:
            latitude = def_lat
            longitude = def_lon

        st.write(f"Coordinates: {st.session_state.marker_location}")
        

    with st.expander("graph colors"):
        prediction_color = st.color_picker(
            "Prediction color:", 
            value="#FF0000", 
            on_change="rerun",
        )
        trajectory_color = st.color_picker(
            "Trajectory color:", 
            value="#001FFF", 
            on_change="rerun",
            disabled=True,
        )

df, df2, df3 = calc_plot_values(rocket_weight, valversnelling, gasconstante, rocket_surface, rocket_drag_coefficient, parachute_drag_coefficient, fuel_weight, brandtijd, delaytime, parachute_surface, rocket_length, has_parachute, motor_curve_file, prediction_color, skip_lines, latitude, longitude)

Tdf = analyse_height("TestData.csv", trajectory_color)

fig = px.line_3d(
    df, x="x", 
    y="y", 
    z="z", 
    title="Positie",
    color_discrete_sequence=[prediction_color],
)

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df2['t'],
    y=df2['h'],
    mode='lines',
    name='Prediction',
    line=dict(color=prediction_color)
))
fig2.add_trace(go.Scatter(
    x=Tdf['t'],
    y=Tdf['h'],
    mode='lines',
    name='Trajectory',
    line=dict(color=trajectory_color)
))

px.line(
    df2, 
    x="t", 
    y="h", 
    title="Hoogte",
    color_discrete_sequence=[prediction_color],
)

fig3 = px.line(
    df3, 
    x="t", 
    y="v",
    title="Snelheid",
    color_discrete_sequence=[prediction_color],
)

with col1:
    st.write("## Simulation Output")
    tab1, tab2, tab3 = st.tabs(["3D positie", "2D hoogte", "2D snelheid"])
    with tab1:
        st.plotly_chart(fig, width="stretch")
    with tab2:
        st.plotly_chart(fig2, width="stretch")
    with tab3:
        st.plotly_chart(fig3, width="stretch")

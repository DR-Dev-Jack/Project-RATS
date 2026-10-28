from main import calc_plot_values
import streamlit as st
import math as m

#natuur constantes
gasconstante = 287.05 # joule per kilogram kelvin
valversnelling = 9.81 # meter per seconde kwadraat

# rocket setup
rocket_weight = 0.6 # kilogram of 0.15 voor de cartoon rocket, aanpasbaar
rocket_length = 0.69 # meter of 0.15 voor de cartoon rocket, aanpasbaar
rocket_drag_coefficient = 0.5 # to be defined
parachute_drag_coefficient = 0.8 # approximatly

rocket_diameter = 7.5e-2 # diameter in meter aanpasbaar
parachute_diameter = 4.5e-1 # diameter in meter aanpasbaar

rocket_surface = m.pi * (rocket_diameter/2)**2 # eerst 4.42e-3
parachute_surface = m.pi * (parachute_diameter/2)**2 # eerst 1.59e-1

#fuel setup
fuel_weight = 0.028 # still in kilograms and 0.024 for the D12
brandtijd = 2.2 # seconden
delaytime = 5.0 # seconden

st.write("""
# R.A.T.S.
Rocket Altitude and Trajectory Simulation
""")

rocket_weight = st.slider(
    "massa (Kg)",
    value=0.6, 
    on_change="rerun",
    min_value=0.01,
    max_value=3.0,
    step=0.01,
)

fig = calc_plot_values(rocket_weight, valversnelling, gasconstante, rocket_surface, rocket_drag_coefficient, parachute_drag_coefficient, fuel_weight, brandtijd, delaytime, parachute_surface, rocket_length)

st.plotly_chart(fig, use_container_width=True)

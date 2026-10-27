import numpy as np
import plotly.express as px
import streamlit as st


# 1. Define a function that takes a parameter and returns a Plotly figure
def plot_sine_wave(frequency):
  x = np.linspace(0, 10, 500)
  y = np.sin(frequency * x)

  fig = px.line(
      x=x, y=y, title=f"Sine Wave with Frequency = {frequency}"
  )
  fig.update_layout(xaxis_title="X", yaxis_title="Y")
  return fig


# 2. Add a Streamlit slider widget
freq_value = st.slider(
    "Select Frequency",
    min_value=0.5,
    max_value=10.0,
    value=1.0,
    step=0.5,
)

# 3. Call the function with the slider input and plot it in Streamlit
fig = plot_sine_wave(freq_value)
st.plotly_chart(fig, use_container_width=True)

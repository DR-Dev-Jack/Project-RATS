import streamlit as st
import main as m


st.write("""
# My first app
Hello *world*!
""")

st.plotly_chart(m.fig)

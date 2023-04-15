import streamlit as st
import backend

start_loc = st.text_input(label="Start Point")
end_loc = st.text_input(label="End Point")
mode = st.selectbox(label="Mode", options=backend.TRANSPORT_MODES)

def render_directions(start_loc, end_loc, mode):
    st.write(backend.get_route_info(start_loc, end_loc, mode=mode))

search_button = st.button(label="Get Routes")
if search_button:
    render_directions(start_loc, end_loc, mode)
    

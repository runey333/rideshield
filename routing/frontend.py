import streamlit as st
import backend

start_loc = st.text_input(label="Start Point")
end_loc = st.text_input(label="End Point")
mode = st.selectbox(label="Mode", options=backend.TRANSPORT_MODES)

search_button = st.button(label="Get Routes")
if search_button:
    st.write(backend.retrieve_routes(start_loc, end_loc, mode=mode))
    

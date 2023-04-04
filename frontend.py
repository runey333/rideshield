import streamlit as st
import backend

start_loc = st.text_input(label="Start Point", value="Start Point")
start_button = st.button(label="Select Places")
if start_button:
    backend.retrieve_places(start_loc)

end_loc = st.text_input(label="End Point", value="End Point")
end_button = st.button(label="Select Places")
if end_button:
    backend.retrieve_place(end_loc)
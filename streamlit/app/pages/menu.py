import streamlit as st
from st_clickable_images import clickable_images

# Configuration de la page
st.set_page_config(page_title="Menu")

# Titre de la page
st.title("Veuillez choisir l'opérateur :")

# Boutons pour choisir l'opérateur
if st.button("ORANGE REUNION"):
    st.session_state.operator = "orange"
    st.switch_page("pages/orange.py")

if st.button("SRR"):
    st.session_state.operator = "sfr"
    st.switch_page("pages/srr.py")

if st.button("TELCO"):
    st.session_state.operator = "telco"
    st.switch_page("pages/telco.py")
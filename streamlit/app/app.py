import streamlit as st
from style import *

# Setup web page
st.set_page_config(
    page_title="Telephony DataViz App",
    page_icon="./streamlit/app/img/Icone.PNG",  # Path as string
)


# Charger le CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title and logo
st.markdown("<h1 style='text-align: center;'>Données Téléphoniques de La Réunion : Visualisez, Analysez, Décidez</h1>", unsafe_allow_html=True)
st.markdown('---')
st.image("./streamlit/app/img/LOGO.PNG", width=800)
st.markdown('---')

# Bouton centré
start_button = st.button("Démarrer l'application")
if start_button:
    st.switch_page("pages/menu.py")



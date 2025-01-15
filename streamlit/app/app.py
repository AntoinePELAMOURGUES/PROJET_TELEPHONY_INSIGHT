import streamlit as st


# Setup web page
st.set_page_config(
    page_title="Telephony DataViz App",
    page_icon="./streamlit/app/img/Icone.PNG",  # Path as string
)
# Importer la police et définir le style CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playwrite+IN:wght@100..400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Playwrite IN', sans-serif;
        font-size: 18px;
        font-weight: 500;
        color: #d8a824;
    }

    /* Centrer le bouton */
    div.stButton > button {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }

    </style>
""", unsafe_allow_html=True)

# Title and logo
# Title and logo
st.markdown("""
    <div style='text-align: center; color: #d8a824; font-family: "Playwrite IN", sans-serif; font-size: 24px;'>
        <h1>
            Données Téléphoniques de La Réunion 🇷🇪<br>
            <span style='color: #d8a824;'>Visualisez</span> 👀,<br>
            <span style='color: #d8a824;'>Analysez</span> 📈,<br>
            <span style='color: #d8a824;'>Décidez</span> ✔️
        </h1>
    </div>
""", unsafe_allow_html=True)
st.markdown('---')
st.image("./streamlit/app/img/LOGO.PNG", width=800)
st.markdown('---')

# Bouton centré
start_button = st.button("Démarrer l'application")
if start_button:
    st.switch_page("pages/menu.py")



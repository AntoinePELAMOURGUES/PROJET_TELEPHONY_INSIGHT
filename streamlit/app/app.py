import streamlit as st

# Setup web page
st.set_page_config(
    page_title="Telephony DataViz App",
    page_icon="/home/antoine/telephony_insight_project/streamlit/app/img/Icone.PNG",  # Path as string
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
    </style>
""", unsafe_allow_html=True)

# Title and logo
st.markdown("<h1 style='text-align: center;'>API DE VISUALISATION DES DONNÉES TELEPHONIQUES</h1>", unsafe_allow_html=True)
st.markdown('---')
st.image("/home/antoine/telephony_insight_project/streamlit/app/img/LOGO.PNG", width=1100)
st.markdown('---')
st.write('Created by Antoine PELAMOURGUES')

# Sidebar for operator selection
st.sidebar.write("CHOIX DE L'OPÉRATEUR:")
if st.sidebar.button("SRR"):
    st.switch_page("pages/srr.py")
if st.sidebar.button("ORANGE REUNION"):
    st.switch_page("pages/orange.py")
if st.sidebar.button("TELCO"):
    st.switch_page("pages/telco.py")

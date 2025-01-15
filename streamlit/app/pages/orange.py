import streamlit as st
from data.orre_preprocess_mt20 import *
import pandas as pd
from data.dataviz import *

# Réinitialiser la page si elle est chargée
if 'page' not in st.session_state:
    st.session_state.page = "orange"

# Page Title
if st.session_state.page == "orange":
    st.markdown("""
    <div style='text-align: center; color: #d8a824; font-family: "Playwrite IN", monospace; font-size: 18px;'>
        <h1>
            ORANGE REUNION
        </h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('---')

    st.write("Veuillez choisir le type de réquisition que vous souhaitez analyser :")

    left, right = st.columns(2)
    if left.button("MT20", use_container_width=True):
        st.session_state.page = "mt24"

    if right.button("MT24", use_container_width=True):
        st.session_state.page = "mt20"

# Logic for MT24 Page
if st.session_state.page == "mt24" or st.session_state.page == "mt20":

    st.write("Veuillez charger votre fichier csv :")

    uploaded_file_1 = st.file_uploader("Fichier contenant les communications", type="csv")

    if uploaded_file_1:
        try:
            df = preprocess_data(uploaded_file_1)
            # Ajouter une ligne horizontale
            st.markdown("---")
            st.write("ℹ️ La période complète de la FADET s'étend du {} au {}".format(df["Date"].min(), df["Date"].max()))
            st.markdown("---")
            st.write("📅 Vous pouvez modifier la période d'analyse ci-dessous :")
            # Ajouter un slider pour choisir la période
            start_date = st.date_input("Date de début", min_value=df["Date"].min(), max_value=df["Date"].max(), value = df["Date"].min())
            end_date = st.date_input("Date de fin", min_value=df["Date"].min(), max_value=df["Date"].max(), value= df["Date"].max())
            start_date = pd.to_datetime(start_date)  # Convertir en datetime
            end_date = pd.to_datetime(end_date)  # Convertir en datetime
            df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            st.markdown("---")
            st.write("Choisissez un filtre si besoin :")
            filter = st.selectbox("Filtrer par :", ["Sélectionner", "Correspondant", "IMEI", "IMSI", "Ville"])
            st.markdown("---")
            # Vérifier si un filtre a été sélectionné
            if filter != "Sélectionner":
                value_filter = st.text_input("Valeur à filtrer :")
                if value_filter:
                    # Appliquer le filtre en fonction de la sélection
                    df = df[df[filter].astype(str) == value_filter]
                    st.write(f"Voici un aperçu des données ayant pour filtre {filter} : {value_filter}")
            else:
                st.write("Voici un aperçu des données complètes sur la période choisie:")
            st.write(df[['Date','Abonné', 'Correspondant', "Type d'appel", 'Durée', 'Adresse', 'IMEI', 'IMSI']])
            st.markdown("---")
            st.write("Nombre de communications par correspondant (exclusion des n° spéciaux):")
            corr = count_corr(df)
            st.write(corr)
            st.markdown("---")
            st.write("Type de communication :")
            type_fig = count_phone_type(df)
            st.plotly_chart(type_fig)
            st.markdown("---")
            st.write("Nombre de communications par IMEI :")
            imei = count_IMEI(df)
            st.write(imei)
            st.markdown("---")
            st.write("Nombre de communications par IMSI :")
            imsi = count_IMSI(df)
            st.write(imsi)
            st.markdown("---")
            comm_histo_glo = comm_histo_global(df)
            st.plotly_chart(comm_histo_glo)
            comm_histo_month = comm_histo_monthly(df)
            st.plotly_chart(comm_histo_month)
            comm_histo_week = comm_histo_weekday(df)
            st.plotly_chart(comm_histo_week)
            comm_histo_h = comm_histo_hour(df)
            st.plotly_chart(comm_histo_h)
            st.markdown("---")
            st.write("Nombre de communications par adresse du relais :")
            adresse_co = adresse_count(df)
            st.write(adresse_co)
            st.markdown("---")
            scatter = scatter_plot_ville(df)
            st.plotly_chart(scatter)
            st.markdown("---")
            st.write("🌍 Cartographie des relais déclenchés :")
            adresse_co['Coordinates'] = adresse_co['Adresse'].apply(geocode_address_datagouv)
            adresse_co[['Latitude', 'Longitude']] = pd.DataFrame(adresse_co['Coordinates'].tolist(), index=adresse_co.index)
            carto = carto_orre(adresse_co)
            # Afficher les adresses non trouvées sous forme de puces
            if non_found_addresses:
                st.write("🔴 Adresses non trouvées :")
                for address in non_found_addresses:
                    st.markdown(f"• {address}")
            st.plotly_chart(carto)
            if st.button("Retour au menu principal"):
                # Option 1 : Vider le session_state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]  # Supprime toutes les clés dans session_state
                # Naviguer vers la page du menu principal
                st.switch_page("pages/menu.py")  # Retour au menu principal
        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {e}")


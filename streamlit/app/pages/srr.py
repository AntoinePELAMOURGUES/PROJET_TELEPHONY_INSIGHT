import streamlit as st
from data.srr_preprocess_mt24 import *
import pandas as pd
from data.dataviz import *

# Check if 'page' is in session state, if not initialize it
if 'page' not in st.session_state:
    st.session_state.page = "srr"  # Default page

# Page Title
if st.session_state.page == "srr":
    st.title("SRR")

    st.write("Veuillez choisir le type de réquisition que vous souhaitez analyser :")

    if st.button("MT24"):
        st.session_state.page = "mt24"  # Change page state

    if st.button("MT20"):  # Example for another option
        st.session_state.page = "mt20"  # Change to another page

# Logic for MT24 Page
if st.session_state.page == "mt24":
    st.write("Veuillez charger vos 2 fichiers xls :")

    uploaded_file_1 = st.file_uploader("Fichier contenant les communications", type="xls")
    uploaded_file_2 = st.file_uploader("Fichier contenant les localisations de relais", type="xls")

    if uploaded_file_1 and uploaded_file_2:
        df = preprocess_data(uploaded_file_1, uploaded_file_2)
        # Ajouter une ligne horizontale
        st.markdown("---")
        st.write("ℹ️ La période d'analyse est du {} au {}".format(df["Date"].min(), df["Date"].max()))
        st.markdown("---")
        st.write("📅 Vous pouvez modifier la période d'analyse ci-dessous :")
        # Ajouter un slider pour choisir la période
        start_date = st.date_input("Date de début", min_value=df["Date"].min(), max_value=df["Date"].max(), value = df["Date"].min())
        end_date = st.date_input("Date de fin", min_value=df["Date"].min(), max_value=df["Date"].max(), value= df["Date"].max())
        start_date = pd.to_datetime(start_date)  # Convertir en datetime
        end_date = pd.to_datetime(end_date)  # Convertir en datetime
        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        st.markdown("---")
        st.write("Filtrage sur un numéro :")
        num = st.text_input("Numéro à filtrer :")
        st.markdown("---")
        st.write("Voici un aperçu des données :")
        if num:
            df = df[(df["Correspondant"] == num)]
        st.write(df[['Date','Abonné', 'Correspondant', "Type d'appel", 'Durée', 'Adresse', 'IMEI', 'IMSI']])
        st.markdown("---")
        st.write("Nombre de communications par correspondant:")
        corr = count_corr(df)
        st.write(corr)
        st.markdown("---")
        st.write("Type de communication :")
        type_fig = count_phone_type(df)
        st.plotly_chart(type_fig)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Nombre de communications par IMEI :")
            imei = count_IMEI(df)
            st.write(imei)
        with col2:
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
        st.write("Nombre de communications par adresse :")
        adresse_co = adresse_count(df)
        st.write(adresse_co)
        st.markdown("---")
        scatter = scatter_plot_ville(df)
        st.plotly_chart(scatter)
        st.markdown("---")
        st.write("🌍 Cartographie des relais déclenchés :")
        carto = carto_adresse(df)
        st.plotly_chart(carto)

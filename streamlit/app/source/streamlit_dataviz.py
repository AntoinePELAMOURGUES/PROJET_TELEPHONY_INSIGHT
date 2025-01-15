import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pyproj import Proj, Transformer
import requests
import streamlit as st

# Fonction pour convertir les coordonnées Gauss-Laborde à WGS84
def gauss_laborde_to_wgs84(x, y):
    try:
        # Définir le système de projection Gauss-Laborde
        gauss_laborde = Proj(proj='tmerc', lat_0=-21.11666667, lon_0=55.53333333, k=1, x_0=160000, y_0=50000)
        # Définir le système de projection WGS84
        wgs84 = Proj(proj='latlong', datum='WGS84')
        # Créer un transformer pour convertir entre les deux systèmes
        transformer = Transformer.from_proj(gauss_laborde, wgs84)
        # Effectuer la transformation
        lon, lat = transformer.transform(x, y)
        return lat, lon
    except Exception as e:
        print(f"Erreur lors de la conversion des coordonnées: {e}")
        return None, None  # Retourner None en cas d'erreur

# Compter le nombre de communications par correspondant
def count_corr(df):
    try:
        # Compter le nombre de contacts par correspondant
        correspondant_counts = df['Correspondant'].value_counts().reset_index()
        correspondant_counts.columns = ['Correspondant', 'Nombre de communication']
        # Filtrer pour garder uniquement les correspondants ayant 11 ou 12 caractères
        correspondant_counts = correspondant_counts[correspondant_counts['Correspondant'].str.len().isin([11, 12])]
        total_contacts = correspondant_counts['Nombre de communication'].sum()
        # Calculer le pourcentage et arrondir à un chiffre après la virgule
        correspondant_counts['Pourcentage'] = ((correspondant_counts['Nombre de communication'] / total_contacts) * 100).round(1)
        # Trier par nombre de contacts du plus élevé au plus bas
        correspondant_counts = correspondant_counts.sort_values(by='Nombre de communication', ascending=False)
        return correspondant_counts
    except Exception as e:
        print(f"Erreur lors du comptage des correspondants: {e}")
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur

# Compter le nombre de communications par IMEI
def count_IMEI(df):
    try:
        imei_counts = df['IMEI'].value_counts().reset_index()
        imei_counts.columns = ['IMEI', 'Nombre de communication']
        return imei_counts
    except Exception as e:
        print(f"Erreur lors du comptage des IMEI: {e}")
        return pd.DataFrame()

# Compter le nombre de communications par IMSI
def count_IMSI(df):
    try:
        imsi_counts = df['IMSI'].value_counts().reset_index()
        imsi_counts.columns = ['IMSI', 'Nombre de communication']
        return imsi_counts
    except Exception as e:
        print(f"Erreur lors du comptage des IMSI: {e}")
        return pd.DataFrame()

# Compter le nombre de types d'appel et créer un graphique en secteurs
def count_phone_type(df):
    try:
        type_appel_counts = df["Type d'appel"].value_counts().reset_index()
        type_appel_counts.columns = ['Type d\'appel', 'Nombre']
        colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']  # Définir les couleurs pour le graphique
        fig = go.Figure(data=[go.Pie(labels=type_appel_counts['Type d\'appel'],
                                       values=type_appel_counts['Nombre'])])
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                          marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        return fig  # Retourner la figure Plotly
    except Exception as e:
        print(f"Erreur lors du comptage des types d'appel: {e}")
        return go.Figure()  # Retourner une figure vide en cas d'erreur

# Créer un histogramme global du nombre de communications par jour
def comm_histo_global(df):
    try:
        df['DateOnly'] = df['Date'].dt.date  # Extraire uniquement la date
        daily_counts = df.groupby('DateOnly').size().reset_index(name='Nombre de communications')
        daily_counts['DateOnly'] = pd.to_datetime(daily_counts['DateOnly'])  # Convertir en datetime
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_counts['DateOnly'],
            y=daily_counts['Nombre de communications'],
            marker=dict(line=dict(color='black', width=1))  # Bordure noire autour des barres
        ))
        fig.update_layout(
            title='Nombre de communications par jour',
            xaxis_title='Date',
            yaxis_title='Nombre de communications',
            xaxis=dict(tickformat='%Y-%m-%d'),  # Format des dates sur l'axe x
            showlegend=False  # Masquer la légende si non nécessaire
        )
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme global: {e}")
        return go.Figure()

# Créer un histogramme mensuel du nombre de communications par mois
def comm_histo_monthly(df):
    try:
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Histogram(x=df['Mois'].dropna().astype(str),
                                            histfunc='count',
                                            name='Communications par mois',
                                            marker=dict(line=dict(color='black', width=1))))
        fig_monthly.update_layout(title='Nombre de communications par mois',
                                   xaxis_title='Mois',
                                   yaxis_title='Nombre de communications')
        return fig_monthly
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme mensuel: {e}")
        return go.Figure()

# Créer un histogramme du nombre de communications par jour de la semaine
def comm_histo_weekday(df):
    try:
        fig_weekday = go.Figure()
        fig_weekday.add_trace(go.Histogram(x=df['Jour de la semaine'],
                                            histfunc='count',
                                            name='Communications par jour de la semaine',
                                            marker=dict(line=dict(color='black', width=1))))
        fig_weekday.update_layout(title='Nombre de communications par jour de la semaine',
                                   xaxis_title='Jour de la semaine',
                                   yaxis_title='Nombre de communications')
        return fig_weekday
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme par jour de la semaine: {e}")
        return go.Figure()

# Créer un histogramme du nombre de communications par heure
def comm_histo_hour(df):
    try:
        df['Date'] = pd.to_datetime(df['Date'])  # Convertir en datetime
        df['Hour'] = df['Date'].dt.hour  # Extraire l'heure
        fig = px.histogram(df, x='Hour', title='Nombre de communications par heure',
                           labels={'Hour': 'Heure', 'count': 'Nombre de communications'},
                           histnorm='')
        # Ajouter des bordures aux barres
        fig.update_traces(marker=dict(line=dict(color='black', width=1)))
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme par heure: {e}")
        return go.Figure()

# Compter le nombre d'appels par adresse et calculer les pourcentages associés
def adresse_count(df):
    try:
       adresse_counts = df['Adresse'].value_counts().reset_index()
       adresse_counts.columns = ['Adresse', 'Nombre de déclenchement']
       adresse_counts.dropna(axis=0, inplace=True)  # Supprimer les lignes sans adresse
       total_contacts = adresse_counts['Nombre de déclenchement'].sum()
       adresse_counts['Pourcentage'] = ((adresse_counts['Nombre de déclenchement'] / total_contacts) * 100).round(1)
       adresse_counts.sort_values(by='Nombre de déclenchement', ascending=False, inplace=True)
       return adresse_counts
    except Exception as e:
       print(f"Erreur lors du comptage des adresses: {e}")
       return pd.DataFrame()

# Créer un scatter plot basé sur les villes et les dates
def scatter_plot_ville(df):
    try:
       fig = px.scatter(df, x='Date', y='Ville', color='Ville', title='Localisation en fonction de la date')
       return fig
    except Exception as e:
       print(f"Erreur lors de la création du scatter plot des villes: {e}")
       return go.Figure()  # Retourner une figure vide en cas d'erreur

# Liste pour stocker les adresses non trouvées (à utiliser dans geocode_address_datagouv)
non_found_addresses = []

# Fonction pour géocoder une adresse via un service externe (API)
def geocode_address_datagouv(address):
    try:
       url = "https://data.geopf.fr/geocodage/search"
       params = {
           'q': address,
           'limit': 1  # Limiter à 1 résultat
       }
       response = requests.get(url, params=params)
       if response.status_code == 200:
           data = response.json()
           if data and 'features' in data and len(data['features']) > 0:
               coords = data['features'][0]['geometry']['coordinates']
               return (coords[1], coords[0])  # Retourner (latitude, longitude)
           else:
               non_found_addresses.append(address)  # Ajouter à la liste si non trouvé
               return (None, None)
       else:
           print(f"Erreur lors de la requête : {response.status_code}")
           return (None, None)
    except Exception as e:
       print(f"Erreur lors du géocodage de l'adresse '{address}': {e}")
       return (None, None)

# Créer une carte des adresses pour l'opérateur SRR avec les coordonnées converties depuis Gauss-Laborde à WGS84.
def carto_adresse_srr(df):
    try:
        adress_count = adresse_count(df)  # Compter les adresses
        df_merged = adress_count.merge(df, how='left', left_on="Adresse", right_on='Adresse')
        # Appliquer la conversion des coordonnées sur chaque ligne
        df_merged[['Latitude', 'Longitude']] = df_merged.apply(lambda row: gauss_laborde_to_wgs84(row['Coordonnée X'], row['Coordonnée Y']), axis=1, result_type='expand')
        fig = px.scatter_map(df_merged,
                            lat="Latitude", lon="Longitude",
                            color="Pourcentage", size="Nombre de déclenchement",
                            hover_name="Adresse", color_continuous_scale=px.colors.sequential.Bluered,
                            size_max=60, zoom=10,
                            map_style="carto-positron")
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de la carte des adresses: {e}")
        return go.Figure()

# Créer une carte des adresses pour l'opérateur ORRE.
def carto_adresse_orre(df):
    try:
        fig = px.scatter_map(df,
                            lat="Latitude", lon="Longitude",
                            color="Pourcentage", size="Nombre de déclenchement",
                            hover_name="Adresse", color_continuous_scale=px.colors.sequential.Bluered,
                            size_max=60, zoom=10,
                            map_style="carto-positron")
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de la carte ORRE: {e}")
        return go.Figure()

# Créer une carte des adresses pour l'opérateur TCOI.
def carto_adresse_tcoi(df):
    try:
        fig = px.scatter_map(df,
                            lat="Latitude", lon="Longitude",
                            color="Percentage", size="Count",
                            hover_name="Adresse", color_continuous_scale=px.colors.sequential.Bluered,
                            size_max=100, zoom=10,
                            map_style="carto-positron")
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de la carte des adresses: {e}")
        return go.Figure()

def visualisation_data(df, operateur: str):
    # Afficher la période complète de la FADET
    st.write("ℹ️ La période complète de la FADET s'étend du {} au {}".format(df["Date"].min(), df["Date"].max()))
    st.markdown("---")

    # Interface pour sélectionner la période d'analyse
    st.write("📅 Vous pouvez modifier la période d'analyse ci-dessous :")
    start_date = st.date_input("Date de début", min_value=df["Date"].min(), max_value=df["Date"].max(), value=df["Date"].min())
    end_date = st.date_input("Date de fin", min_value=df["Date"].min(), max_value=df["Date"].max(), value=df["Date"].max())

    # Conversion des dates en datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrer le DataFrame en fonction des dates sélectionnées
    df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
    st.markdown("---")

    # Interface pour appliquer un filtre supplémentaire
    st.write("Choisissez un filtre si besoin :")
    filter = st.selectbox("Filtrer par :", ["Sélectionner", "Correspondant", "IMEI", "IMSI", "Ville"])
    st.markdown("---")

    # Vérifier si un filtre a été sélectionné
    if filter != "Sélectionner":
        value_filter = st.selectbox(f"{filter} :", ['Sélectionner'] + list(df[filter].dropna().unique()))
        if value_filter != 'Sélectionner':
            st.markdown("---")
            # Appliquer le filtre en fonction de la sélection
            df = df[df[filter].astype(str) == value_filter]
            st.write(f"Voici un aperçu des données ayant pour filtre {filter} : {value_filter}")

    else:
        st.write("Voici un aperçu des données complètes sur la période choisie:")

    # Affichage des données filtrées
    st.write(df[['Date', 'Abonné', 'Correspondant', "Type d'appel", 'Durée', 'Adresse', 'IMEI', 'IMSI']])
    st.markdown("---")

    # Afficher le nombre de communications par correspondant (exclusion des n° spéciaux)
    st.write("Nombre de communications par correspondant (exclusion des n° spéciaux):")
    corr = count_corr(df)
    st.write(corr)
    st.markdown("---")

    # Afficher le type de communications
    st.write("Type de communications :")
    type_fig = count_phone_type(df)
    st.plotly_chart(type_fig)
    st.markdown("---")

    # Afficher le nombre de communications par IMEI et IMSI
    st.write("Nombre de communications par IMEI :")
    imei = count_IMEI(df)
    st.write(imei)

    st.markdown("---")

    st.write("Nombre de communications par IMSI :")
    imsi = count_IMSI(df)
    st.write(imsi)

    # Histogrammes des communications
    st.markdown("---")

    comm_histo_glo = comm_histo_global(df)
    st.plotly_chart(comm_histo_glo)

    comm_histo_month = comm_histo_monthly(df)
    st.plotly_chart(comm_histo_month)

    comm_histo_week = comm_histo_weekday(df)
    st.plotly_chart(comm_histo_week)

    comm_histo_h = comm_histo_hour(df)
    st.plotly_chart(comm_histo_h)

    # Nombre de communications par adresse du relais
    st.markdown("---")

    st.write("Nombre de communications par adresse du relais :")
    adresse_co = adresse_count(df)
    st.write(adresse_co)

    # Graphique scatter par ville
    st.markdown("---")

    scatter = scatter_plot_ville(df)
    st.plotly_chart(scatter)

    # Cartographie des relais déclenchés selon l'opérateur
    st.markdown("---")

    st.write("🌍 Cartographie des relais déclenchés :")

    if operateur == 'SRR':
        carto = carto_adresse_srr(df)
        st.plotly_chart(carto)

    elif operateur == "TCOI":
        # Supprimer les doublons dans df en fonction de l'adresse
        df_unique = df[['Adresse', 'Latitude', 'Longitude']].drop_duplicates()
        # Faire la jointure pour obtenir les coordonnées
        df_merged = adresse_co.merge(df_unique, on='Adresse', how='left')
        carto = carto_adresse_tcoi(df_merged)
        st.plotly_chart(carto)

    elif operateur == 'ORRE':
        adresse_co['Coordinates'] = adresse_co['Adresse'].apply(geocode_address_datagouv)
        # Vérifier si les coordonnées ont été trouvées avant d'ajouter les colonnes Latitude et Longitude
        if non_found_addresses:
            st.write("🔴 Adresses non trouvées :")
            for address in non_found_addresses:
                st.markdown(f"• {address}")
        if 'Coordinates' in adresse_co.columns:
            adresse_co[['Latitude', 'Longitude']] = pd.DataFrame(adresse_co['Coordinates'].tolist(), index=adresse_co.index)
        carto = carto_adresse_orre(adresse_co)
        non_found_addresses = []
        st.plotly_chart(carto)
        st.markdown("---")


   # Bouton pour retourner au menu principal
    if st.button("Retour au menu principal"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]  # Supprime toutes les clés dans session_state
        # Naviguer vers la page du menu principal
        st.switch_page("pages/menu.py")  # Retour au menu principal


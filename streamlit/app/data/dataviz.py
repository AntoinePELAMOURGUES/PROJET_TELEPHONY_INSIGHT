import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pyproj import Proj, Transformer
from geopy.geocoders import Photon
from geopy.extra.rate_limiter import RateLimiter
import requests

# Fonction pour convertir Gauss-Laborde à WGS84
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
        return None, None

def count_corr(df):
    try:
        # Compter le nombre de contacts par correspondant
        correspondant_counts = df['Correspondant'].value_counts().reset_index()
        # Renommer les colonnes pour plus de clarté
        correspondant_counts.columns = ['Correspondant', 'Nombre de communication']
        # Filtrer pour garder uniquement les correspondants ayant 11 ou 12 caractères
        correspondant_counts = correspondant_counts[correspondant_counts['Correspondant'].str.len().isin([11, 12])]
        # Calculer le nombre total de contacts
        total_contacts = correspondant_counts['Nombre de communication'].sum()
        # Calculer le pourcentage et arrondir à un chiffre après la virgule
        correspondant_counts['Pourcentage'] = ((correspondant_counts['Nombre de communication'] / total_contacts) * 100).round(1)
        # Trier par nombre de contacts du plus élevé au plus bas
        correspondant_counts = correspondant_counts.sort_values(by='Nombre de communication', ascending=False)
        return correspondant_counts
    except Exception as e:
        print(f"Erreur lors du comptage des correspondants: {e}")
        return pd.DataFrame()

def count_IMEI(df):
    try:
        # Compter le nombre de communications par IMEI
        imei_counts = df['IMEI'].value_counts().reset_index()
        # Renommer les colonnes pour plus de clarté
        imei_counts.columns = ['IMEI', 'Nombre de communication']
        return imei_counts
    except Exception as e:
        print(f"Erreur lors du comptage des IMEI: {e}")
        return pd.DataFrame()

def count_IMSI(df):
    try:
        # Compter le nombre de communications par IMEI
        imsi_counts = df['IMSI'].value_counts().reset_index()
        # Renommer les colonnes pour plus de clarté
        imsi_counts.columns = ['IMSI', 'Nombre de communication']
        return imsi_counts
    except Exception as e:
        print(f"Erreur lors du comptage des IMSI: {e}")
        return pd.DataFrame()

def count_phone_type(df):
    try:
        # Compter le nombre de types d'appel
        type_appel_counts = df["Type d'appel"].value_counts().reset_index()
        type_appel_counts.columns = ['Type d\'appel', 'Nombre']
        # Définir les couleurs pour le graphique
        colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']
        # Créer le graphique en secteurs
        fig = go.Figure(data=[go.Pie(labels=type_appel_counts['Type d\'appel'],
                                    values=type_appel_counts['Nombre'])])
        # Mettre à jour les traces du graphique
        fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                        marker=dict(colors=colors, line=dict(color='#000000', width=2)))
        return fig  # Retourner la figure Plotly
    except Exception as e:
        print(f"Erreur lors du comptage des types d'appel: {e}")
        return go.Figure()

def comm_histo_global(df):
    try:
        # Extraire uniquement la date
        df['DateOnly'] = df['Date'].dt.date
        # Compter le nombre de communications par date
        daily_counts = df.groupby('DateOnly').size().reset_index(name='Nombre de communications')
        # Convertir la colonne 'DateOnly' en datetime
        daily_counts['DateOnly'] = pd.to_datetime(daily_counts['DateOnly'])
        # Créer l'histogramme
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=daily_counts['DateOnly'],
            y=daily_counts['Nombre de communications'],
            marker=dict(line=dict(color='black', width=1))  # Bordure noire autour des barres
        ))
        # Mettre à jour la mise en page
        fig.update_layout(
            title='Nombre de communications par jour',
            xaxis_title='Date',
            yaxis_title='Nombre de communications',
            xaxis=dict(tickformat='%Y-%m-%d'),  # Format des dates sur l'axe x
        )
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme global: {e}")
        return go.Figure()

def comm_histo_monthly(df):
    try:
        # Histogramme par mois
        fig_monthly = go.Figure()
        fig_monthly.add_trace(go.Histogram(x=df['Mois'].dropna().astype(str), histfunc='count', name='Communications par mois',marker=dict(line=dict(color='black', width=1))))
        fig_monthly.update_layout(title='Nombre de communications par mois', xaxis_title='Mois', yaxis_title='Nombre de communications')
        return fig_monthly
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme mensuel: {e}")
        return go.Figure()

def comm_histo_weekday(df):
    try:
        # Histogramme par jour de la semaine
        fig_weekday = go.Figure()
        fig_weekday.add_trace(go.Histogram(x=df['Jour de la semaine'], histfunc='count', name='Communications par jour de la semaine', marker=dict(line=dict(color='black', width=1))))
        fig_weekday.update_layout(title='Nombre de communications par jour de la semaine', xaxis_title='Jour de la semaine', yaxis_title='Nombre de communications')
        return fig_weekday
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme par jour de la semaine: {e}")
        return go.Figure()

def comm_histo_hour(df):
    try:
        # Convertir la colonne 'Date' en datetime
        df['Date'] = pd.to_datetime(df['Date'])
        # Extraire l'heure de la date
        df['Hour'] = df['Date'].dt.hour
        # Créer l'histogramme par heure
        fig = px.histogram(df, x='Hour', title='Nombre de communications par heure',
                        labels={'Hour': 'Heure', 'count': 'Nombre de communications'},
                        histnorm='',)
        # Ajouter des bordures aux barres
        fig.update_traces(marker=dict(line=dict(color='black', width=1)))
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de l'histogramme par heure: {e}")
        return go.Figure()

def adresse_count(df):
    try:
        # Compter le nombre de contacts par correspondant
        adresse_counts = df['Adresse'].value_counts().reset_index()
        # Renommer les colonnes pour plus de clarté
        adresse_counts.columns = ['Adresse', 'Nombre de déclenchement']
        # Supprimer les lignes sans adresse
        adresse_counts = adresse_counts.dropna(axis=0)
        # Calculer le nombre total de contacts
        total_contacts = adresse_counts['Nombre de déclenchement'].sum()
        # Calculer le pourcentage et arrondir à un chiffre après la virgule
        adresse_counts['Pourcentage'] = ((adresse_counts['Nombre de déclenchement'] / total_contacts) * 100).round(1)
        # Trier par nombre de contacts du plus élevé au plus bas
        adresse_counts = adresse_counts.sort_values(by='Nombre de déclenchement', ascending=False)
        return adresse_counts
    except Exception as e:
        print(f"Erreur lors du comptage des adresses: {e}")
        return pd.DataFrame()

def carto_adresse(df):
    try:
        adress_count = adresse_count(df)
        df_merged = adress_count.merge(df, how = 'left', left_on="Adresse", right_on='Adresse')
        # Appliquer la fonction sur les colonnes 'Coordonnée X' et 'Coordonnée Y'
        df_merged[['Latitude', 'Longitude']] = df_merged.apply(lambda row: gauss_laborde_to_wgs84(row['Coordonnée X'], row['Coordonnée Y']), axis=1, result_type='expand')
        fig = px.scatter_map(df_merged, lat="Latitude", lon="Longitude", color="Pourcentage", size="Nombre de déclenchement", hover_name="Adresse",
                    color_continuous_scale=px.colors.sequential.Bluered, size_max=15, zoom=10,
                    map_style="carto-positron")
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de la carte des adresses: {e}")
        return go.Figure()

def scatter_plot_ville(df):
    try:
        fig = px.scatter(df, x= 'Date', y='Ville', color= 'Ville', title='Localisation en fonction de la date')
        return fig
    except Exception as e:
        print(f"Erreur lors de la création du scatter plot des villes: {e}")
        return go.Figure()

geolocator = Photon(user_agent="my_geocoder")

geocode_with_delay = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)

# Liste pour stocker les adresses non trouvées
non_found_addresses = []
# Fonction pour obtenir les coordonnées géographiques
def get_coordinates(address):
    try:
        location = geocode_with_delay(address)
        return (location.latitude, location.longitude) if location else non_found_addresses.append(address)
    except Exception as e:
        print(f"Erreur lors de la géocodage de l'adresse {address}: {e}")
        return (None, None)


def carto_orre(df):
    try:
        fig = px.scatter_map(df, lat="Latitude", lon="Longitude", color="Pourcentage", size="Nombre de déclenchement", hover_name="Adresse",
                        color_continuous_scale=px.colors.sequential.Bluered, size_max=15, zoom=10,
                        map_style="carto-positron")
        return fig
    except Exception as e:
        print(f"Erreur lors de la création de la carte ORRE: {e}")
        return go.Figure()

def geocode_address_datagouv(address):
    try:
        # URL du service de géocodage
        url = "https://data.geopf.fr/geocodage/search"

        # Paramètres de la requête
        params = {
            'q': address,
            'limit': 1  # Limiter à 1 résultat
        }

        # Envoyer la requête GET
        response = requests.get(url, params=params)

        # Vérifier si la requête a réussi
        if response.status_code == 200:
            data = response.json()
            # Vérifier si des résultats sont retournés
            if data and 'features' in data and len(data['features']) > 0:
                # Extraire les coordonnées
                coords = data['features'][0]['geometry']['coordinates']
                return (coords[1], coords[0])  # Retourner (latitude, longitude)
            else:
                non_found_addresses.append(address)
                return (None, None)  # Pas de résultats trouvés
        else:
            print(f"Erreur lors de la requête : {response.status_code}")
            return (None, None)
    except Exception as e:
        print(f"Erreur lors du géocodage de l'adresse '{address}': {e}")
        return (None, None)
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pyproj import Proj, Transformer

def preprocess_data(file1, file2):
    df1 = pd.read_excel(file1, usecols= ["Type d'appel", "Abonné", "Correspondant", "Date", "Durée", "CIREF", "IMEI", "IMSI"], dtype= {"Type d'appel": str, "Abonné": str, "Correspondant": str, "Durée": str, "CIREF": str, "IMEI": str, "IMSI": str})
    df2 = pd.read_excel(file2, usecols=["CIREF", "Adresse", "Comp. adresse", "Code postal", "Bureau Distributeur", "Coordonnée X", "Coordonnée Y"], dtype={"CIREF":str, "Adresse":str,"Code postal" :str, "Comp. adresse": str,  "Bureau Distributeur":str, "Coordonnée X": str, "Coordonnée Y": str})
    # Remplacer '0693' par '262693' dans les colonnes 'Abonné' et 'Correspondant'
    df1['Abonné'] = df1['Abonné'].replace(r'^0693', '262693', regex=True)
    df1['Correspondant'] = df1['Correspondant'].replace(r'^0693', '262693', regex=True)
    df1['Abonné'] = df1['Abonné'].replace(r'^0692', '262692', regex=True)
    df1['Correspondant'] = df1['Correspondant'].replace(r'^0692', '262692', regex=True)
    df1['Abonné'] = df1['Abonné'].replace(r'^06', '336', regex=True)
    df1['Correspondant'] = df1['Correspondant'].replace(r'^06', '336', regex=True)
    df1['Correspondant'] = df1['Correspondant'].replace(r'^07', '337', regex=True)
    df1['Correspondant'] = df1['Correspondant'].replace(r'^02', '2622', regex=True)
    # Remplacer les NaN par 'Data'
    df1['Abonné'] = df1['Abonné'].fillna('Data')
    df1['Correspondant'] = df1['Correspondant'].fillna('Data')
    # Création de colonne Anné, Mois, jour
    # Convertir la colonne 'Date' en datetime
    df1['Date'] = pd.to_datetime(df1['Date'])
    # Extraire l'année, le mois et le jour de la semaine
    df1['Années'] = df1['Date'].dt.year
    df1['Mois'] = df1['Date'].dt.month
    df1['Jour de la semaine'] = df1['Date'].dt.day_name()
    # Mapper les jours de la semaine en français
    jours_semaine_fr = {
        'Monday': 'Lundi',
        'Tuesday': 'Mardi',
        'Wednesday': 'Mercredi',
        'Thursday': 'Jeudi',
        'Friday': 'Vendredi',
        'Saturday': 'Samedi',
        'Sunday': 'Dimanche'
    }
    # Mapper les mois en français
    mois_fr = {
        1: 'Janvier',
        2: 'Février',
        3: 'Mars',
        4: 'Avril',
        5: 'Mai',
        6: 'Juin',
        7: 'Juillet',
        8: 'Août',
        9: 'Septembre',
        10: 'Octobre',
        11: 'Novembre',
        12: 'Décembre'
    }
    # Remplacer les numéros de mois par leur équivalent en français
    df1['Mois'] = df1['Mois'].map(mois_fr)
    # Remplacer les noms des jours par leur équivalent en français
    df1['Jour de la semaine'] = df1['Jour de la semaine'].map(jours_semaine_fr)
    df2 = df2.rename(columns={'Bureau Distributeur': 'Ville'})
    df2['Ville']= df2['Ville'].str.upper()
    df2['Ville']= df2['Ville'].str.replace("-", " ")
    df2['Ville']= df2['Ville'].str.replace("SAINT", "ST")
    df2['Ville']= df2['Ville'].str.replace("SAINTE", "STE")
    df2['Ville']= df2['Ville'].str.replace("L'", "")
    df2 = df2.fillna('')
    df2['adresse_complete'] = df2['Adresse'] + " " + df2['Comp. adresse'] + " " + df2['Code postal'] + " " + df2['Ville']
    df2['adresse_complete']= df2['adresse_complete'].str.upper()
    df2['adresse_complete']= df2['adresse_complete'].str.replace(r'\s+', ' ', regex=True)
    df2 = df2.drop(columns=['Adresse', 'Comp. adresse', 'Code postal'])
    df2= df2.rename(columns={'adresse_complete': 'Adresse'})
    df = df1.merge(df2, how="left", left_on="CIREF", right_on='CIREF')
    return df

# Fonction pour convertir Gauss-Laborde à WGS84
def gauss_laborde_to_wgs84(x, y):
    # Définir le système de projection Gauss-Laborde
    gauss_laborde = Proj(proj='tmerc', lat_0=-21.11666667, lon_0=55.53333333, k=1, x_0=160000, y_0=50000)
    # Définir le système de projection WGS84
    wgs84 = Proj(proj='latlong', datum='WGS84')
    # Créer un transformer pour convertir entre les deux systèmes
    transformer = Transformer.from_proj(gauss_laborde, wgs84)
    # Effectuer la transformation
    lon, lat = transformer.transform(x, y)
    return lat, lon

def count_corr(df):
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

def count_IMEI(df):
    # Compter le nombre de communications par IMEI
    imei_counts = df['IMEI'].value_counts().reset_index()
    # Renommer les colonnes pour plus de clarté
    imei_counts.columns = ['IMEI', 'Nombre de communication']
    # Afficher le DataFrame des IMEI comptabilisés
    return imei_counts

def count_IMSI(df):
    # Compter le nombre de communications par IMEI
    imsi_counts = df['IMSI'].value_counts().reset_index()
    # Renommer les colonnes pour plus de clarté
    imsi_counts.columns = ['IMSI', 'Nombre de communication']
    # Afficher le DataFrame des IMEI comptabilisés
    return imsi_counts

def count_phone_type(df):
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

def comm_histo_global(df):
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
    # Afficher le graphique
    return fig

def comm_histo_monthly(df):
    # Histogramme par mois
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Histogram(x=df['Mois'].dropna().astype(str), histfunc='count', name='Communications par mois',marker=dict(line=dict(color='black', width=1))))
    fig_monthly.update_layout(title='Nombre de communications par mois', xaxis_title='Mois', yaxis_title='Nombre de communications')
    return fig_monthly

def comm_histo_weekday(df):
    # Histogramme par jour de la semaine
    # Créer une colonne pour le jour de la semaine
    fig_weekday = go.Figure()
    fig_weekday.add_trace(go.Histogram(x=df['Jour de la semaine'], histfunc='count', name='Communications par jour de la semaine', marker=dict(line=dict(color='black', width=1))))
    fig_weekday.update_layout(title='Nombre de communications par jour de la semaine', xaxis_title='Jour de la semaine', yaxis_title='Nombre de communications')
    return fig_weekday

def comm_histo_hour(df):
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
    # Afficher le graphique
    return fig

def adresse_count(df):
    # Compter le nombre de contacts par correspondant
    adresse_counts = df['Adresse'].value_counts().reset_index()
    # Renommer les colonnes pour plus de clarté
    adresse_counts.columns = ['Adresse', 'Nombre de déclenchement']
    # Calculer le nombre total de contacts
    total_contacts = adresse_counts['Nombre de déclenchement'].sum()
    # Calculer le pourcentage et arrondir à un chiffre après la virgule
    adresse_counts['Pourcentage'] = ((adresse_counts['Nombre de déclenchement'] / total_contacts) * 100).round(1)
    # Trier par nombre de contacts du plus élevé au plus bas
    adresse_counts = adresse_counts.sort_values(by='Nombre de déclenchement', ascending=False)
    return adresse_counts

def carto_adresse(df):
    adress_count = adresse_count(df)
    df_merged = adress_count.merge(df, how = 'left', left_on="Adresse", right_on='Adresse')
    # Appliquer la fonction sur les colonnes 'Coordonnée X' et 'Coordonnée Y'
    df_merged[['Latitude', 'Longitude']] = df_merged.apply(lambda row: gauss_laborde_to_wgs84(row['Coordonnée X'], row['Coordonnée Y']), axis=1, result_type='expand')
    fig = px.scatter_map(df_merged, lat="Latitude", lon="Longitude", color="Pourcentage", size="Nombre de déclenchement",
                  color_continuous_scale=px.colors.sequential.Bluered, size_max=15, zoom=10,
                  map_style="carto-positron")
    return fig

def scatter_plot_ville(df):
    fig = px.scatter(df, x= 'Date', y='Ville', color= 'Ville', title='Localisation en fonction de la date')
    return fig
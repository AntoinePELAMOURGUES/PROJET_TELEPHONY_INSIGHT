import pandas as pd
import numpy as np


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
    df2['adresse_complete'] = df2['Adresse'] + " " + df2['Comp. adresse'] + " " + df2['Code postal'] + " " + df2['Ville']
    df2['adresse_complete']= df2['adresse_complete'].str.upper()
    df2['adresse_complete']= df2['adresse_complete'].str.replace(r'\s+', ' ', regex=True)
    df2 = df2.drop(columns=['Adresse', 'Comp. adresse', 'Code postal'])
    df2= df2.rename(columns={'adresse_complete': 'Adresse'})
    df = df1.merge(df2, how="left", left_on="CIREF", right_on='CIREF')
    return df


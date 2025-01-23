import pandas as pd
import numpy as np
import re
import streamlit as st

def extract_city(address):
    if isinstance(address, str):  # Vérifie si l'adresse est une chaîne
        # Regex pour capturer la ville après le code postal (5 chiffres)
        match = re.search(r'\d{5}\s+(.*)', address)
        if match:
            return match.group(1).strip()  # Retourne la ville sans espaces superflus
    return None  # Retourne None si aucune correspondance n'est trouvée ou si l'adresse n'est pas une chaîne

def preprocess_data(file1):
     # Liste des colonnes attendues
    expected_columns = [
        "Date de début d'appel",
        "MSISDN Abonné",
        "Correspondant",
        "Type de communication",
        "Durée / Nbr SMS",
        "Adresse du relais",
        "IMEI abonné",
        "IMSI abonné"
    ]
    # Lire à nouveau avec usecols
    df = pd.read_csv(file1, header=1, sep=';', encoding='latin1')
    rename_dict = {
        "Date de début d'appel": "Date",
        "MSISDN Abonné": "Abonné",
        "Type de communication": "Type d'appel",
        "Durée / Nbr SMS": "Durée",
        "Adresse du relais": "Adresse",
        "IMEI abonné": "IMEI",
        "IMSI abonné": "IMSI"
    }
    # Renommer uniquement les colonnes présentes dans le DataFrame
    df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)
    # Remplacer '0693' par '262693' dans les colonnes 'Abonné' et 'Correspondant'
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        # Extraire l'année, le mois et le jour de la semaine
        df['Années'] = df['Date'].dt.year
        df['Mois'] = df['Date'].dt.month
        df['Jour de la semaine'] = df['Date'].dt.day_name()
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
        df['Mois'] = df['Mois'].map(mois_fr)
        # Remplacer les noms des jours par leur équivalent en français
        df['Jour de la semaine'] = df['Jour de la semaine'].map(jours_semaine_fr)
    if 'IMEI' in df.columns:
        df['IMEI'] = df['IMEI'].astype('str')
        df['IMEI'] = df['IMEI'].str.replace('.0', '')
    if 'Abonné' in df.columns:
        df['Abonné'] = df['Abonné'].replace(r'^0693', '262693', regex=True)
        df['Abonné'] = df['Abonné'].replace(r'^0692', '262692', regex=True)
        df['Abonné'] = df['Abonné'].replace(r'^06', '336', regex=True)
        # Remplacer les NaN par 'Data'
        df['Abonné'] = df['Abonné'].fillna('Data')
    if 'Correspondant' in df.columns:
        df['Correspondant'] = df['Correspondant'].str.split(',').str[0]
        df['Correspondant'] = df['Correspondant'].replace(r'^0693', '262693', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^0692', '262692', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^06', '336', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^07', '337', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^02', '2622', regex=True)
        df['Correspondant'] = df['Correspondant'].fillna('Data')
        # Remplacer les NaN par 'Data'
        df['Correspondant'] = df['Correspondant'].fillna('Data')
    if 'Adresse' in df.columns:
        df['Adresse'] = df['Adresse'].str.upper()
    if 'Ville' in df.columns:
        df['Ville'] = df['Ville'].str.upper()
        # Appliquer la fonction pour créer une nouvelle colonne 'Ville'
        df['Ville'] = df['Adresse'].apply(extract_city)
        df['Ville']= df['Ville'].str.replace("-", " ")
        df['Ville']= df['Ville'].str.replace("SAINT", "ST")
        df['Ville']= df['Ville'].str.replace("SAINTE", "STE")
        df['Ville']= df['Ville'].str.replace("L'", "")
        df['Ville'] = df['Ville'].str.replace("É", "E", regex=False)
    return df


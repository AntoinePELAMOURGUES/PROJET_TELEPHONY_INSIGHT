import pandas as pd
import numpy as np


def preprocess_data(file1, file2):
    expected_columns_file1 = ["Type d'appel", "Abonné", "Correspondant", "Date", "Durée", "CIREF", "IMEI", "IMSI"]
    expected_columns_file2 = ["CIREF", "Adresse", "Comp. adresse", "Code postal", "Bureau Distributeur", "Coordonnée X", "Coordonnée Y"]
    df1 = pd.read_excel(file1, dtype={"Abonné": str, "Correspondant": str, "IMEI": str, "IMSI": str, "CIREF": str})
    df2 = pd.read_excel(file2, dtype= {"CIREF": str, "Adresse" : str, "Comp. adresse" : str, "Code postal" : str, "Bureau Distributeur" : str, "Coordonnée X": str, "Coordonnée Y": str})
    available_columns_1 = df1.columns.tolist()
    # Filtrer les colonnes attendues qui sont disponibles
    filtered_columns_1 = list(set(expected_columns_file1) & set(available_columns_1))
    available_columns_2 = df2.columns.tolist()
    # Filtrer les colonnes attendues qui sont disponibles
    filtered_columns_2 = list(set(expected_columns_file2) & set(available_columns_2))
    if 'Date' in df1.columns:
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
    if 'Abonné' in df1.columns:
        df1['Abonné'] = df1['Abonné'].replace(r'^0693', '262693', regex=True)
        df1['Abonné'] = df1['Abonné'].replace(r'^0692', '262692', regex=True)
        df1['Abonné'] = df1['Abonné'].replace(r'^06', '336', regex=True)
    if 'Correspondant' in df1.columns:
        df1['Correspondant'] = df1['Correspondant'].fillna('Data')
        df1['Correspondant'] = df1['Correspondant'].str.split(',').str[0]
        df1['Correspondant'] = df1['Correspondant'].replace(r'^0693', '262693', regex=True)
        df1['Correspondant'] = df1['Correspondant'].replace(r'^0692', '262692', regex=True)
        df1['Correspondant'] = df1['Correspondant'].replace(r'^06', '336', regex=True)
        df1['Correspondant'] = df1['Correspondant'].replace(r'^07', '337', regex=True)
        df1['Correspondant'] = df1['Correspondant'].replace(r'^02', '2622', regex=True)
    if 'Bureau Distributeur' in df2.columns:
        df2 = df2.rename(columns={'Bureau Distributeur': 'Ville'})
        df2['Ville']= df2['Ville'].str.upper()
        df2['Ville']= df2['Ville'].str.replace("-", " ")
        df2['Ville']= df2['Ville'].str.replace("SAINT", "ST")
        df2['Ville']= df2['Ville'].str.replace("SAINTE", "STE")
        df2['Ville']= df2['Ville'].str.replace("L'", "")
        df2['Ville'] = df2['Ville'].str.replace("É", "E", regex=False)
    if 'Adresse' in df2.columns and 'Comp. adresse' in df2.columns and 'Code postal' in df2.columns:
        df2['adresse_complete'] = df2['Adresse'] + " " + df2['Comp. adresse'] + " " + df2['Code postal'] + " " + df2['Ville']
        df2['adresse_complete']= df2['adresse_complete'].str.upper()
        df2['adresse_complete']= df2['adresse_complete'].str.replace(r'\s+', ' ', regex=True)
        df2 = df2.drop(columns=['Adresse', 'Comp. adresse', 'Code postal'])
        df2= df2.rename(columns={'adresse_complete': 'Adresse'})
    df = df1.merge(df2, how="left", left_on="CIREF", right_on='CIREF')
    return df


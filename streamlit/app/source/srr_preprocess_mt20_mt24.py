import pandas as pd
import numpy as np


def preprocess_data(file1, file2):
    expected_columns_file1 = ["Type d'appel", "Abonné", "Correspondant", "Date", "Durée", "CIREF", "IMEI", "IMSI"]
    expected_columns_file2 = ["CIREF", "Adresse", "Comp. adresse", "Code postal", "Bureau Distributeur", "Coordonnée X", "Coordonnée Y"]
    df1 = pd.read_excel(file1, dtype={"Abonné": str, "Correspondant": str, "IMEI": str, "IMSI": str, "CIREF": str, "Durée": str})
    df2 = pd.read_excel(file2, dtype= {"CIREF": str, "Adresse" : str, "Comp. adresse" : str, "Code postal" : str, "Bureau Distributeur" : str, "Coordonnée X": str, "Coordonnée Y": str})
    available_columns_1 = df1.columns.tolist()
    # Filtrer les colonnes attendues qui sont disponibles
    filtered_columns_1 = list(set(expected_columns_file1) & set(available_columns_1))
    available_columns_2 = df2.columns.tolist()
    # Filtrer les colonnes attendues qui sont disponibles
    filtered_columns_2 = list(set(expected_columns_file2) & set(available_columns_2))
    df1 = df1[filtered_columns_1]
    df1.Abonné.ffill(inplace=True)
    df1.Abonné.bfill(inplace=True)
    df2 = df2[filtered_columns_2]
    df = df1.merge(df2, on="CIREF", how="left")
    deleted_columns =['Critère Recherché_x', 'Commentaire_x', '3ème interlocuteur', 'Nature Correspondant',
       'Nature 3ème interlocuteur', 'GCI_x', 'EGCI_x', 'NGCI_x', 'Code PLMN',
       'Volume de données montant', 'Volume de données descendant',"Opérateur d'itinérance", 'Indicateur RO', 'Décalage horaire',
       'Service de Base', 'IPV4 VO Wifi', 'IPV6 VO Wifi',
       'Port Source VO Wifi', 'Critère Recherché_y', 'Commentaire_y', 'GCI_y',
       'EGCI_y', 'NGCI_y', 'Système', 'Nom du site', 'Code zone', 'Coordonnée Z', 'Début asso. CIREF/GCI', 'Fin asso. CIREF/GCI']
    for i in df.columns.tolist():
        if i in deleted_columns:
            df.drop(i, axis=1, inplace=True)
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
    if 'Abonné' in df.columns:
        df['Abonné'] = df["Abonné"].ffill()
        df['Abonné'] = df["Abonné"].bfill()
        df['Abonné'] = df['Abonné'].replace(r'^0693', '262693', regex=True)
        df['Abonné'] = df['Abonné'].replace(r'^0692', '262692', regex=True)
        df['Abonné'] = df['Abonné'].replace(r'^06', '336', regex=True)
    if 'Correspondant' in df.columns:
        df['Correspondant'] = df['Correspondant'].fillna('Data')
        df['Correspondant'] = df['Correspondant'].str.split(',').str[0]
        df['Correspondant'] = df['Correspondant'].replace(r'^0693', '262693', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^0692', '262692', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^06', '336', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^07', '337', regex=True)
        df['Correspondant'] = df['Correspondant'].replace(r'^02', '2622', regex=True)
    if 'Bureau Distributeur' in df.columns:
        df = df.rename(columns={'Bureau Distributeur': 'Ville'})
        df['Ville']= df['Ville'].str.upper()
        df['Ville']= df['Ville'].str.replace("-", " ")
        df['Ville']= df['Ville'].str.replace("SAINT", "ST")
        df['Ville']= df['Ville'].str.replace("SAINTE", "STE")
        df['Ville']= df['Ville'].str.replace("L'", "")
        df['Ville'] = df['Ville'].str.replace("É", "E", regex=False)
    if 'Adresse' in df.columns and 'Comp. adresse' in df.columns and 'Code postal' in df.columns:
        df['adresse_complete'] = df['Adresse'] + "," + df['Code postal'] + " " + df['Ville']
        df['adresse_complete']= df['adresse_complete'].str.upper()
        df['adresse_complete']= df['adresse_complete'].str.replace(r'\s+', ' ', regex=True)
        df.fillna({'adresse_complete': 'INDETERMINE'}, inplace=True)
        df = df.drop(columns=['Adresse', 'Comp. adresse', 'Code postal'])
        df= df.rename(columns={'adresse_complete': 'Adresse'})
    return df


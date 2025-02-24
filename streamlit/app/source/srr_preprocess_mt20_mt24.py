import pandas as pd
import numpy as np
from .preprocess_functions import *

def preprocess_data(file1, file2, sheet_name=0):
    expected_columns_file1 = ["Type d'appel", "Abonné", "Correspondant", "Date", "Durée", "CIREF", "IMEI", "IMSI"]
    expected_columns_file2 = ["CIREF", "Adresse", "Comp. adresse", "Code postal", "Bureau Distributeur", "Coordonnée X", "Coordonnée Y"]
    df1 = pd.read_excel(file1, sheet_name=sheet_name, dtype={"Abonné": str, "Correspondant": str, "IMEI": str, "IMSI": str, "CIREF": str, "Durée": str, "Type d'appel" : str})
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
        df = transform_date(df)
    if 'Abonné' in df.columns:
        df = clean_cell_number(df, 'Abonné')
    if 'Correspondant' in df.columns:
        df = clean_cell_number(df, 'Correspondant')
    if "Type d'appel" in df.columns:
        df["Type d'appel"] = df["Type d'appel"].astype(str)
        df["Type d'appel"] = df["Type d'appel"].str.upper()
        df["Type d'appel"] = df["Type d'appel"].apply(reset_accent)
    if 'Bureau Distributeur' in df.columns:
        df = clean_city(df, columns='Bureau Distributeur')
    if 'Adresse' in df.columns and 'Code postal' in df.columns:
        df['adresse_complete'] = df['Adresse'] + " " + df['Code postal'] + " " + df['VILLE']
        df['adresse_complete'] = df['adresse_complete'].astype(str)
        df['adresse_complete']= df['adresse_complete'].str.upper()
        df['adresse_complete']= df['adresse_complete'].str.replace(r'\s+', ' ', regex=True)
        df['adresse_complete'] = df['adresse_complete'].apply(reset_accent)
        df = df.drop(columns=['Adresse', 'Comp. adresse', 'Code postal'])
        df= df.rename(columns={'adresse_complete': 'Adresse'})
    df.fillna("INDETERMINE", inplace=True)
    definitive_columns = ["Type d'appel", "Abonné", "Correspondant", "Date", "Durée", "CIREF", "IMEI", "IMSI", "Adresse", "Ville", 'Années', 'Mois', 'Heure', 'Jour de la semaine', "Coordonnée X", "Coordonnée Y"]
    no_accent_columns = [reset_accent(i) for i in definitive_columns]
    final_columns = [i.upper() for i in no_accent_columns]
    for old_columns, new_columns in zip(definitive_columns, final_columns):
        df = df.rename(columns={old_columns : new_columns})
    return df
import pandas as pd
import numpy as np
import re

def convert_date(date_str):
    # Extraire le fuseau horaire avec une expression régulière
    match = re.search(r'UTC([+-]\d)', date_str)
    if match:
        utc_offset = int(match.group(1))  # Récupérer le décalage horaire
    else:
        utc_offset = 0  # Valeur par défaut si aucun fuseau horaire n'est trouvé
    # Retirer le fuseau horaire et convertir en datetime
    date_without_tz = date_str.split(' UTC')[0]  # Retirer ' UTC+X'
    dt = pd.to_datetime(date_without_tz, format='%d/%m/%Y - %H:%M:%S')
    # Ajuster le fuseau horaire à UTC+4
    dt = dt + pd.Timedelta(hours=(4 - utc_offset))  # Ajustement basé sur l'offset
    return dt

# Fonction pour nettoyer les chaînes
def clean_number(number_str):
    # Utiliser une expression régulière pour supprimer le préfixe et le suffixe
    return re.sub(r'^\=\("\s*|\s*"\)$', '', number_str)

reunion_postal_codes = {
    "97400": "ST DENIS",
    "97410": "ST PIERRE",
    "97411": "BOIS DE NEFLES",
    "97412": "BRAS PANON",
    "97413": "CILAOS",
    "97414": "ENTRE DEUX",
    "97416": "LA CHALOUPE",
    "97417": "ST BERNARD",
    "97418": "LA PLAINE DES CAFRES",
    "97419": "LA POSSESSION",
    "97420": "LE PORT",
    "97421": "LA RIVIERE ST LOUIS",
    "97422": "LA SALINE",
    "97423": "LE GUILLAUME",
    "97424": "PITON ST LEU",
    "97425": "LES AVRIONS",
    "97426": "LES TROIS BASSINS",
    "97427": "L'ETANG SALE",
    "97428": "LA NOUVELLE",
    "97429": "PETITE ILE",
    "97430": "LE TAMPON",
    "97431": "LA PLAINE DES PALMISTES",
    "97432": "LA RAVINE DES CABRIS",
    "97433": "SALAZIE - HELL BOURG",
    "97434": "ST GILLES LES BAINS",
    "97435": "BERNICA",
    "97436": "ST LEU",
    "97437": "STE ANNE",
    "97438": "STE MARIE",
    "97439": "STE ROSE",
    "97440": "ST ANDRE",
    "97441": "STE SUZANNE",
    "97442": "BASSE VALLEE",
    "97450": "ST LOUIS",
    "97460": "ST PAUL",
    "97470": "ST BENOIT"
}

def replace_unknown_ville(row):
    if row['VILLE'] == 'ville inconnue':
        return reunion_postal_codes.get(row['CODE POSTAL'], 'ville inconnue')  # Remplace par la ville correspondante ou garde 'ville inconnue'
    return row['VILLE']

def preprocess_data(file1):
    df = pd.read_csv(file1, sep=';', encoding='latin1', dtype={"CIBLE": str, "CORRESPONDANT": str, "DUREE": str, "IMSI": str, "IMEI": str, "CODE POSTAL": str,  "X": str, "Y": str})
    # Appliquer la fonction pour convertir les dates
    if 'DATE' in df.columns:
        df['converted_date'] = df['DATE'].apply(convert_date)
        # Extraire l'année, le mois et le jour de la semaine
        df['Années'] = df['converted_date'].dt.year
        df['Mois'] = df['converted_date'].dt.month
        df['Jour de la semaine'] = df['converted_date'].dt.day_name()
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
    if 'CORRESPONDANT' in df.columns:
        df["CORRESPONDANT"] = df["CORRESPONDANT"].fillna("Data")
        df['CORRESPONDANT'] = df['CORRESPONDANT'].str.split(',').str[0]
        df['CORRESPONDANT'] = df['CORRESPONDANT'].apply(clean_number)
        df['CORRESPONDANT'] = df['CORRESPONDANT'].replace(r'^0692', '262692', regex=True)
        df['CORRESPONDANT'] = df['CORRESPONDANT'].replace(r'^0693', '262693', regex=True)
        df['CORRESPONDANT'] = df['CORRESPONDANT'].replace(r'^06', '336', regex=True)
        df['CORRESPONDANT'] = df['CORRESPONDANT'].replace(r'^07', '337', regex=True)
        df['CORRESPONDANT'] = df['CORRESPONDANT'].replace(r'^02', '2622', regex=True)
    if 'DUREE' in df.columns:
        df["DUREE"] = df["DUREE"].fillna("0")
    if 'IMEI' in df.columns:
        df['IMEI'] = df['IMEI'].fillna("Non précisé")
        df["IMEI"] = df["IMEI"].apply(clean_number)
    if "IMSI" in df.columns:
        df['IMSI'] = df['IMSI'].apply(clean_number)
    if "CIBLE" in df.columns:
        df['CIBLE'] = df['CIBLE'].apply(clean_number)
        df['CIBLE'] = df['CIBLE'].replace(r'^0692', '262692', regex=True)
        df['CIBLE'] = df['CIBLE'].replace(r'^0693', '262693', regex=True)
        df['CIBLE'] = df['CIBLE'].replace(r'^06', '336', regex=True)
    if "VILLE" in df.columns:
        df['VILLE'] = df.apply(replace_unknown_ville, axis=1)
        df['VILLE'] = df['VILLE'].str.upper()
        df['VILLE']= df['VILLE'].str.replace("-", " ")
        df['VILLE']= df['VILLE'].str.replace("SAINT", "ST")
        df['VILLE']= df['VILLE'].str.replace("SAINTE", "STE")
        df['VILLE']= df['VILLE'].str.replace("L'", "")
        df['VILLE'] = df['VILLE'].str.replace("É", "E", regex=False)
    if "VILLE" in df.columns and "CODE POSTAL" in df.columns and "VILLE" in df.columns:
        df["Adresse"] = df["ADRESSE2"] + " " + df["CODE POSTAL"] + " " + df["VILLE"]
        df.fillna({'Adresse': 'INDETERMINE', 'VILLE' : 'INDETERMINE', 'CODE POSTAL' : 'INDETERMINE' }, inplace=True)
        df['Adresse'] = df['Adresse'].str.upper()
        df['Adresse']= df['Adresse'].str.replace(r'\s+', ' ', regex=True)
        df['Adresse'] = df['Adresse'].str.strip() # Supprimer les espaces inutiles
    deleted_columns = ['DATE', 'TYPE CORRESPONDANT', 'COMP.', 'EFFICACITE' , 'CELLID', 'ADRESSE IP VO WIFI', 'PORT SOURCE VO WIFI', 'ADRESSE2','ADRESSE3','ADRESSE4', 'ADRESSE5', 'PAYS', 'TYPE-COORD', 'CODE POSTAL']
    df.drop(columns=deleted_columns, inplace=True, errors='ignore')
    rename_dict = {"TYPE": "Type d'appel", "CORRESPONDANT": "Correspondant", "CIBLE": "Abonné", "DIRECTION": "Direction", "DUREE": "Durée", "VILLE": "Ville", "X": "Latitude", "Y": "Longitude", "converted_date": "Date"
    }
    # Renommer uniquement les colonnes présentes dans le DataFrame
    df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)
    return df
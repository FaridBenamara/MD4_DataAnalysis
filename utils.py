# utils.py
import pandas as pd
import numpy as np

def load_and_preprocess_data():
    """Charge et prétraite les données pour le dashboard"""
    # Charger les données avec low_memory=False pour éviter l'avertissement
    df = pd.read_csv('Stop_Data_2019_to_2022.csv', low_memory=False)
    
    # Conversion des dates
    df['DATETIME'] = pd.to_datetime(df['DATETIME'])
    
    # Nettoyage de la colonne STOP_DISTRICT
    df['STOP_DISTRICT'] = pd.to_numeric(df['STOP_DISTRICT'], errors='coerce')
    df = df.dropna(subset=['STOP_DISTRICT'])  # Supprimer les lignes où STOP_DISTRICT est NaN
    
    # Création d'indicateurs temporels
    df['hour'] = df['DATETIME'].dt.hour
    df['day_of_week'] = df['DATETIME'].dt.day_name()
    df['month'] = df['DATETIME'].dt.month
    df['year'] = df['DATETIME'].dt.year
    df['season'] = pd.cut(df['month'], 
                         bins=[0,3,6,9,12], 
                         labels=['Hiver', 'Printemps', 'Été', 'Automne'])
    
    # Création d'indicateurs d'intervention
    df['intervention_score'] = (
        (df['PERSON_SEARCH_PAT_DOWN'].notna().astype(int) * 2) +
        (df['PROPERTY_SEARCH_PAT_DOWN'].notna().astype(int) * 2) +
        (df['TICKETS_ISSUED'].notna().astype(int)) +
        (df['WARNINGS_ISSUED'].notna().astype(int) * 0.5) +
        (df['ARREST_CHARGES'].notna().astype(int) * 3)
    )
    
    # Classification des interventions
    df['intervention_type'] = 'Contrôle simple'
    df.loc[df['TICKETS_ISSUED'].notna(), 'intervention_type'] = 'Contravention'
    df.loc[df['PERSON_SEARCH_PAT_DOWN'].notna(), 'intervention_type'] = 'Fouille personnelle'
    df.loc[df['PROPERTY_SEARCH_PAT_DOWN'].notna(), 'intervention_type'] = 'Fouille matérielle'
    df.loc[df['ARREST_CHARGES'].notna(), 'intervention_type'] = 'Arrestation'
    
    return df

# Constantes pour la cartographie
DISTRICT_COORDINATES = {
    1.0: {'lat': 38.8935, 'lon': -77.0135, 'name': 'Downtown/Penn Quarter'},
    2.0: {'lat': 38.9115, 'lon': -77.0335, 'name': 'Georgetown/Dupont Circle'},
    3.0: {'lat': 38.9275, 'lon': -77.0235, 'name': 'Adams Morgan/Columbia Heights'},
    4.0: {'lat': 38.9515, 'lon': -77.0335, 'name': 'Upper NW'},
    5.0: {'lat': 38.9215, 'lon': -76.9835, 'name': 'Northeast'},
    6.0: {'lat': 38.8815, 'lon': -76.9955, 'name': 'Capitol Hill/Navy Yard'},
    7.0: {'lat': 38.8675, 'lon': -76.9655, 'name': 'Anacostia/Southeast'}
}

def analyze_stop_reasons(df):
    """Analyse les raisons des arrêts"""
    # Combiner les raisons de différents types d'arrêts
    reasons = pd.concat([
        df['STOP_REASON_TICKET'].dropna(),
        df['STOP_REASON_NONTICKET'].dropna(),
        df['STOP_REASON_HARBOR'].dropna()
    ])
    return reasons.value_counts().head(10)

def get_hourly_stats(df):
    """Obtient des statistiques détaillées par heure"""
    hourly_stats = df.groupby('hour').agg({
        'STOP_DURATION_MINS': 'mean',
        'intervention_score': 'mean',
        'ARREST_CHARGES': lambda x: x.notna().mean() * 100,
        'TICKETS_ISSUED': lambda x: x.notna().mean() * 100
    }).round(2)
    
    hourly_stats.columns = ['Durée moyenne (min)', 'Score intervention', 
                           'Taux arrestation (%)', 'Taux verbalisation (%)']
    return hourly_stats
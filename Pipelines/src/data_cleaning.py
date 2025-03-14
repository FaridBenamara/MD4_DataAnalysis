import logging 
from abc import ABC, abstractmethod
import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split
from typing import Union

class DataStrategy(ABC):
    """
    Abstract class defining strategy for data cleaning.
    """

    @abstractmethod
    def handle_data(self, data: pd.DataFrame) -> Union[pd.DataFrame, pd.Series]:
        pass

class DataPreProcessing(DataStrategy):
    """
    Preprocessing data by cleaning and creating new features.
    """

    def handle_data(self, data: pd.DataFrame) -> pd.DataFrame:
        try:
            # Conversion des dates
            data['DATETIME'] = pd.to_datetime(data['DATETIME'])

            # Nettoyage des durées d'intervention
            data['STOP_DURATION_MINS'] = pd.to_numeric(data['STOP_DURATION_MINS'], errors='coerce')
            median_duration = data['STOP_DURATION_MINS'].median()
            data['STOP_DURATION_MINS'] = data['STOP_DURATION_MINS'].apply(
                lambda x: median_duration if pd.isna(x) or x < 0 or x > 1440 else x
            )

            # Nettoyage de la colonne STOP_DISTRICT
            data['STOP_DISTRICT'] = pd.to_numeric(data['STOP_DISTRICT'], errors='coerce')
            data = data.dropna(subset=['STOP_DISTRICT'])

            # Création d'indicateurs temporels
            data['hour'] = data['DATETIME'].dt.hour
            data['day_of_week'] = data['DATETIME'].dt.day_name()
            data['month'] = data['DATETIME'].dt.month
            data['year'] = data['DATETIME'].dt.year
            data['season'] = pd.cut(data['month'], 
                                    bins=[0, 3, 6, 9, 12], 
                                    labels=['Hiver', 'Printemps', 'Été', 'Automne'])

            # Création d'indicateurs d'intervention
            data['intervention_score'] = (
                (data['PERSON_SEARCH_PAT_DOWN'].notna().astype(int) * 2) +
                (data['PROPERTY_SEARCH_PAT_DOWN'].notna().astype(int) * 2) +
                (data['TICKETS_ISSUED'].notna().astype(int)) +
                (data['WARNINGS_ISSUED'].notna().astype(int) * 0.5) +
                (data['ARREST_CHARGES'].notna().astype(int) * 3)
            )

            # Classification des interventions
            data['intervention_type'] = 'Contrôle simple'
            data.loc[data['TICKETS_ISSUED'].notna(), 'intervention_type'] = 'Contravention'
            data.loc[data['PERSON_SEARCH_PAT_DOWN'].notna(), 'intervention_type'] = 'Fouille personnelle'
            data.loc[data['PROPERTY_SEARCH_PAT_DOWN'].notna(), 'intervention_type'] = 'Fouille matérielle'
            data.loc[data['ARREST_CHARGES'].notna(), 'intervention_type'] = 'Arrestation'

            return data

        except Exception as e:
            logging.error(f"Error in data preprocessing: {e}")
            raise


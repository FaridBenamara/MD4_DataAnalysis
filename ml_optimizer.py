import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

class PoliceResourceOptimizer:
    def __init__(self):
        self.total_officers = 4000  # Nombre total d'officiers disponibles
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.le = LabelEncoder()
        
    def prepare_features(self, df):
        """Préparation des caractéristiques pour la prédiction"""
        # Création de features temporelles
        df_features = pd.DataFrame()
        df_features['hour'] = df['DATETIME'].dt.hour
        df_features['day_of_week'] = df['DATETIME'].dt.dayofweek
        df_features['month'] = df['DATETIME'].dt.month
        df_features['is_weekend'] = df['DATETIME'].dt.dayofweek.isin([5, 6]).astype(int)
        df_features['is_night'] = ((df['DATETIME'].dt.hour >= 22) | 
                                 (df['DATETIME'].dt.hour <= 5)).astype(int)
        
        # Agrégation par district et période
        district_stats = df.groupby('STOP_DISTRICT').agg({
            'CCN_ANONYMIZED': 'count',  # Nombre d'interventions
            'STOP_DURATION_MINS': 'mean',  # Durée moyenne
            'intervention_score': 'mean'  # Score moyen d'intervention
        }).reset_index()
        
        return district_stats, df_features
    
    def predict_resource_needs(self, df):
        """Prédiction des besoins en ressources par district et période"""
        district_stats, time_features = self.prepare_features(df)
        
        # Calcul des besoins en personnel
        resources_needed = pd.DataFrame()
        for district in district_stats['STOP_DISTRICT'].unique():
            district_data = district_stats[district_stats['STOP_DISTRICT'] == district]
            
            # Calcul du nombre d'agents nécessaires
            base_officers = np.ceil(district_data['CCN_ANONYMIZED'] * 
                                  district_data['STOP_DURATION_MINS'] / (8 * 60))  # 8h de travail
            
            # Ajustement selon la gravité
            adjusted_officers = base_officers * (1 + district_data['intervention_score'] / 10)
            
            resources_needed = pd.concat([resources_needed, pd.DataFrame({
                'STOP_DISTRICT': district,
                'officers_needed': adjusted_officers.values[0],
                'patrol_cars': np.ceil(adjusted_officers.values[0] / 2),  # 2 officiers par voiture
                'priority_level': district_data['intervention_score'].values[0]
            }, index=[0])], ignore_index=True)
        
        return resources_needed

    def optimize_distribution(self, predictions):
        """Optimise la répartition des 4000 officiers disponibles"""
        # Calculer le ratio de répartition basé sur les besoins prédits
        total_predicted = sum(predictions)
        ratios = predictions / total_predicted
        
        # Répartir les 4000 officiers selon ces ratios
        optimized_distribution = ratios * self.total_officers
        
        # Arrondir à l'entier le plus proche
        return np.round(optimized_distribution).astype(int)

    def predict_today(self, data):
        # ... existing code ...
        raw_predictions = self.model.predict(donnees_actuelles)
        
        # Optimiser la distribution pour 4000 officiers
        optimized_predictions = self.optimize_distribution(raw_predictions)
        
        return optimized_predictions

def create_deployment_visualization(resources_df, DISTRICT_COORDINATES):
    """Création de la visualisation du plan de déploiement"""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    # Figure 1: Les graphiques standards
    fig1 = make_subplots(rows=2, cols=2,
                       subplot_titles=("Répartition des Officiers par District",
                                     "Besoins en Véhicules",
                                     "Niveaux de Priorité",
                                     ""))
    
    # Graphique des officiers par district
    fig1.add_trace(
        go.Bar(x=resources_df['STOP_DISTRICT'],
               y=resources_df['officers_needed'],
               name="Officiers nécessaires"),
        row=1, col=1
    )
    
    # Graphique des véhicules
    fig1.add_trace(
        go.Bar(x=resources_df['STOP_DISTRICT'],
               y=resources_df['patrol_cars'],
               name="Véhicules de patrouille"),
        row=1, col=2
    )
    
    # Niveaux de priorité
    fig1.add_trace(
        go.Heatmap(
            z=resources_df['priority_level'].values.reshape(1, -1),
            x=resources_df['STOP_DISTRICT'],
            y=['Priorité'],
            colorscale='RdYlGn_r'),
        row=2, col=1
    )
    
    # Figure 2: La carte
    fig2 = go.Figure(go.Scattermapbox(
        lat=[DISTRICT_COORDINATES[d]['lat'] for d in resources_df['STOP_DISTRICT']],
        lon=[DISTRICT_COORDINATES[d]['lon'] for d in resources_df['STOP_DISTRICT']],
        mode='markers+text',
        marker=dict(
            size=resources_df['officers_needed'] * 2,
            color=resources_df['priority_level'],
            colorscale='RdYlGn_r'
        ),
        text=resources_df['officers_needed'].round().astype(int).astype(str) + ' officiers',
        name="Déploiement"
    ))
    
    fig2.update_layout(
        mapbox_style="carto-positron",
        mapbox=dict(
            center=dict(lat=38.9072, lon=-77.0369),
            zoom=11
        ),
        height=400,
        title="Carte de Déploiement"
    )
    
    # Mise en page de la première figure
    fig1.update_layout(
        height=600,
        showlegend=True,
        title_text="Analyse du Plan de Déploiement"
    )
    
    # Retourner les deux figures dans un dictionnaire
    return {
        'analytics': fig1,
        'map': fig2
    } 
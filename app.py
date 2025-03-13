# app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_and_preprocess_data, DISTRICT_COORDINATES, analyze_stop_reasons, get_hourly_stats
import pandas as pd

# Chargement des données
df = load_and_preprocess_data()

# Création de l'application avec thème Bootstrap
app = dash.Dash(__name__, external_stylesheets=[
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
])

# Layout principal
app.layout = html.Div([
    # Navbar avec titre
    html.Nav(className="navbar navbar-dark bg-dark", children=[
        html.Span("Analyse des interventions policières à Washington DC", 
                 className="navbar-brand mb-0 h1")
    ]),
    
    # Corps principal
    html.Div(className="container-fluid", children=[
        # Filtres
        html.Div(className="row mt-3", children=[
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Filtres", className="card-title"),
                        html.Div(className="row", children=[
                            # Sélection de la période
                            html.Div(className="col-md-4", children=[
                                html.Label("Période d'analyse"),
                                dcc.DatePickerRange(
                                    id='date-range',
                                    start_date=df['DATETIME'].min(),
                                    end_date=df['DATETIME'].max(),
                                    display_format='YYYY-MM-DD'
                                )
                            ]),
                            # Sélection des districts
                            html.Div(className="col-md-4", children=[
                                html.Label("Districts"),
                                dcc.Dropdown(
                                    id='district-filter',
                                    options=[
                                        {'label': f'District {int(d)} - {DISTRICT_COORDINATES[d]["name"]}', 
                                         'value': d}
                                        for d in sorted(df['STOP_DISTRICT'].unique()) if not pd.isna(d)
                                    ],
                                    multi=True,
                                    placeholder="Tous les districts"
                                )
                            ]),
                            # Sélection du type d'intervention
                            html.Div(className="col-md-4", children=[
                                html.Label("Type d'intervention"),
                                dcc.Dropdown(
                                    id='intervention-type-filter',
                                    options=[
                                        {'label': t, 'value': t}
                                        for t in df['intervention_type'].unique()
                                    ],
                                    multi=True,
                                    placeholder="Tous les types"
                                )
                            ])
                        ])
                    ])
                ])
            ])
        ]),

        # Première rangée - Carte et Stats
        html.Div(className="row mt-3", children=[
            # Carte des districts
            html.Div(className="col-md-8", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Distribution géographique", className="card-title"),
                        dcc.Graph(id='district-map')
                    ])
                ])
            ]),
            # Statistiques globales
            html.Div(className="col-md-4", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Statistiques globales", className="card-title"),
                        html.Div(id='global-stats')
                    ])
                ])
            ])
        ]),

        # Deuxième rangée - Analyse temporelle
        html.Div(className="row mt-3", children=[
            # Distribution horaire
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Analyse horaire détaillée", className="card-title"),
                        dcc.Graph(id='hourly-analysis')
                    ])
                ])
            ])
        ]),

        # Troisième rangée - Raisons et Types
        html.Div(className="row mt-3", children=[
            # Raisons des arrêts
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Top 10 des raisons d'intervention", className="card-title"),
                        dcc.Graph(id='stop-reasons')
                    ])
                ])
            ]),
            # Types d'interventions
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Types d'interventions", className="card-title"),
                        dcc.Graph(id='intervention-types')
                    ])
                ])
            ])
        ]),

        # Quatrième rangée - Heatmap et Patterns
        html.Div(className="row mt-3", children=[
            # Heatmap temporelle
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Distribution temporelle", className="card-title"),
                        dcc.Graph(id='temporal-heatmap')
                    ])
                ])
            ]),
            # Patterns hebdomadaires
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Patterns hebdomadaires", className="card-title"),
                        dcc.Graph(id='weekly-patterns')
                    ])
                ])
            ])
        ]),

        # Cinquième rangée - Analyse ethnique
        html.Div(className="row mt-3", children=[
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Analyse par ethnicité", className="card-title"),
                        dcc.Graph(id='ethnicity-analysis')
                    ])
                ])
            ])
        ]),

        # Sixième rangée - Analyse par âge
        html.Div(className="row mt-3", children=[
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Analyse par âge", className="card-title"),
                        dcc.Graph(id='age-analysis')
                    ])
                ])
            ])
        ]),

        # Septième rangée - Tendances mensuelles
        html.Div(className="row mt-3 mb-3", children=[
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Tendances mensuelles", className="card-title"),
                        dcc.Graph(id='monthly-trends')
                    ])
                ])
            ])
        ])
    ])
])

# Callbacks
@app.callback(
    [Output('district-map', 'figure'),
     Output('global-stats', 'children'),
     Output('hourly-analysis', 'figure'),
     Output('stop-reasons', 'figure'),
     Output('intervention-types', 'figure'),
     Output('temporal-heatmap', 'figure'),
     Output('weekly-patterns', 'figure'),
     Output('ethnicity-analysis', 'figure'),
     Output('age-analysis', 'figure'),
     Output('monthly-trends', 'figure')],
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date'),
     Input('district-filter', 'value'),
     Input('intervention-type-filter', 'value')]
)
def update_all_graphs(start_date, end_date, selected_districts, selected_types):
    # Filtrage des données
    filtered_df = df.copy()
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['DATETIME'] >= start_date) &
            (filtered_df['DATETIME'] <= end_date)
        ]
    if selected_districts:
        filtered_df = filtered_df[filtered_df['STOP_DISTRICT'].isin(selected_districts)]
    if selected_types:
        filtered_df = filtered_df[filtered_df['intervention_type'].isin(selected_types)]

    return (
        create_map(filtered_df),
        create_stats_component(filtered_df),
        create_hourly_analysis(filtered_df),
        create_stop_reasons_chart(filtered_df),
        create_intervention_types(filtered_df),
        create_temporal_heatmap(filtered_df),
        create_weekly_patterns(filtered_df),
        create_ethnicity_analysis(filtered_df),
        create_age_analysis(filtered_df),
        create_monthly_trends(filtered_df)
    )

def create_map(df):
    """Création de la carte des districts"""
    district_counts = df['STOP_DISTRICT'].value_counts()
    
    lats, lons, sizes, texts = [], [], [], []
    for district in DISTRICT_COORDINATES:
        if district in district_counts.index:
            lats.append(DISTRICT_COORDINATES[district]['lat'])
            lons.append(DISTRICT_COORDINATES[district]['lon'])
            count = district_counts[district]
            sizes.append(count)
            texts.append(
                f"District {int(district)} - {DISTRICT_COORDINATES[district]['name']}"
                f"<br>Arrêts: {count:,}"
                f"<br>% du total: {(count/len(df)*100):.1f}%"
            )
    
    return px.scatter_mapbox(
        lat=lats,
        lon=lons,
        size=[s/100 for s in sizes],
        text=texts,
        hover_name=texts,
        mapbox_style="carto-positron",
        center={"lat": 38.9072, "lon": -77.0369},
        zoom=11
    )

def create_stats_component(df):
    """Création des statistiques globales"""
    total_stops = len(df)
    # Ne plus diviser par 60 car c'est déjà en minutes
    avg_duration = df['STOP_DURATION_MINS'].mean()
    arrest_rate = (df['ARREST_CHARGES'].notna().sum() / total_stops * 100)
    ticket_rate = (df['TICKETS_ISSUED'].notna().sum() / total_stops * 100)
    
    return html.Div([
        html.H6(f"Nombre total d'arrêts: {total_stops:,}"),
        html.H6(f"Durée moyenne: {avg_duration:.1f} minutes"),
        html.H6(f"Taux d'arrestation: {arrest_rate:.1f}%"),
        html.H6(f"Taux de verbalisation: {ticket_rate:.1f}%")
    ])

def create_hourly_analysis(df):
    """Création de l'analyse horaire"""
    hourly_stats = get_hourly_stats(df)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    hourly_counts = df['hour'].value_counts().sort_index()
    fig.add_trace(
        go.Bar(x=hourly_counts.index, y=hourly_counts.values, 
               name="Nombre d'interventions", opacity=0.7),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=hourly_stats.index, y=hourly_stats['Taux arrestation (%)'],
                  name="Taux d'arrestation", line=dict(color='red')),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(x=hourly_stats.index, y=hourly_stats['Taux verbalisation (%)'],
                  name="Taux de verbalisation", line=dict(color='orange')),
        secondary_y=True
    )
    
    fig.update_layout(
        title="Analyse horaire des interventions",
        xaxis_title="Heure",
        yaxis_title="Nombre d'interventions",
        yaxis2_title="Taux (%)"
    )
    
    return fig

def create_stop_reasons_chart(df):
    """Création du graphique des raisons d'arrêt"""
    reasons = analyze_stop_reasons(df)
    
    return px.bar(
        x=reasons.values,
        y=reasons.index,
        orientation='h',
        title="Top 10 des raisons d'intervention",
        labels={'x': "Nombre d'interventions", 'y': "Raison"}
    )

def create_intervention_types(df):
    """Création du graphique des types d'intervention"""
    type_counts = df['intervention_type'].value_counts()
    
    return px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title="Distribution des types d'intervention",
        hole=0.4
    )

def create_temporal_heatmap(df):
    """Création de la heatmap temporelle"""
    heatmap_data = pd.crosstab(
        df['hour'],
        df['day_of_week']
    )
    
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data[days_order]
    
    return px.imshow(
        heatmap_data,
        title="Distribution des arrêts par heure et jour",
        labels=dict(x="Jour", y="Heure", color="Nombre d'arrêts")
    )

def create_weekly_patterns(df):
    """Création des patterns hebdomadaires"""
    weekly = pd.crosstab(df['day_of_week'], df['intervention_type'])
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly = weekly.reindex(days_order)
    
    return px.bar(
        weekly,
        barmode='stack',
        title="Distribution des interventions par jour",
        labels={'day_of_week': 'Jour', 'value': "Nombre d'interventions"}
    )

def create_ethnicity_analysis(df):
    """Analyse détaillée par ethnicité"""
    # Création de plusieurs sous-graphiques
    fig = make_subplots(rows=2, cols=2,
                       subplot_titles=("Distribution par ethnicité",
                                    "Durée moyenne par ethnicité",
                                    "Taux d'arrestation par ethnicité",
                                    "Types d'intervention par ethnicité"))
    
    # Distribution par ethnicité
    ethnicity_counts = df['ETHNICITY'].value_counts()
    fig.add_trace(
        go.Bar(x=ethnicity_counts.index, y=ethnicity_counts.values,
               name="Nombre d'arrêts"),
        row=1, col=1
    )
    
    # Durée moyenne par ethnicité
    duration_by_ethnicity = df.groupby('ETHNICITY')['STOP_DURATION_MINS'].mean()
    fig.add_trace(
        go.Bar(x=duration_by_ethnicity.index, y=duration_by_ethnicity.values,
               name="Durée moyenne"),
        row=1, col=2
    )
    
    # Taux d'arrestation par ethnicité
    arrest_by_ethnicity = df.groupby('ETHNICITY').apply(
        lambda x: (x['ARREST_CHARGES'].notna().sum() / len(x)) * 100
    )
    fig.add_trace(
        go.Bar(x=arrest_by_ethnicity.index, y=arrest_by_ethnicity.values,
               name="Taux d'arrestation"),
        row=2, col=1
    )
    
    # Types d'intervention par ethnicité
    intervention_by_ethnicity = pd.crosstab(df['ETHNICITY'], df['intervention_type'], normalize='index') * 100
    for intervention_type in df['intervention_type'].unique():
        fig.add_trace(
            go.Bar(x=intervention_by_ethnicity.index, 
                  y=intervention_by_ethnicity[intervention_type],
                  name=intervention_type),
            row=2, col=2
        )
    
    fig.update_layout(height=800, showlegend=True,
                     title_text="Analyse détaillée par ethnicité")
    return fig

def create_age_analysis(df):
    """Analyse détaillée par âge"""
    # Assurons-nous que AGE est numérique
    df_clean = df.copy()
    df_clean['AGE'] = pd.to_numeric(df_clean['AGE'], errors='coerce')
    
    fig = make_subplots(rows=2, cols=2,
                       subplot_titles=("Distribution des âges",
                                    "Âge moyen par type d'intervention",
                                    "Âge moyen par district",
                                    "Relation âge/durée d'intervention"))
    
    # Distribution des âges
    fig.add_trace(
        go.Histogram(x=df_clean['AGE'].dropna(), nbinsx=30, name="Distribution des âges"),
        row=1, col=1
    )
    
    # Âge moyen par type d'intervention
    age_by_type = df_clean.groupby('intervention_type')['AGE'].agg(lambda x: x.mean()).sort_values()
    fig.add_trace(
        go.Bar(x=age_by_type.index, y=age_by_type.values,
               name="Âge moyen"),
        row=1, col=2
    )
    
    # Âge moyen par district
    age_by_district = df_clean.groupby('STOP_DISTRICT')['AGE'].agg(lambda x: x.mean()).sort_values()
    fig.add_trace(
        go.Bar(x=age_by_district.index.astype(str), y=age_by_district.values,
               name="Âge moyen"),
        row=2, col=1
    )
    
    # Relation âge/durée
    fig.add_trace(
        go.Scatter(x=df_clean['AGE'].dropna(), 
                  y=df_clean['STOP_DURATION_MINS'].dropna(), 
                  mode='markers',
                  opacity=0.5, 
                  name="Âge vs Durée"),
        row=2, col=2
    )
    
    # Mise à jour de la mise en page
    fig.update_layout(
        height=800, 
        showlegend=True,
        title_text="Analyse détaillée par âge"
    )
    
    # Mise à jour des axes
    fig.update_xaxes(title_text="Âge", row=1, col=1)
    fig.update_xaxes(title_text="Type d'intervention", row=1, col=2)
    fig.update_xaxes(title_text="District", row=2, col=1)
    fig.update_xaxes(title_text="Âge", row=2, col=2)
    
    fig.update_yaxes(title_text="Nombre d'interventions", row=1, col=1)
    fig.update_yaxes(title_text="Âge moyen", row=1, col=2)
    fig.update_yaxes(title_text="Âge moyen", row=2, col=1)
    fig.update_yaxes(title_text="Durée (minutes)", row=2, col=2)
    
    return fig

def create_monthly_trends(df):
    """Analyse des tendances mensuelles"""
    df['month_year'] = df['DATETIME'].dt.to_period('M')
    monthly_data = df.groupby('month_year').agg({
        'STOP_DISTRICT': 'count',
        'ARREST_CHARGES': lambda x: x.notna().mean() * 100,
        'STOP_DURATION_MINS': 'mean',
        'intervention_score': 'mean'
    }).reset_index()
    monthly_data['month_year'] = monthly_data['month_year'].astype(str)
    
    fig = make_subplots(rows=2, cols=1,
                       subplot_titles=("Évolution mensuelle du nombre d'interventions",
                                    "Évolution des indicateurs mensuels"))
    
    # Nombre d'interventions
    fig.add_trace(
        go.Scatter(x=monthly_data['month_year'], 
                  y=monthly_data['STOP_DISTRICT'],
                  mode='lines+markers',
                  name="Nombre d'interventions"),
        row=1, col=1
    )
    
    # Indicateurs mensuels
    fig.add_trace(
        go.Scatter(x=monthly_data['month_year'],
                  y=monthly_data['ARREST_CHARGES'],
                  mode='lines+markers',
                  name="Taux d'arrestation (%)"),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_data['month_year'],
                  y=monthly_data['intervention_score'],
                  mode='lines+markers',
                  name="Score d'intervention"),
        row=2, col=1
    )
    
    fig.update_layout(height=800, showlegend=True,
                     title_text="Tendances mensuelles")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
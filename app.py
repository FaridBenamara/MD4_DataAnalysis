# app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import load_and_preprocess_data, DISTRICT_COORDINATES
import pandas as pd

# Chargement des données
df = load_and_preprocess_data()

# Création de l'application avec thème Bootstrap
app = dash.Dash(__name__, external_stylesheets=[
    'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
])

# Layout principal
app.layout = html.Div([
    # Navbar
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
                                        {'label': f'District {int(d)} - {DISTRICT_COORDINATES[d]["name"]}', 'value': d}
                                        for d in sorted(df['STOP_DISTRICT'].unique()) if not pd.isna(d)  # Ajout de la vérification pour NaN
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
        
        # Première rangée de visualisations
        html.Div(className="row mt-3", children=[
            # Carte principale
            html.Div(className="col-md-8", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Distribution géographique des interventions", 
                               className="card-title"),
                        dcc.Graph(id='main-map')
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
        
        # Deuxième rangée
        html.Div(className="row mt-3", children=[
            # Distribution temporelle
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Distribution temporelle", className="card-title"),
                        dcc.Graph(id='temporal-distribution')
                    ])
                ])
            ]),
            # Distribution ethnique
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Distribution ethnique", className="card-title"),
                        dcc.Graph(id='ethnicity-distribution')
                    ])
                ])
            ])
        ]),
        
        # Troisième rangée
        html.Div(className="row mt-3", children=[
            # Heatmap temporelle
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Patterns temporels", className="card-title"),
                        dcc.Graph(id='temporal-heatmap')
                    ])
                ])
            ])
        ]),
        
        # Quatrième rangée
        html.Div(className="row mt-3", children=[
            # Types d'interventions
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Types d'interventions", className="card-title"),
                        dcc.Graph(id='intervention-types')
                    ])
                ])
            ]),
            # Durée des interventions
            html.Div(className="col-md-6", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Durée des interventions", className="card-title"),
                        dcc.Graph(id='duration-analysis')
                    ])
                ])
            ])
        ]),
        
        # Cinquième rangée
        html.Div(className="row mt-3 mb-3", children=[
            # Analyse des tendances
            html.Div(className="col-md-12", children=[
                html.Div(className="card", children=[
                    html.Div(className="card-body", children=[
                        html.H5("Analyse des tendances", className="card-title"),
                        dcc.Graph(id='trends-analysis')
                    ])
                ])
            ])
        ])
    ])
])

# Callbacks
@app.callback(
    [Output('main-map', 'figure'),
     Output('global-stats', 'children'),
     Output('temporal-distribution', 'figure'),
     Output('ethnicity-distribution', 'figure'),
     Output('temporal-heatmap', 'figure'),
     Output('intervention-types', 'figure'),
     Output('duration-analysis', 'figure'),
     Output('trends-analysis', 'figure')],
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
    
    # 1. Carte principale
    map_fig = create_map_visualization(filtered_df)
    
    # 2. Statistiques globales
    stats_component = create_stats_component(filtered_df)
    
    # 3. Distribution temporelle
    temporal_fig = create_temporal_distribution(filtered_df)
    
    # 4. Distribution ethnique
    ethnicity_fig = create_ethnicity_distribution(filtered_df)
    
    # 5. Heatmap temporelle
    heatmap_fig = create_temporal_heatmap(filtered_df)
    
    # 6. Types d'interventions
    intervention_fig = create_intervention_types(filtered_df)
    
    # 7. Analyse des durées
    duration_fig = create_duration_analysis(filtered_df)
    
    # 8. Analyse des tendances
    trends_fig = create_trends_analysis(filtered_df)
    
    return (map_fig, stats_component, temporal_fig, ethnicity_fig,
            heatmap_fig, intervention_fig, duration_fig, trends_fig)

# Fonctions de création des visualisations
def create_map_visualization(df):
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
        zoom=11,
        title="Distribution des arrêts par district"
    )

def create_stats_component(df):
    total_stops = len(df)
    avg_duration = df['STOP_DURATION_MINS'].mean()
    arrest_rate = (df['ARREST_CHARGES'].notna().sum() / total_stops * 100)
    ticket_rate = (df['TICKETS_ISSUED'].notna().sum() / total_stops * 100)
    
    return html.Div([
        html.H6(f"Nombre total d'arrêts: {total_stops:,}"),
        html.H6(f"Durée moyenne: {avg_duration:.1f} minutes"),
        html.H6(f"Taux d'arrestation: {arrest_rate:.1f}%"),
        html.H6(f"Taux de verbalisation: {ticket_rate:.1f}%")
    ])

def create_temporal_distribution(df):
    hourly_counts = df['hour'].value_counts().sort_index()
    
    return px.line(
        x=hourly_counts.index,
        y=hourly_counts.values,
        title="Distribution horaire des arrêts",
        labels={'x': 'Heure', 'y': 'Nombre d\'arrêts'}
    )

def create_ethnicity_distribution(df):
    ethnicity_counts = df['ETHNICITY'].value_counts()
    
    return px.pie(
        values=ethnicity_counts.values,
        names=ethnicity_counts.index,
        title="Distribution par ethnicité",
        hole=0.4
    )

def create_temporal_heatmap(df):
    heatmap_data = pd.crosstab(df['hour'], df['day_of_week'])
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data[days_order]
    
    return px.imshow(
        heatmap_data,
        title="Distribution des arrêts par heure et jour",
        labels=dict(x="Jour", y="Heure", color="Nombre d'arrêts"),
        aspect="auto"
    )

def create_intervention_types(df):
    intervention_counts = df['intervention_type'].value_counts()
    
    return px.bar(
        x=intervention_counts.index,
        y=intervention_counts.values,
        title="Types d'interventions",
        labels={'x': 'Type', 'y': 'Nombre'}
    )

def create_duration_analysis(df):
    return px.box(
        df,
        x='intervention_type',
        y='STOP_DURATION_MINS',
        title="Distribution des durées par type d'intervention"
    )

def create_trends_analysis(df):
    daily_counts = df.groupby(df['DATETIME'].dt.date).size()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_counts.index,
        y=daily_counts.values,
        mode='lines',
        name='Nombre d\'arrêts'
    ))
    
    fig.update_layout(
        title="Évolution du nombre d'arrêts dans le temps",
        xaxis_title="Date",
        yaxis_title="Nombre d'arrêts"
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
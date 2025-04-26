import json
from dash import html, dcc, Input, Output, State, ALL
import base64
import io
import pandas as pd
import plotly.graph_objs as go
from app_data import app_data
from datetime import datetime
import os
import numpy as np

# Laad de kleuren en tinten uit het JSON-bestand
with open("data/colors.json", "r") as f:
    COLORS = json.load(f)

def layout(app):
    return html.Div([
        html.H2("📊 Dashboard"),
        dcc.Upload(
            id='upload-data',
            children=html.Button('📤 Upload CSV-bestanden'),
            multiple=True  # Meerdere bestanden toestaan
        ),
        html.Div(id='upload-output'),
        html.Label("X-as kolom:"),
        dcc.Dropdown(id='x-axis'),
        html.Label("Y-as kolommen:"),
        dcc.Dropdown(id='y-axis', multi=True),
        html.Label("Kleuren per Y-as:"),
        html.Div(id='color-selectors'),  # Dynamische kleurselectie
        html.Label("Chart type:"),
        dcc.Dropdown(
            id='chart-type',
            options=[{'label': i, 'value': i} for i in ['line', 'bar', 'scatter']],
            value='line'
        ),
        html.Label("Titel van de visualisatie:"),
        dcc.Input(id='dashboard-title', type='text', placeholder='Voer een titel in...', style={'width': '100%', 'marginBottom': '10px'}),
        html.Label("Toelichting:"),
        dcc.Textarea(id='description', style={'width': '100%', 'height': 100}),
        html.Button("📈 Genereer", id='generate-btn'),
        dcc.Graph(id='plot'),
        html.Button("✅ Publiceer", id='publish-btn'),
        html.Div(id='publish-status')
    ])

def register_callbacks(app):
    @app.callback(
        [Output('upload-output', 'children'),
         Output('x-axis', 'options'),
         Output('y-axis', 'options')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def handle_upload(contents_list, filenames):
        if contents_list is None:
            return "❌ Geen bestanden geüpload.", [], []

        try:
            dfs = []  # Lijst om dataframes op te slaan
            for contents, filename in zip(contents_list, filenames):
                # Decode de inhoud van elk bestand
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)

                # Probeer elk bestand te lezen met verschillende coderingen
                try:
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                except UnicodeDecodeError:
                    df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))

                dfs.append(df)  # Voeg het dataframe toe aan de lijst

            # Combineer alle dataframes
            combined_df = pd.concat(dfs, ignore_index=True)

            # Sla het gecombineerde dataframe op in app_data
            app_data['df'] = combined_df

            # Genereer opties voor de dropdowns
            options = [{'label': col, 'value': col} for col in combined_df.columns]
            return f"✅ {len(filenames)} bestanden succesvol geüpload en gecombineerd.", options, options

        except Exception as e:
            # Foutafhandeling
            return f"❌ Fout bij het verwerken van de bestanden: {e}", [], []

    @app.callback(
        Output('color-selectors', 'children'),
        Input('y-axis', 'value')
    )
    def update_color_selectors(y_columns):
        if not y_columns:
            return "❌ Selecteer eerst Y-as kolommen."
        
        dropdowns = []
        for col in y_columns:
            options = []
            for color_name, shades in COLORS.items():
                for shade, code in shades.items():
                    options.append({'label': f"{color_name} {shade}", 'value': code})
            
            dropdowns.append(html.Div([
                html.Label(f"Kleur voor {col}:"),
                dcc.Dropdown(
                    id={'type': 'color-dropdown', 'index': col},
                    options=options,
                    value=list(COLORS.values())[0]["100%"]  # Standaardkleur (100%)
                )
            ], style={"marginBottom": "10px"}))
        
        return dropdowns

    @app.callback(
        Output('plot', 'figure'),
        Input('generate-btn', 'n_clicks'),
        State('x-axis', 'value'),
        State('y-axis', 'value'),
        State('chart-type', 'value'),
        State({'type': 'color-dropdown', 'index': ALL}, 'value')  # Haal kleuren op
    )
    def generate_chart(n, x, ys, chart_type, colors):
        df = app_data.get('df')
        fig = go.Figure()
        if df is None or x is None or not ys:
            return fig
        
        for i, y in enumerate(ys):
            color = colors[i] if i < len(colors) else "#000000"  # Gebruik zwart als fallback
            if chart_type == 'line':
                fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='lines+markers', name=y, line=dict(color=color)))
            elif chart_type == 'bar':
                fig.add_trace(go.Bar(x=df[x], y=df[y], name=y, marker=dict(color=color)))
            elif chart_type == 'scatter':
                fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='markers', name=y, marker=dict(color=color)))
        
        app_data['graph'] = fig
        return fig

    @app.callback(
        Output('publish-status', 'children'),
        Input('publish-btn', 'n_clicks'),
        State('dashboard-title', 'value'),
        State('description', 'value')
    )
    def publish(n, title, desc):
        if not n:
            return "❌ Geen actie uitgevoerd. Klik op de knop om te publiceren."

        # Controleer of er een grafiek beschikbaar is
        if 'graph' not in app_data or app_data['graph'] is None:
            return "❌ Geen grafiek beschikbaar om op te slaan. Genereer eerst een grafiek."

        # Controleer of er een titel is
        if not title:
            return "❌ Titel is verplicht om te publiceren."

        # Controleer of er een beschrijving is
        if not desc:
            return "❌ Beschrijving is verplicht om te publiceren."

        try:
            # Maak een record aan voor de grafiek
            figure_json = app_data["graph"].to_plotly_json()

            # Converteer numpy-arrays naar lijsten
            def convert_ndarray(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj

            # Recursief door de JSON-structuur lopen en arrays omzetten
            figure_json = json.loads(json.dumps(figure_json, default=convert_ndarray))

            record = {
                "title": title,
                "description": desc,
                "user": app_data.get("current_user", "Onbekend"),
                "timestamp": datetime.now().isoformat(),
                "figure": figure_json
            }

            # Controleer of de opslagmap bestaat
            os.makedirs("storage", exist_ok=True)

            # Schrijf het record naar het bestand
            with open("storage/saved_graphs.json", "a") as f:
                f.write(json.dumps(record) + "\n")

            return f"✅ Visualisatie '{title}' succesvol opgeslagen en gepubliceerd!"

        except Exception as e:
            # Foutafhandeling
            return f"❌ Fout bij het opslaan van de visualisatie: {e}"

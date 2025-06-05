# TODO: wanneer een nieuw bestand wordt geselecteerd, verwijder de oude data.

import json
from dash import html, dcc, Input, Output, State, ALL, MATCH
import base64
import io
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from app_data import app_data
from datetime import datetime
import os
import numpy as np

# Laad de kleuren en tinten uit het JSON-bestand
with open("data/colors.json", "r") as f:
    COLORS = json.load(f)

COLOR_CODES = {}
COLOR_NAMES = {}
for color_name, shades in COLORS.items():
    for shade, code in shades.items():
        COLOR_CODES[f"{color_name} {shade}"] = code
        COLOR_NAMES[code] = f"{color_name} {shade}"

COLOR_EMOJIS = {
    "Lintblauw": "🟦",
    "Rood": "🟥",
    "Geel": "🟨",
    "Groen": "🟩",
    "Oranje": "🟧",
    "Paars": "🟪",
    "Zwart": "⬛",
    "Grijs": "⬜",
    # Voeg meer toe indien gewenst
}

HEATMAP_COLORS = ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Greens", "YlGnBu", "YlOrRd", "RdBu", "Picnic", "Jet"]

def layout(app):
    return html.Div([
        html.H2("📊 Dashboard", style={
            "textAlign": "center",
            "marginBottom": "30px",
            "color": "#CA005D",
            "fontWeight": "bold",
            "fontSize": "2rem"
        }),

        # Upload card
        html.Div([
            html.H4("1. Upload je CSV-bestanden", style={"marginBottom": "10px"}),
            dcc.Upload(
                id='upload-data',
                children=html.Button('📤 Upload CSV-bestanden', style={
                    "backgroundColor": "#CA005D",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "5px",
                    "padding": "10px 20px",
                    "fontWeight": "bold",
                    "cursor": "pointer"
                }),
                multiple=True
            ),
            html.Div(id='upload-output', style={"marginTop": "10px", "color": "#333"})
        ], style={
            "backgroundColor": "#f7f7f7",
            "padding": "24px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "marginBottom": "30px",
            "maxWidth": "600px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }),

        # Upload bouwblok.
        html.Div([
            html.H4("X. Upload json-export-bestanden fdsfdsfd", style={"marginBottom": "10px"}),
            dcc.Upload(
                id='upload-export-data',
                children=html.Button('📤 Upload json-export-bestanden', style={
                    "backgroundColor": "#CA005D",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "5px",
                    "padding": "10px 20px",
                    "fontWeight": "bold",
                    "cursor": "pointer"
                }),
            ),
            html.Div(id='upload-export-output', style={"marginTop": "10px", "color": "#333"})
        ], style={
            "backgroundColor": "#f7f7f7",
            "padding": "24px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "marginBottom": "30px",
            "maxWidth": "600px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }),

        html.Div([
            html.H4("X. Kies het visualisatietype", style={"marginBottom": "10px"}),
            html.Div([
                html.Label("Chart type:", style={
                    "fontWeight": "bold",
                    "minWidth": "140px",
                    "marginRight": "12px"
                }),
                dcc.Dropdown(
                    id='chart-type',
                    options=[
                        {'label': 'Lijn (Line)', 'value': 'line'},
                        {'label': 'Staaf (Bar)', 'value': 'bar'},
                        {'label': 'Punten (Scatter)', 'value': 'scatter'},
                        {'label': 'Taartdiagram (Pie)', 'value': 'pie'},
                        {'label': 'Histogram', 'value': 'histogram'},
                        {'label': 'Boxplot', 'value': 'box'},
                        # {'label': 'Violinplot', 'value': 'violin'},
                        {'label': 'Heatmap', 'value': 'heatmap'},
                        # {'label': 'Area', 'value': 'area'},
                        # {'label': 'Bubble', 'value': 'bubble'},
                        # {'label': 'Funnel', 'value': 'funnel'},
                        # {'label': 'Sunburst', 'value': 'sunburst'},
                        # {'label': 'Treemap', 'value': 'treemap'},
                        # {'label': 'Polar', 'value': 'polar'},
                        # {'label': '3D Scatter', 'value': 'scatter3d'},
                        # {'label': '3D Surface', 'value': 'surface'},
                    ],
                    style={"width": "100%"}
                )
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
        ], style={
            "backgroundColor": "#f7f7f7",
            "padding": "24px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "marginBottom": "30px",
            "maxWidth": "600px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }),

        # Instellingen card
        html.Div(children=[
            html.H4("2. Instellingen", style={"marginBottom": "18px"}),

            html.Div([
                html.Div([
                    html.Label("x-as:", style={
                        "fontWeight": "bold",
                        "minWidth": "140px",
                        "marginRight": "12px"
                    }),
                    dcc.Dropdown(id='x-axis', style={"width": "100%"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
            ], style={"marginBottom": "18px"}),

            html.Div([
                html.Div([
                    html.Label("y-as:", style={
                        "fontWeight": "bold",
                        "minWidth": "140px",
                        "marginRight": "12px"
                    }),
                    dcc.Dropdown(id='y-axis', style={"width": "100%"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
            ], style={"marginBottom": "18px"}),

            html.Div(id="nbins-section", children=[
                html.Div([
                    html.Label("nbins:", style={
                        "fontWeight": "bold",
                        "minWidth": "140px",
                        "marginRight": "12px"
                    }),
                    dcc.Input(id='nbins', type="number", style={"width": "75%", "padding": "6px 12px", "border": "1px solid #ced4da", "borderRadius": "4px", "backgroundColor": "white", "fontSize": "14px", "height": "36px", "boxSizing": "border-box"})
                ], style={"display": "flex", "alignItems": "space-between", "marginBottom": "12px"}),
            ], style={"marginBottom": "18px"}),

            html.Div(id="heatmap-value-section", children=[
                html.Div([
                    html.Label("waardekolom:", style={
                        "fontWeight": "bold",
                        "minWidth": "140px",
                        "marginRight": "12px"
                    }),
                    dcc.Dropdown(id='heatmap-dropdown', style={"width": "100%"})
                ], style={"display": "flex", "alignItems": "space-between", "marginBottom": "12px"}),
            ], style={"marginBottom": "18px"}),

            html.Div([
                html.Div([
                    html.Label("Kleur toepassen:", style={
                        "fontWeight": "bold",
                        "minWidth": "140px",
                        "marginRight": "12px"
                    }),
                    dcc.Dropdown(id='column-to-color', style={"width": "100%"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),
            ], style={"marginBottom": "18px"}),

            html.Label("Kleuren:", style={"fontWeight": "bold", "marginTop": "10px"}),
            html.Div(id='color-selectors', style={"marginBottom": "18px"}),

            html.Div([
                html.Div([
                    html.Label("Titel van de visualisatie:", style={"fontWeight": "bold"}),
                    dcc.Input(
                        id='dashboard-title',
                        type='text',
                        placeholder='Voer een titel in...',
                        style={'width': '100%', 'marginBottom': '10px'}
                    )
                ], style={"marginBottom": "18px"}),
            ], style={"marginBottom": "18px"}),

            html.Label("Toelichting:", style={"fontWeight": "bold"}),
            dcc.Textarea(id='description', style={'width': '100%', 'height': 80, "marginBottom": "18px"}),
        ], style={
            "backgroundColor": "#f7f7f7",
            "padding": "24px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "marginBottom": "30px",
            "maxWidth": "900px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }),

        # Genereer-knop en grafiek
        html.Div([
            html.Button("📈 Genereer", id='generate-btn', style={
                "backgroundColor": "#CA005D",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "padding": "10px 30px",
                "fontWeight": "bold",
                "fontSize": "1rem",
                "cursor": "pointer",
                "marginBottom": "20px"
            }),
            dcc.Graph(id='plot', style={"backgroundColor": "white", "borderRadius": "10px", "boxShadow": "0 2px 8px rgba(0,0,0,0.07)"})
        ], style={
            "backgroundColor": "#fff",
            "padding": "24px",
            "borderRadius": "10px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.07)",
            "marginBottom": "30px",
            "maxWidth": "900px",
            "marginLeft": "auto",
            "marginRight": "auto"
        }),

        # Publiceer-knop
        html.Div([
            html.Button("✅ Publiceer", id='publish-btn', style={
                "backgroundColor": "#009966",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "padding": "10px 30px",
                "fontWeight": "bold",
                "fontSize": "1rem",
                "cursor": "pointer",
                "marginRight": "20px"
            }),
            html.Span(id='publish-status', style={"fontWeight": "bold", "color": "#CA005D"})
        ], style={
            "textAlign": "center",
            "marginBottom": "40px"
        })
    ], style={
        "backgroundColor": "#f2f2f2",
        "minHeight": "100vh",
        "paddingTop": "30px",
        "paddingBottom": "30px"
    })

def register_callbacks(app):
    @app.callback(
        [Output('upload-output', 'children'),
         Output('x-axis', 'options'),
         Output('y-axis', 'options'),
         Output('column-to-color', 'options'),
         Output('heatmap-dropdown', 'options', allow_duplicate=True)],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')],
        prevent_initial_call=True
    )
    def handle_upload(contents_list, filenames):
        if contents_list is None:
            return "❌ Geen bestanden geüpload.", [], [], []
        try:
            dfs = []  # Lijst om dataframes op te slaan
            for contents, filename in zip(contents_list, filenames):
                # Decode de inhoud van elk bestand
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)

                # Detecteer bestandstype en lees in
                if filename.lower().endswith('.csv'):
                    try:
                        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                    except UnicodeDecodeError:
                        df = pd.read_csv(io.StringIO(decoded.decode('latin-1')))
                elif filename.lower().endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(io.BytesIO(decoded))
                else:
                    continue  # Sla onbekende bestandstypes over

                dfs.append(df)  # Voeg het dataframe toe aan de lijst

            if not dfs:
                return "❌ Geen geldige CSV of Excel bestanden geüpload.", [], [], []

            # Combineer alle dataframes
            combined_df = pd.concat(dfs, ignore_index=True)#.head(5) # TODO: remove .head call.

            # Sla het gecombineerde dataframe op in app_data
            app_data['df'] = combined_df
            app_data['parameters'] = {
                "dataframe": combined_df.to_dict(),
                "length": combined_df.shape[0],
                "columns": list(combined_df.columns),
            }

            dropdown_values = HEATMAP_COLORS

            # Genereer opties voor de dropdowns
            options = [{'label': col, 'value': col} for col in combined_df.columns]
            return f"✅ {len(dfs)} bestand(en) succesvol geüpload en gecombineerd.", options, options, dropdown_values, options

        except Exception as e:
            # Foutafhandeling
            return f"❌ Fout bij het verwerken van de bestanden: {e}", [], [], [], []

    @app.callback(
        [Output('upload-export-output', 'children'),
         Output('plot', 'figure', allow_duplicate=True),
         Output('column-to-color', 'options', allow_duplicate=True),
         Output('x-axis', 'options', allow_duplicate=True),
         Output('y-axis', 'options', allow_duplicate=True),
         Output('chart-type', 'value', allow_duplicate=True)],
         Output('x-axis', 'value'),
         Output('y-axis', 'value'),
         Output('column-to-color', 'value'),
         Output('nbins', 'value'),
         Output('heatmap-dropdown', 'options'),
         Output('heatmap-dropdown', 'value'),
        [Input('upload-export-data', 'contents')],
        [State('upload-export-data', 'filename')],
        prevent_initial_call=True
    )
    def handle_export_file_upload(content, filename):
        if not filename.lower().endswith('.json'):
            return ["❌ Upload een JSON bestand.", None, [], [], [], None, None, None, None, 0, None, ""]

        _content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        try:
            content_io = io.StringIO(decoded.decode('utf-8'))
        except UnicodeDecodeError:
            content_io = io.StringIO(decoded.decode('latin-1'))

        content_str = content_io.read()
        content = json.loads(content_str)

        graph = content["figureContents"]
        app_data["graph"] = graph
        app_data["parameters"] = content["parameters"]
        x = app_data["parameters"]["x"]
        y = app_data["parameters"].get("y")
        column_to_color = app_data["parameters"].get("columnToColor")
        app_data['df'] = pd.DataFrame(app_data["parameters"]["dataframe"])

        nbins = 0
        if content["parameters"]["chartType"] == "histogram":
            nbins = app_data["parameters"]["nbins"]

        options = [{'label': col, 'value': col} for col in content["parameters"]["columns"]]

        dropdown_values = []
        value_column = None
        if content["parameters"]["chartType"] == "heatmap":
            dropdown_values = HEATMAP_COLORS
            column_to_color = content["parameters"]["colorContinuousScale"]
            value_column = content["parameters"]["valueColumn"]
        else:
            dropdown_values = options

        return [f"✅ Geselecteerd bestand: {filename}", graph, dropdown_values, options, options, content["parameters"]["chartType"], x, y, column_to_color, nbins, options, value_column]


    @app.callback(
        Output('column-to-color', 'disabled'),
        Input('chart-type', 'value'),
        prevent_initial_call=True
    )
    def disable_color_dropdown(chart_type):
        return chart_type == "scatter" or chart_type == "histogram"

    @app.callback(
        Output('y-axis', 'disabled'),
        Input('chart-type', 'value'),
        prevent_initial_call=True
    )
    def disable_y_dropdown(chart_type):
        return chart_type == "histogram"

    @app.callback(
        Output('nbins-section', 'style'),
        Input('chart-type', 'value'),
    )
    def show_nbins_section(chart_type):
        if chart_type == "histogram":
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('heatmap-value-section', 'style'),
        Input('chart-type', 'value'),
    )
    def show_heatmap_value_section(chart_type):
        if chart_type == "heatmap":
            return {'display': 'block'}
        else:
            return {'display': 'none'}

    @app.callback(
        Output('color-selectors', 'children'),
        Input('column-to-color', 'value'),
        Input('chart-type', 'value'),
    )
    def update_color_selectors(column_to_color, chart_type):
        if not column_to_color and not chart_type == "scatter" and not chart_type == "histogram":
            return "❌ Selecteer de kolom die gekleurd moet worden."
        
        if "parameters" not in app_data or "df" not in app_data:
            return "❌ Selecteer een dataset."

        if chart_type == "heatmap":
            return "Gebruik de waardekolom dropdown voor een kleur."

        dropdowns = []

        length = 0
        if chart_type == "line" or chart_type == "box":
            length = app_data['df'][column_to_color].unique().shape[0]
        elif chart_type == "scatter" or chart_type == "histogram":
            length = 1
        else:
            length = app_data["parameters"]["length"]

        for col in range(0, length):
            color_from_module = None
            if "colors" in app_data["parameters"]:
                color_amount = len(app_data["parameters"]["colors"])
                color_from_module = app_data["parameters"]["colors"][col % color_amount]

            options = []
            for color_name, shades in COLORS.items():
                for shade, code in shades.items():
                    naam_tint = f"{color_name} {shade}"
                    options.append({
                        'label': f"{color_name} {shade}",
                        'value': naam_tint
                    })
            # Zet standaardkleur
            default_value = list(COLORS.keys())[0] + " 100%"
            default_color = COLOR_CODES.get(default_value, "#000000")
            dropdowns.append(
                html.Div([
                    html.Label(f"Kleur voor {col + 1}:", style={
                        "minWidth": "120px",
                        "marginRight": "16px",
                        "fontWeight": "bold"
                    }),
                    html.Div([
                        html.Div(
                            id={'type': 'color-preview', 'index': col},
                            style={
                                'display': 'inline-block',
                                'width': '32px',
                                'height': '32px',
                                'verticalAlign': 'middle',
                                'marginRight': '16px',
                                'backgroundColor': default_color,
                                'border': '1px solid #888'
                            }
                        ),
                        dcc.Dropdown(
                            id={'type': 'color-dropdown', 'index': col},
                            options=options,
                            value=COLOR_NAMES[color_from_module] if color_from_module else default_value,
                            style={
                                'width': '200px',
                                'display': 'inline-block',
                                'verticalAlign': 'middle'
                            }
                        ),
                    ], style={
                        "display": "flex",
                        "alignItems": "center"
                    })
                ], style={
                    "display": "flex",
                    "alignItems": "center",
                    "marginBottom": "18px",
                    "gap": "12px"
                })
            )
        return dropdowns

    @app.callback(
        Output('plot', 'figure'),
        Input('generate-btn', 'n_clicks'),
        State('x-axis', 'value'),
        State('y-axis', 'value'),
        State('column-to-color', 'value'),
        State('chart-type', 'value'),
        State({'type': 'color-dropdown', 'index': ALL}, 'value'), # Haal kleuren op
        State('nbins', 'value'),
        State('heatmap-dropdown', 'value'),
    )
    def generate_chart(n, x, y, column_to_color, chart_type, colors, nbins, value_column):
        df = app_data.get('df')
        fig = go.Figure()

        if "parameters" in app_data and "dataframe" in app_data["parameters"]:
            df = pd.DataFrame(app_data["parameters"]["dataframe"])

        select_colors = []
        if colors is not None:
            for color in colors:
                color_code = COLOR_CODES.get(color)
                if color_code is None:
                    continue
                select_colors.append(color_code)

        if chart_type == 'bar':
            fig = px.bar(df, x=x, y=y, color=column_to_color, color_discrete_sequence=select_colors)
        elif chart_type == "pie":
            fig = px.pie(df, values=x, names=y, color=column_to_color, color_discrete_sequence=select_colors)
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, color=column_to_color, color_discrete_sequence=select_colors)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x, y=y, color_discrete_sequence=select_colors)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x, y=y, nbins=nbins, color_discrete_sequence=select_colors)
        elif chart_type == "box":
            fig = px.box(df, x=x, y=y, color=column_to_color, color_discrete_sequence=select_colors)
        elif chart_type == "heatmap":
            heatmap_data = df.pivot(index=x, columns=y, values=value_column)
            fig = px.imshow(
                heatmap_data,
                labels=dict(x=x, y=y, color=value_column),
                color_continuous_scale=column_to_color,
            )

        # for i, y in enumerate(ys):
        #     naam_tint = colors[i] if i < len(colors) else None
        #     color = COLOR_CODES.get(naam_tint, "#000000")
        #     if chart_type == 'line':
        #         fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='lines+markers', name=y, line=dict(color=color)))
        #     elif chart_type == 'bar':
        #         fig.add_trace(go.Bar(x=df[x], y=df[y], name=y, marker=dict(color=color)))
        #     elif chart_type == 'scatter':
        #         fig.add_trace(go.Scatter(x=df[x], y=df[y], mode='markers', name=y, marker=dict(color=color)))
        #     elif chart_type == 'area':
        #         fig.add_trace(go.Scatter(x=df[x], y=df[y], fill='tozeroy', mode='lines', name=y, line=dict(color=color)))
        #     elif chart_type == 'bubble':
        #         fig.add_trace(go.Scatter(
        #             x=df[x], y=df[y], mode='markers', name=y,
        #             marker=dict(size=df[y], color=color, sizemode='area', sizeref=2.*max(df[y])/(40.**2), sizemin=4)
        #         ))
        #     elif chart_type == 'histogram':
        #         fig.add_trace(go.Histogram(x=df[y], name=y, marker=dict(color=color)))
        #     elif chart_type == 'box':
        #         fig.add_trace(go.Box(y=df[y], name=y, marker=dict(color=color)))
        #     elif chart_type == 'violin':
        #         fig.add_trace(go.Violin(y=df[y], name=y, line=dict(color=color)))
        #     elif chart_type == 'heatmap':
        #         if len(ys) > 1 and x in df.columns:
        #             fig.add_trace(go.Heatmap(z=df[ys].values, x=df[x], y=ys, colorscale='Viridis'))
        #             break
        #         else:
        #             fig.add_trace(go.Heatmap(z=[df[y].values], x=df[x], y=[y], colorscale='Viridis'))
        #     elif chart_type == 'pie':
        #         fig = go.Figure(go.Pie(labels=df[x], values=df[y], marker=dict(colors=[color])))
        #         break
        #     elif chart_type == 'donut':
        #         fig = go.Figure(go.Pie(labels=df[x], values=df[y], hole=0.4, marker=dict(colors=[color])))
        #         break
        #     elif chart_type == 'funnel':
        #         fig = go.Figure(go.Funnel(y=df[x], x=df[y], marker=dict(color=color)))
        #         break
        #     elif chart_type == 'sunburst':
        #         fig = go.Figure(go.Sunburst(labels=df[x], parents=[""]*len(df[x]), values=df[y]))
        #         break
        #     elif chart_type == 'treemap':
        #         fig = go.Figure(go.Treemap(labels=df[x], parents=[""]*len(df[x]), values=df[y]))
        #         break
        #     elif chart_type == 'polar':
        #         fig.add_trace(go.Scatterpolar(r=df[y], theta=df[x], mode='lines+markers', name=y, line=dict(color=color)))
        #     elif chart_type == 'scatter3d':
        #         if len(ys) >= 3:
        #             fig = go.Figure(go.Scatter3d(
        #                 x=df[ys[0]], y=df[ys[1]], z=df[ys[2]],
        #                 mode='markers', marker=dict(color=color), name="3D Scatter"
        #             ))
        #             break
        #     elif chart_type == 'surface':
        #         if len(ys) >= 3:
        #             fig = go.Figure(go.Surface(
        #                 z=df[ys[2]].values.reshape((len(df[ys[0]].unique()), len(df[ys[1]].unique()))),
        #                 x=df[ys[0]].unique(), y=df[ys[1]].unique(), colorscale='Viridis'
        #             ))
        #             break

        app_data['graph'] = fig
        return fig

    @app.callback(
        Output('publish-status', 'children'),
        Input('publish-btn', 'n_clicks'),
        State('dashboard-title', 'value'),
        State('description', 'value'),
        State('chart-type', 'value'),
    )
    def publish(n, title, desc, chart_type):
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

        if not chart_type:
            return "❌ Kiez een visualisatietype."

        try:
            # Maak een record aan voor de grafiek
            if hasattr(app_data["graph"], "to_plotly_json"):
                figure_json = app_data["graph"].to_plotly_json()
            else:
                figure_json = app_data["graph"]

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
                "timestamp": datetime.now().strftime("%Y-%m-%d"),
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

    @app.callback(
        Output({'type': 'color-preview', 'index': MATCH}, 'style'),
        Input({'type': 'color-dropdown', 'index': MATCH}, 'value')
    )
    def update_color_preview(naam_tint):
        color = COLOR_CODES.get(naam_tint, "#000000")
        return {
            'display': 'inline-block',
            'width': '32px',
            'height': '32px',
            'verticalAlign': 'middle',
            'marginLeft': '10px',
            'backgroundColor': color,
            'border': '1px solid #888'
        }

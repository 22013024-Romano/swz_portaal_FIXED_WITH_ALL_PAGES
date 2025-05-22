from dash import html, dcc, Input, Output, State, ALL
import dash
import json
import os
import plotly.graph_objs as go
from app_data import app_data  # Controleer de authenticatiestatus

def layout(app):
    return html.Div([
        html.H2("🖼️ Galerij", style={
            "textAlign": "center",
            "marginBottom": "30px",
            "color": "#CA005D",
            "fontWeight": "bold"
        }),
        html.Div(
            dcc.Input(
                id="search-input",
                type="text",
                placeholder="🔍 Zoek op titel...",
                style={
                    "marginBottom": "20px",
                    "width": "60%",
                    "padding": "10px",
                    "borderRadius": "6px",
                    "border": "1px solid #ccc",
                    "display": "inline-block"
                }
            ),
            style={"textAlign": "center"}
        ),
        html.Div(id="search-results", style={"marginTop": "20px"})
    ], style={
        "backgroundColor": "#f7f7f7",
        "minHeight": "100vh",
        "padding": "30px"
    })

def register_callbacks(app):
    @app.callback(
        Output('search-results', 'children'),
        [Input('search-input', 'value'),
         Input({'type': 'delete-button', 'index': ALL}, 'n_clicks')],
        State('search-input', 'value')
    )
    def update_gallery(search_term, n_clicks, search_state):
        try:
            path = "storage/saved_graphs.json"
            if not os.path.exists(path):
                return html.Div("⚠️ Geen opgeslagen visualisaties gevonden.", style={"margin": "30px", "color": "#CA005D"})

            # Laad alle records
            with open(path, "r") as f:
                records = [json.loads(line) for line in f]

            # Verwijderfunctionaliteit op basis van unieke timestamp
            triggered = dash.callback_context.triggered
            if n_clicks and any(click is not None for click in n_clicks):
                if not app_data['is_authenticated']:
                    return "❌ Alleen ingelogde gebruikers kunnen dashboards verwijderen."

                # Zoek welke knop is geklikt
                for t in triggered:
                    prop_id = t['prop_id']
                    if prop_id.startswith("{"):
                        btn_id = json.loads(prop_id.split('.')[0])
                        if btn_id.get('type') == 'delete-button':
                            # Vind het record met deze unieke timestamp
                            delete_timestamp = btn_id.get('index')
                            records = [rec for rec in records if rec.get('timestamp') != delete_timestamp]
                            # Schrijf terug
                            with open(path, "w") as f:
                                for record in records:
                                    f.write(json.dumps(record) + "\n")
                            break  # Slechts één verwijderen per klik

            # Zoekfunctionaliteit
            results = []
            for record in records:
                if (
                    not search_term
                    or search_term.lower() in record.get("title", "").lower()
                    or search_term.lower() in record.get("description", "").lower()
                ):
                    results.append(record)

            if not results:
                return html.Div("⚠️ Geen resultaten gevonden.", style={"margin": "30px", "color": "#CA005D"})

            # Toon de resultaten als cards over de hele breedte
            return html.Div([
                html.Div([
                    html.Div([
                        html.H4(rec['title'], style={"marginBottom": "8px", "color": "#CA005D"}),
                        html.P(f"Beschrijving: {rec['description']}", style={"marginBottom": "8px"}),
                        html.Small(f"Gebruiker: {rec['user']} – Datum: {rec['timestamp']}", style={"color": "#888"}),
                        dcc.Graph(
                            figure=go.Figure(rec['figure']),
                            config={"displayModeBar": True},
                            style={"height": "320px", "marginTop": "10px"}
                        ),
                        html.Button(
                            "Verwijderen",
                            id={'type': 'delete-button', 'index': rec['timestamp']},  # Gebruik timestamp als unieke index
                            style={
                                "marginTop": "12px",
                                "backgroundColor": "#CA005D",
                                "color": "white",
                                "border": "none",
                                "borderRadius": "5px",
                                "padding": "8px 18px",
                                "fontWeight": "bold",
                                "cursor": "pointer",
                                "display": "block" if app_data['is_authenticated'] else "none"
                            }
                        )
                    ], style={
                        "background": "white",
                        "borderRadius": "12px",
                        "boxShadow": "0 2px 8px rgba(0,0,0,0.09)",
                        "padding": "28px",
                        "margin": "0 auto 32px auto",
                        "width": "100%",
                        "maxWidth": "1100px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "space-between"
                    })
                ]) for rec in results
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center"
            })

        except Exception as e:
            return html.Div(f"❌ Fout bij het verwerken: {e}", style={"color": "#CA005D", "margin": "30px"})

from dash import html, dcc, Input, Output, State, ALL
import dash
import json
import os
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
    
    def logout_user(n_clicks):
        if n_clicks:
            # Zet de authenticatiestatus op False
            app_data['is_authenticated'] = False
            app_data['current_user'] = None
            return "/login"  # Stuur de gebruiker naar de loginpagina
        return dash.no_update

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

            # Verwijderfunctionaliteit
            if n_clicks and any(click is not None for click in n_clicks):
                if not app_data['is_authenticated']:
                    return "❌ Alleen ingelogde gebruikers kunnen dashboards verwijderen."

                # Zoek het dashboard dat moet worden verwijderd
                with open(path, "r") as f:
                    records = [json.loads(line) for line in f]

                updated_records = []
                for i, record in enumerate(records):
                    if i >= len(n_clicks) or n_clicks[i] is None:  # Niet aangeklikt, behouden
                        updated_records.append(record)

                # Schrijf de bijgewerkte lijst terug naar het bestand
                with open(path, "w") as f:
                    for record in updated_records:
                        f.write(json.dumps(record) + "\n")

            # Zoekfunctionaliteit
            results = []
            with open(path, "r") as f:
                for line in f:
                    record = json.loads(line)
                    # Voeg alle records toe als er geen zoekterm is
                    if not search_term or search_term.lower() in record["title"].lower():
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
                        dcc.Graph(figure=rec['figure'], config={"displayModeBar": False}, style={"height": "320px", "marginTop": "10px"}),
                        html.Button(
                            "Verwijderen",
                            id={'type': 'delete-button', 'index': i},
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
                ]) for i, rec in enumerate(results)
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center"
            })

        except Exception as e:
            return html.Div(f"❌ Fout bij het verwerken: {e}", style={"color": "#CA005D", "margin": "30px"})

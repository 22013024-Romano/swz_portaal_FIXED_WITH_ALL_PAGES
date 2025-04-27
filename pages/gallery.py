from dash import html, dcc, Input, Output, State, ALL
import dash
import json
import os
from app_data import app_data  # Controleer de authenticatiestatus

def layout(app):
    return html.Div([
        html.H2("🖼️ Galerij"),
        dcc.Input(
            id="search-input",
            type="text",
            placeholder="🔍 Zoek op titel...",
            style={"marginBottom": "10px", "width": "50%"}
        ),
        html.Div(id="search-results", style={"marginTop": "20px"})
    ])

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
            # Lees de opgeslagen visualisaties
            path = "storage/saved_graphs.json"
            if not os.path.exists(path):
                return "⚠️ Geen opgeslagen visualisaties gevonden."

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
                return "⚠️ Geen resultaten gevonden."

            # Toon de resultaten
            return html.Ul([
                html.Li([
                    html.H4(rec['title']),
                    html.P(f"Beschrijving: {rec['description']}"),
                    html.Small(f"Gebruiker: {rec['user']} - Datum: {rec['timestamp']}"),
                    dcc.Graph(figure=rec['figure']),
                    # Verwijderknop alleen tonen als de gebruiker is ingelogd
                    html.Button(
                        "Verwijderen",
                        id={'type': 'delete-button', 'index': i},
                        style={"marginTop": "10px", "display": "block"} if app_data['is_authenticated'] else {"display": "none"}
                    )
                ]) for i, rec in enumerate(results)
            ])

        except Exception as e:
            return f"❌ Fout bij het verwerken: {e}"

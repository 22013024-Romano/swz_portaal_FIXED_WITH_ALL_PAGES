import os
import json
from dash import dcc, html, Input, Output
import plotly.graph_objs as go


def layout(app):
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "height": "100vh",
            "backgroundColor": "#f9f9f9",
            "fontFamily": "Arial, sans-serif",
        },
        children=[
        html.P(id="message")
    ])

def register_callbacks(app):
    @app.callback(
        Output("message", "children"),
        Input("url", "search"),
    )
    def display_graph(search):
        from urllib.parse import parse_qs

        query = parse_qs(search[1:] if search else "")
        graph_id = query.get("id", [None])[0]

        if graph_id is None:
            return f"geen grafiek gevonden met id {graph_id}"
        
        try:
            path = "storage/saved_graphs.json"
            if not os.path.exists(path):
                return html.Div("⚠️ Geen opgeslagen visualisaties gevonden.", style={"margin": "30px", "color": "#CA005D"})

            graph = None

            # Vind de juiste grafiek
            with open(path, "r") as f:
                records = [json.loads(line) for line in f]
                for record in records:
                    if record["id"] == graph_id:
                        graph = record
                        break

            if graph is None:
                return "Geen grafiek gevonden"

            return html.Div([
                        html.H4(graph['title']),
                        html.P(f"Beschrijving: {graph['description']}", style={"marginBottom": "8px"}),
                        html.Small(f"Gebruiker: {graph['user']} – Datum: {graph['timestamp']}", style={"color": "#888"}),
                        dcc.Graph(
                            figure=go.Figure(graph['figure']),
                            config={"displayModeBar": 'hover', "displaylogo": False},
                            style={"height": "640px", "marginTop": "10px"}
                        ),
                        html.Div(
                            [
                                html.Span(keyword, style={
                                    "padding": "8px 12px",
                                    "backgroundColor": "#CCE7F4", # Lichtblauw 45%.
                                    "borderRadius": "20px",
                                })
                                    for keyword in graph.get("keywords", [])],
                            style={
                                "display": "flex",
                                "gap": "5px",
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

        except Exception as e:
            return "Error bij het laden van de grafiek"

        return graph_id


import dash
from dash import dcc, html, Input, Output


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
        html.P(id="foo")
    ])

def register_callbacks(app):
    @app.callback(
        Output("foo", "children"),
        Input("url", "search"),
    )
    def display_graph(search):
        from urllib.parse import parse_qs

        query = parse_qs(search[1:] if search else "")
        graph_id = query.get("id", [None])[0]

        if graph_id is None:
            return f"geen grafiek gevonden met id {graph_id}"

        return graph_id


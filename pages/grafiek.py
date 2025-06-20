import dash
from dash import dcc, html, Input, Output


def layout(app):
    return html.Div([
        html.P(id="foo")
    ])

def register_callbacks(app):
    @app.callback(
        Output("foo", "children"),
        # Output("product-graph", "figure"),
        Input("url", "search"),
    )
    def display_graph(search):
        from urllib.parse import parse_qs

        query = parse_qs(search[1:] if search else "")
        graph_id = query.get("id", [None])[0]

        if graph_id is None:
            return f"geen grafiek gevonden met id {graph_id}"

        return graph_id


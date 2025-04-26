from dash import html, dcc, Input, Output
from pages import login, dashboard, gallery
from app_data import app_data
import dash

def create_layout(app):
    return html.Div(
        style={
            "backgroundColor": "white",  # Witte achtergrond
            "color": "black",  # Zwarte tekstkleur voor leesbaarheid
            "minHeight": "100vh",  # Zorg dat de achtergrond de volledige hoogte bedekt
            "fontFamily": "Arial, sans-serif",  # Professioneel lettertype
            "display": "flex",
            "flexDirection": "column"
        },
        children=[
            # Header
            html.Header(
                children=[
                    html.Div(
                        children=[
                            html.Img(
                                src="/assets/logo.png",  # Zorg dat je logo in de 'assets'-map staat
                                style={
                                    "height": "80px",  # Pas de hoogte van het logo aan
                                    "marginRight": "20px"
                                }
                            ),
                            html.H1(
                                "Data Visualisatie Portaal",
                                style={
                                    "display": "inline-block",
                                    "verticalAlign": "middle",
                                    "margin": "0",
                                    "fontSize": "28px",
                                    "color": "white"  # Witte tekst in de header
                                }
                            )
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "padding": "10px 20px",
                            "borderBottom": "2px solid white"
                        }
                    )
                ],
                style={"backgroundColor": "#CA005D"}  # Robijnrode header
            ),
            # Navigatiebalk
            html.Nav(
                children=[
                    dcc.Link("🏠 Galerij", href="/", style={"marginRight": "20px", "color": "#CA005D", "textDecoration": "none"}),
                    dcc.Link("📊 Dashboard", href="/dashboard", style={"marginRight": "20px", "color": "#CA005D", "textDecoration": "none"}),
                    dcc.Link(
                        "🔐 Login",
                        href="/login",
                        style={
                            "marginRight": "20px",
                            "color": "#CA005D",
                            "textDecoration": "none"
                        }
                    )
                ],
                style={
                    "textAlign": "center",
                    "padding": "10px 0",
                    "borderBottom": "1px solid #CA005D",
                    "fontSize": "18px"
                }
            ),
            # Pagina-inhoud
            html.Main(
                children=[
                    dcc.Location(id="url", refresh=False),
                    html.Div(id="page-content", style={"padding": "20px"})
                ],
                style={"flex": "1"}  # Zorg dat de inhoud de resterende ruimte vult
            ),
            # Footer
            html.Footer(
                children=[
                    html.P(
                        "© 2025 Data Visualisatie Portaal. Alle rechten voorbehouden.",
                        style={"margin": "0", "fontSize": "14px", "color": "white"}  # Witte tekst in de footer
                    )
                ],
                style={
                    "textAlign": "center",
                    "padding": "10px",
                    "backgroundColor": "#CA005D",  # Robijnrode footer
                    "borderTop": "2px solid white"
                }
            )
        ]
    )

def register_page_callbacks(app):
    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname')
    )
    def handle_navigation(pathname):
        # Toon de juiste pagina op basis van de URL
        if pathname == "/login":
            return login.layout(app)
        elif pathname == "/dashboard":
            if app_data.get("is_authenticated"):
                return dashboard.layout(app)
            return login.layout(app)
        # Standaard naar de galerijpagina
        return gallery.layout(app)
from dash import html, dcc, Input, Output
from pages import login, dashboard, gallery
from app_data import app_data
import dash

def create_layout(app):
    return html.Div(
        style={
            "backgroundColor": "white",
            "color": "black",
            "minHeight": "100vh",
            "fontFamily": "Arial, sans-serif",
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
                                src="/assets/logo.png",
                                style={
                                    "height": "80px",
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
                                    "color": "white"
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
                style={"backgroundColor": "#CA005D"}
            ),
            # Navigatiebalk
            html.Nav(
                children=[
                    html.Div(
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
                            ),
                        ],
                        style={"display": "inline-block"}
                    ),
                    html.Div(
                        children=[
                            html.Button(
                                "Uitloggen",
                                id="logout-button",
                                style={
                                    "backgroundColor": "#CA005D",
                                    "color": "white",
                                    "border": "none",
                                    "borderRadius": "5px",
                                    "padding": "5px 10px",
                                    "cursor": "pointer",
                                    "display": "none",  # Standaard verborgen
                                    "marginRight": "20px"  # Voeg ruimte toe aan de rechterkant
                                }
                            )
                        ],
                        style={"display": "inline-block", "float": "right"}
                    )
                ],
                style={
                    "textAlign": "center",
                    "padding": "10px 0",
                    "borderBottom": "1px solid #CA005D",
                    "fontSize": "18px",
                    "overflow": "hidden"
                }
            ),
            # Pagina-inhoud
            html.Main(
                children=[
                    dcc.Location(id="url", refresh=False),
                    html.Div(id="page-content", style={"padding": "20px"})
                ],
                style={"flex": "1"}
            ),
            # Footer
            html.Footer(
                children=[
                    html.P(
                        "© 2025 Data Visualisatie Portaal. Alle rechten voorbehouden.",
                        style={"margin": "0", "fontSize": "14px", "color": "white"}
                    )
                ],
                style={
                    "textAlign": "center",
                    "padding": "10px",
                    "backgroundColor": "#CA005D",
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

    @app.callback(
        Output('logout-button', 'style'),
        Input('url', 'pathname')
    )
    def update_logout_button(pathname):
        # Toon de uitlogknop alleen als de gebruiker is ingelogd
        if app_data.get('is_authenticated', False):
            return {
                "marginLeft": "20px",
                "backgroundColor": "#CA005D",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "padding": "5px 10px",
                "cursor": "pointer",
                "display": "block"  # Maak de knop zichtbaar
            }
        return {"display": "none"}  # Verberg de knop als de gebruiker niet is ingelogd
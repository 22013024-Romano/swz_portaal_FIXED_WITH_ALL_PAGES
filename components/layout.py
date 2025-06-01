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
            "fontFamily": "RijksoverheidSans, Arial, sans-serif",
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
                                id="login-link",
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
                                    "borderRadius": "6px",
                                    "padding": "8px 22px",
                                    "cursor": "pointer",
                                    "display": "none",  # Standaard verborgen
                                    "marginRight": "24px",
                                    "fontWeight": "bold",
                                    "fontSize": "16px",
                                    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
                                    "transition": "background 0.2s"
                                }
                            )
                        ],
                        style={"display": "inline-block", "float": "right", "verticalAlign": "middle"}
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
        elif pathname == "/dashboard2": # TODO: remove this when done.
            import pages
            return pages.dashboard2.layout(app)
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
                "marginRight": "10px",
                "backgroundColor": "#CA005D",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "padding": "5px 10px",
                "cursor": "pointer",
                "display": "block"  # Maak de knop zichtbaar
            }
        return {"display": "none"}  # Verberg de knop als de gebruiker niet is ingelogd

    @app.callback(
        Output('login-button', 'disabled'),
        Input('url', 'pathname')
    )
    def disable_login_button(pathname):
        # Deactiveer de login-knop als de gebruiker al is ingelogd
        if app_data.get('is_authenticated', False):
            return True
        return False

    @app.callback(
        Output('login-link', 'style'),
        Input('url', 'pathname')
    )
    def hide_login_link(pathname):
        # Verberg de login-link als de gebruiker is ingelogd
        if app_data.get('is_authenticated', False):
            return {"display": "none"}
        return {
            "marginRight": "20px",
            "color": "#CA005D",
            "textDecoration": "none",
            "display": "inline-block"
        }
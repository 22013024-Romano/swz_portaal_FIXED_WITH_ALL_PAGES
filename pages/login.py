from dash import html, dcc, Input, Output, State
import json
from app_data import app_data

def layout(app):
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "height": "100vh",
            "backgroundColor": "#f9f9f9",
            "fontFamily": "Arial, sans-serif"
        },
        children=[
            html.Div(
                style={
                    "width": "100%",
                    "maxWidth": "400px",
                    "padding": "20px",
                    "borderRadius": "8px",
                    "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "backgroundColor": "white"
                },
                children=[
                    html.H2(
                        "🔐 Inloggen",
                        style={
                            "textAlign": "center",
                            "marginBottom": "20px",
                            "color": "#CA005D"
                        }
                    ),
                    html.Label(
                        "E-mailadres:",
                        style={
                            "display": "block",
                            "marginBottom": "5px",
                            "fontWeight": "bold",
                            "color": "#333"
                        }
                    ),
                    dcc.Input(
                        id="email",
                        type="email",
                        placeholder="Voer je e-mailadres in",
                        style={
                            "width": "100%",  # Zorgt ervoor dat het veld even breed is als de container
                            "padding": "10px",
                            "marginBottom": "15px",
                            "border": "1px solid #ccc",
                            "borderRadius": "5px",
                            "fontSize": "16px",
                            "boxSizing": "border-box"  # Houdt rekening met padding en border
                        }
                    ),
                    html.Label(
                        "Wachtwoord:",
                        style={
                            "display": "block",
                            "marginBottom": "5px",
                            "fontWeight": "bold",
                            "color": "#333"
                        }
                    ),
                    dcc.Input(
                        id="password",
                        type="password",
                        placeholder="Voer je wachtwoord in",
                        style={
                            "width": "100%",  # Zorgt ervoor dat het veld even breed is als de container
                            "padding": "10px",
                            "marginBottom": "20px",
                            "border": "1px solid #ccc",
                            "borderRadius": "5px",
                            "fontSize": "16px",
                            "boxSizing": "border-box"  # Houdt rekening met padding en border
                        }
                    ),
                    html.Button(
                        "Login",
                        id="login-button",
                        style={
                            "width": "100%",  # Zorgt ervoor dat de knop even breed is als de container
                            "padding": "10px",
                            "backgroundColor": "#CA005D",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "5px",
                            "fontSize": "16px",
                            "cursor": "pointer"
                        }
                    ),
                    dcc.Location(id="url-login", refresh=True),
                    html.Div(
                        id="login-status",
                        style={
                            "marginTop": "15px",
                            "textAlign": "center",
                            "color": "green",
                            "fontSize": "14px"
                        }
                    )
                ]
            )
        ]
    )

def register_callbacks(app):
    @app.callback(
        Output('url-login', 'pathname'),
        Output('login-status', 'children'),
        Input('login-button', 'n_clicks'),
        State('email', 'value'),
        State('password', 'value')
    )
    def login_user(n, email, pw):
        if n and email and pw:
            try:
                with open("users.json", "r") as f:
                    users = json.load(f).get("users", [])
                for user in users:
                    if user["email"] == email and user["password"] == pw:
                        app_data['is_authenticated'] = True
                        app_data['current_user'] = email
                        return "/dashboard", f"Ingelogd als {email}"
                return None, html.Span("Verkeerde gebruikersnaam of wachtwoord.", style={"color": "#ED0707"})
            except Exception as e:
                return None, html.Span(f"Fout: {e}", style={"color": "#ED0707"})
        return None, ""

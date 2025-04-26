from dash import html, dcc, Input, Output, State
import json
from app_data import app_data

def layout(app):
    return html.Div([
        html.H2("🔐 Inloggen"),
        html.Label("E-mailadres:"),
        dcc.Input(id="email", type="email"),
        html.Label("Wachtwoord:"),
        dcc.Input(id="password", type="password"),
        html.Button("Login", id="login-button"),
        dcc.Location(id="url-login", refresh=True),
        html.Div(id="login-status", style={"color": "green", "marginTop": 10})
    ])

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
                        return "/dashboard", f"✅ Ingelogd als {email}"
                return None, "❌ Verkeerde gebruikersnaam of wachtwoord."
            except Exception as e:
                return None, f"❌ Fout: {e}"
        return None, "❌ Vul je gegevens in."

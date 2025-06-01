import os
from flask import Flask
from dash import Dash, no_update
from components.layout import create_layout, register_page_callbacks
from dash.dependencies import Output, Input
from pages.login import register_callbacks as register_login_callbacks
from pages.dashboard import register_callbacks as register_dashboard_callbacks
from pages.dashboard2 import register_callbacks as register_dashboard_callbacks2
from pages.gallery import register_callbacks as register_gallery_callbacks
from app_data import app_data


server = Flask(__name__)
app = Dash(__name__, server=server, suppress_callback_exceptions=True)
app.title = "Data Visualisatie Portaal"
app.layout = create_layout(app)

# Registreer de callbacks
register_page_callbacks(app)
register_login_callbacks(app)
# register_dashboard_callbacks(app) # TODO: uncomment this.
register_dashboard_callbacks2(app)
register_gallery_callbacks(app)

@app.callback(
    Output('url', 'pathname'),
    Input('logout-button', 'n_clicks')
)
def logout_user(n_clicks):
    if n_clicks:
        app_data['is_authenticated'] = False
        app_data['current_user'] = None
        return "/login"  # Stuur de gebruiker naar de loginpagina
    return no_update

if __name__ == "__main__":
    os.makedirs("storage", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    if not os.path.exists("storage/saved_graphs.json"):
        with open("storage/saved_graphs.json", "w") as f:
            f.write("")
    app.run(debug=True)

import os
from flask import Flask
from dash import Dash
from components.layout import create_layout, register_page_callbacks
from pages.login import register_callbacks as register_login_callbacks
from pages.dashboard import register_callbacks as register_dashboard_callbacks
from pages.gallery import register_callbacks as register_gallery_callbacks

server = Flask(__name__)
app = Dash(__name__, server=server, suppress_callback_exceptions=True)
app.title = "Data Visualisatie Portaal"
app.layout = create_layout(app)

# Registreer de callbacks
register_page_callbacks(app)
register_login_callbacks(app)
register_dashboard_callbacks(app)
register_gallery_callbacks(app)

if __name__ == "__main__":
    os.makedirs("storage", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    if not os.path.exists("storage/saved_graphs.json"):
        with open("storage/saved_graphs.json", "w") as f:
            f.write("")
    app.run(debug=True)

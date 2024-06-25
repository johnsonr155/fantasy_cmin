# stdlib
import logging
import os

# third party
import dash
import dash_bootstrap_components as dbc
from ten_ds_utils.config.dash import DashConfig
import dotenv

from ten_ds_utils.dash.layout import Layout

dotenv.load_dotenv()
# enable logging
logging.basicConfig(level=logging.INFO)

# include external css and js
# TODO: review
external_js = [
    "https://code.jquery.com/jquery-3.4.1.slim.min.js",
    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
]
lato_font = "https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900"

conf = DashConfig()

prefix_url = os.environ.get("PREFIX_URL", "/")

app = dash.Dash(
    __name__,
    external_scripts=external_js,
    external_stylesheets=[
        dbc.themes.LUX,
        lato_font
    ],
    url_base_pathname=prefix_url,
)

layout = Layout(app)

server = app.server
app.config.suppress_callback_exceptions = True

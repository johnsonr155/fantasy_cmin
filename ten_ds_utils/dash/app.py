import os
import dash_bootstrap_components as dbc
from dash import Dash


EXTERNAL_JS = [
    "https://code.jquery.com/jquery-3.4.1.slim.min.js",
    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
]


def create_app():
    return Dash(
        __name__,
        external_scripts=EXTERNAL_JS,
        external_stylesheets=[dbc.themes.LUX],
        url_base_pathname=os.environ.get("PREFIX_URL", "/"),
    )

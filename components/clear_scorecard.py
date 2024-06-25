import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc, html, Input, Output, State, callback_context

from app import app
from layouts.functions.prep_data import (
    json_to_s3,
    write_file,
    get_saved_scorecards_metadata,
)


def clear_scorecard_button():
    return html.Div(
        [dmc.Button("Clear", color="blue", compact=True, id="clear-scorecard-button")]
    )

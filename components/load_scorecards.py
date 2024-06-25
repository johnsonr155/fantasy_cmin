import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import dcc, html, Input, Output, State, callback_context

from app import app
from layouts.functions.prep_data import (
    json_to_s3,
    write_file,
    get_saved_scorecards_metadata,
)


def load_scorecard_modal():
    return html.Div(
        [
            dmc.Modal(
                title="Load a previously saved options",
                id="load-scorecard-modal",
                size="xl",
                children=[
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="load-scorecard-select",
                                searchable=True,
                                placeholder="Select a saved file",
                                optionHeight=65,
                                maxHeight=550,
                                style={
                                    "height": "75px",
                                },
                            ),
                            dmc.Button("Load", id="load-scorecard-button-submit"),
                        ],
                        style={
                            "display": "flex",
                            "flex-direction": "column",
                            "gap": "0.5rem",
                        },
                    ),
                ],
            ),
            dmc.Button(
                "Load",
                color="pink",
                compact=True,
                id="load-scorecard-button-open-modal",
            ),
        ]
    )


def load_scorecard_dropdown_options(name, description, date, user):

    return html.Div(
        [
            dmc.Text(name, weight=700, style={"line-height": "1em"}),
            dmc.Text(description, size="sm", style={"line-height": "1em"}),
            dmc.Text(
                f"Saved at: {date} by {user}",
                size="xs",
                style={"line-height": "1em", "color": "#a6a6a6"},
            ),
        ],
        style={
            "display": "flex",
            "flex-direction": "column",
            "width": "100%",
            "padding-top": "0.25rem",
            "padding-bottom": "0.25rem",
            "padding-right": "2rem",
            "gap": "0.375rem",
        },
    )


# load button
@app.callback(
    Output("load-scorecard-modal", "opened"),
    Input("load-scorecard-button-open-modal", "n_clicks"),
    Input("load-scorecard-button-submit", "n_clicks"),
    State("load-scorecard-modal", "opened"),
    State("load-scorecard-select", "value"),
    prevent_initial_call=True,
)
def update_load_government_modal(open_clicks, submit_clicks, opened, save_name):
    prop_id = callback_context.triggered[0]["prop_id"]

    # if submitted on empty return error message and dont close
    if ("submit" in prop_id) and (not save_name):
        return True

    return not opened


# populating saved government dropdowns in load gov and compare gov features
@app.callback(
    Output("load-scorecard-select", "options"),
    Output("load-scorecard-select", "value"),
    Output("load-existing-saves-scorecard-select", "options"),
    Output("load-existing-saves-scorecard-select", "value"),
    Input("load-scorecard-button-open-modal", "n_clicks"),
    Input("save-scorecard-button-open-modal", "n_clicks"),
)
def update_select_data(load_button, save_button):
    # find latest baseline gov based on storage
    # which is already sorted by gov date
    saved_score_cards_metadata = get_saved_scorecards_metadata()
    if len(saved_score_cards_metadata) == 0:
        return [], None, [], None

    latest_scorecard = saved_score_cards_metadata[0]

    load_scorecard_options = [
        dict(
            value=metadata_dict["filename"],
            label=load_scorecard_dropdown_options(
                name=metadata_dict["name"],
                description=metadata_dict.get("description", ""),
                date=metadata_dict.get("date", ""),
                user=metadata_dict.get("user", ""),
            ),
        )
        for metadata_dict in saved_score_cards_metadata
    ]

    return (
        load_scorecard_options,
        latest_scorecard["filename"],
        load_scorecard_options,
        None,
    )

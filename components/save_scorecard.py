import re
import os
from datetime import datetime as dt
from app import conf

import pandas as pd
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import dash
from dash import dcc, html, Input, Output, State, callback_context

from app import app

from layouts.functions.utils import get_username
from layouts.functions.prep_data import (
    json_to_s3,
    json_from_s3,
    write_file,
    move_metadata_to_archive,
)


def save_scorecard_form():
    return html.Div(
        [
            dmc.Modal(
                title="Save Policy Configuration",
                id="save-scorecard-modal",
                size="xl",
                children=[
                    dmc.SegmentedControl(
                        id="save-segmented",
                        color="pink",
                        value="new",
                        data=[
                            {"value": "new", "label": "New save"},
                            {"value": "existing", "label": "Save as existing"},
                        ],
                        mt=10,
                    ),
                    html.Div(
                        id="save-new-div",
                        children=[
                            dmc.Text(
                                "Fill out the form below and hit 'Save' to save the current policy options"
                            ),
                            html.Div(
                                [
                                    dmc.TextInput(
                                        placeholder="Policy name",
                                        id="save-scorecard-text-input",
                                        description="Policy Name",
                                    ),
                                ],
                                style={
                                    "width": "35vw",
                                    "max-width": "400px",
                                },
                            ),
                            dmc.Textarea(
                                placeholder="Description of the policy configuration",
                                id="save-scorecard-description-input",
                                description="Description",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flex-direction": "column",
                            "gap": "0.5rem",
                            "margin": "0rem 1rem",
                        },
                    ),
                    html.Div(
                        id="save-existing-div",
                        children=[
                            dmc.Text("Overwrite an existing save or delete one by saving a blank policy configuration", style={"font-style": "italic"}),
                            dmc.Text(
                                "* Select an existing save to overwrite it",
                                color="red",
                                size="xs",
                                id="load-existing-saves-scorecard-error",
                                style={"display": "none"},
                            ),
                            dmc.Alert(
                                id="delete-save-warning",
                                title="Warning!",
                                color="red",
                                children="You have not selected any policies. Saving on top of this file will delete it!",
                                style={"display": "none"},
                            ),
                            dcc.Dropdown(
                                id="load-existing-saves-scorecard-select",
                                searchable=True,
                                placeholder="Select a saved file",
                                optionHeight=65,
                                maxHeight=550,
                                style={
                                    "height": "75px",
                                },
                            ),
                        ],
                        style={"margin": "0rem 1rem"},
                    ),
                    dmc.Button("Save", id="save-scorecard-button-submit"),
                ],
            ),
            dmc.Button(
                "Save",
                compact=True,
                id="save-scorecard-button-open-modal",
                color="green",
            ),
        ]
    )

@app.callback(
    Output("delete-save-warning", "style"),
    Input("save-scorecard-button-open-modal", "n_clicks"),
    Input("load-existing-saves-scorecard-select", "value"),
    State("save-scorecard-store", "data"),
)
def update_delete_save_warning(open_model, value, scorecard_data):
    if value and not bool(scorecard_data):
        return {"display": "flex"}
    else:
        return {"display": "none"}

@app.callback(
    Output("save-existing-div", "style"),
    Output("save-new-div", "style"),
    Input("save-segmented", "value"),
)
def update_segmented(value):
    show = {
        "display": "flex",
        "flex-direction": "column",
        "gap": "0.5rem",
        "margin": "1rem 0",
    }
    if value == "new":
        return {"display": "none"}, show
    else:
        return show, {"display": "none"}


# save button
@app.callback(
    Output("save-scorecard-modal", "opened"),
    Output("save-scorecard-text-input", "value"),
    Output("save-scorecard-description-input", "value"),
    Output("save-scorecard-text-input", "error"),
    Output("save-scorecard-description-input", "error"),
    Output("load-existing-saves-scorecard-error", "style"),
    Input("save-scorecard-button-open-modal", "n_clicks"),
    Input("save-scorecard-button-submit", "n_clicks"),
    State("save-segmented", "value"),
    State("save-scorecard-modal", "opened"),
    State("save-scorecard-text-input", "value"),
    State("save-scorecard-description-input", "value"),
    State("save-scorecard-store", "data"),
    State("load-existing-saves-scorecard-select", "value"),
    State("10ds-url", "href"),
    prevent_initial_call=True,
)
def update_save_scorecard_modal(
    open_clicks,
    submit_clicks,
    save_segmented,
    opened,
    save_name,
    save_description,
    scorecard_data,
    existing_save,
    href,
):
    prop_id = callback_context.triggered[0]["prop_id"]

    # if submitted on empty save name or description return error message and dont close
    if ("submit" in prop_id) and (not save_name or not save_description) and (save_segmented == "new"):
        description_error = (
            "Please enter a valid description" if not save_description else ""
        )
        name_error = "Please enter a valid save name" if not save_name else ""
        return (
            True,
            save_name,
            save_description,
            name_error,
            description_error,
            {"display": "none"},
        )

    # They've tried to overwrite an existing save but not selected one
    if ("submit" in prop_id) and (existing_save == None) and (save_segmented == "existing"):
        return (
            True,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            dash.no_update,
            {},
        )

    # brand new save 
    elif ("submit" in prop_id) and save_name and save_description and (save_segmented == "new"):
        timestamp_file = dt.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = save_name.replace(" ", "").lower()
        sanitised_filename = (
            re.sub("[^a-zA-Z0-9 \n\.]", "", filename) + f"_{timestamp_file}"
        )
        metadata = {
            "name": save_name,
            "filename": sanitised_filename,
            "description": save_description,
            "date": dt.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": get_username(href),
        }

        scorecard_df = pd.DataFrame(scorecard_data)

        write_file(
            scorecard_df,
            file_name=f"saved_scorecards/{sanitised_filename}.csv",
        )
        json_to_s3(
            metadata,
            file_name=f"saved_scorecards/metadata/{sanitised_filename}.json",
        )

    # overwrite existing save
    elif ("submit" in prop_id) and (existing_save != None) and (save_segmented == "existing"):
        metadata_path = f"saved_scorecards/metadata/{existing_save}.json"
        existing_metadata = json_from_s3(metadata_path)
        existing_metadata["date"] = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_metadata["user"] = get_username(href)

        scorecard_df = pd.DataFrame(scorecard_data)

        if scorecard_df.empty:
            archived_path = f"saved_scorecards/archived_metadata/{existing_save}.json"
            move_metadata_to_archive(metadata_path, archived_path)
        
        else:
            write_file(
                scorecard_df,
                file_name=f"saved_scorecards/{existing_save}.csv",
            )
            json_to_s3(
                existing_metadata,
                file_name=f"saved_scorecards/metadata/{existing_save}.json",
            )

    return not opened, "", "", "", "", {"display": "none"}

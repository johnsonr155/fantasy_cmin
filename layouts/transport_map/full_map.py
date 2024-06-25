import re
import json
import logging
from copy import copy
import dash_deck
from dash.exceptions import PreventUpdate
import dash
from dash import html, dcc, Input, Output, State
import dash_mantine_components as dmc
import pydeck as pdk
import pandas as pd

from app import app, layout
from layouts.transport_map.constants import (
    line_layer_dict,
    funding_pots_col_dict,
    mapbox_api_token,
    map_style,
)
from layouts.functions.maps import la_pdk_layer, build_cumulative_policy_geojson


def toggle_section(title, children):
    return html.Div(
        [
            html.Div(
                [
                    dmc.Title(title, order=5),
                    dmc.Divider(),
                ]
            ),
        ]
        + children,
        style={"display": "flex", "flex-direction": "column", "gap": "5px"},
    )


checkbox_ids = [x for x in line_layer_dict]

layout.add_full_page(
    path=["transport-map"],
    title="",
    children=[
        html.Div(
            [
                dmc.Card(
                    withBorder=True,
                    shadow="sm",
                    radius="md",
                    children=[
                        html.Div(
                            [
                                dmc.Title("Map Layers", order=3),
                                dcc.Store(
                                    id="transport-policies-store",
                                    storage_type="session",
                                ),
                                dmc.Button(
                                    "Select All",
                                    color="blue",
                                    compact=True,
                                    id="select-all-policies-button",
                                ),
                                dmc.Button(
                                    "Clear",
                                    color="pink",
                                    compact=True,
                                    id="clear-all-policies-button",
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "0.5rem",
                                "align-items": "center",
                            },
                        ),
                        html.Div(
                            [
                                toggle_section(
                                    "Base Map",
                                    children=[
                                        dmc.Checkbox(
                                            size="sm",
                                            id="modern-railways-checkbox",
                                            label="Modern Railways",
                                            checked=True,
                                            color="red",
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="hs2-checkbox",
                                            label="HS2",
                                            color="blue",
                                        ),
                                    ],
                                ),
                                toggle_section(
                                    "Rail Options",
                                    children=[
                                        dmc.Text(
                                            "* High speed sections in black", size="sm"
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="rump-hs2-checkbox",
                                            label="Full HS2",
                                            color="teal",
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="west-yorkshire-checkbox",
                                            label="West Yorkshire Mass Transit",
                                            color="pink",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="midlands-rail-hub-checkbox",
                                            label="Midlands Rail Hub",
                                            color="grape",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="beeching-checkbox",
                                            label="Beeching Reversal",
                                            color="gray",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="north-wales-electrification-checkbox",
                                            label="North Wales Electrification",
                                            color="cyan",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="ely-junction-checkbox",
                                            label="Ely Junction Freight Route",
                                            color="lime",
                                            checked=True,
                                        ),
                                    ],
                                ),
                                toggle_section(
                                    "Further Intercity Options",
                                    children=[
                                        dmc.Checkbox(
                                            size="sm",
                                            id="intercity-leeds-shefield-checkbox",
                                            label="Leeds-Sheffield",
                                            color="cyan",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="intercity-shefield-hull-checkbox",
                                            label="Sheffield-Hull",
                                            color="cyan",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="intercity-leeds-hull-checkbox",
                                            label="Leeds-Hull",
                                            color="cyan",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="intercity-manchester-shefield-checkbox",
                                            label="Manchester-Sheffield",
                                            color="cyan",
                                            checked=True,
                                        ),
                                    ],
                                ),
                                toggle_section(
                                    "Station Options",
                                    children=[
                                        dmc.Checkbox(
                                            size="sm",
                                            id="new-station-checkbox",
                                            label="New Stations",
                                            color="blue",
                                            radius="xl",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="upgrade-station-checkbox",
                                            label="Station Upgrades",
                                            color="red",
                                            radius="xl",
                                            checked=True,
                                        ),
                                    ],
                                ),
                                toggle_section(
                                    "Road Options",
                                    children=[
                                        dmc.Text(
                                            "* Roads = central white stripe", size="sm"
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="a50-a500-corridor-checkbox",
                                            label="A50 to A500 corridor",
                                            color="orange",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="a1-to-a19-corridor-checkbox",
                                            label="A1 to A19 link road",
                                            color="yellow",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="a5-corridor-checkbox",
                                            label="A5 Corridor East Midlands",
                                            color="green",
                                            checked=True,
                                        ),
                                        dmc.Checkbox(
                                            size="sm",
                                            id="gretna-checkbox",
                                            label="A75 Gretna to Stranraer",
                                            color="blue",
                                            checked=True,
                                        ),
                                    ],
                                ),
                            ],
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "flex-direction": "column",
                                "max-height": "80vh",
                                "overflow-y": "scroll",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "10px",
                        "flex-direction": "column",
                    },
                ),
                html.Div(
                    id="full-rail-deckgl-map",
                ),
            ],
            style={"display": "flex", "gap": "20px"},
        )
    ],
)


@app.callback(
    Output("full-rail-deckgl-map", "children"),
    Output("transport-policies-store", "data"),
    [Input(policy_id, "checked") for policy_id in checkbox_ids],
    [State(policy_id, "id") for policy_id in checkbox_ids],
)
def update_map(*args):
    layers = []
    funding_pots_cols = []

    arg_length = int(len(args) / 2)
    checked_args = args[:arg_length]
    id_args = args[arg_length:]

    for i, checkbox_id in enumerate(checkbox_ids):
        checkbox_index = id_args.index(checkbox_id)
        checkbox = checked_args[checkbox_index]
        if checkbox:

            # pots is slightly different where we want to add the column name
            # this is then used lower down to build the choropleth layer
            if "pot" in checkbox_id:
                funding_pots_cols.append(funding_pots_col_dict[checkbox_id])

            else:
                layers.extend(line_layer_dict[checkbox_id])

    if bool(funding_pots_cols):
        choropleth_layers = build_cumulative_policy_geojson(funding_pots_cols)
        funding_pots_pdk_layer = la_pdk_layer(choropleth_layers)
        layers = [funding_pots_pdk_layer] + layers

    r = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(latitude=53.2, longitude=-2, zoom=7),
        map_style="light",
    ).to_json()

    

    return (
        dash_deck.DeckGL(r, mapboxKey=mapbox_api_token, style=map_style),
        checked_args,
    )


@app.callback(
    [Output(policy_id, "checked") for policy_id in checkbox_ids],
    Input("select-all-policies-button", "n_clicks"),
    Input("clear-all-policies-button", "n_clicks"),
    Input("10ds-url", "href"),
    [State("transport-policies-store", "data")]
    + [State(policy_id, "checked") for policy_id in checkbox_ids],
)
def select_all_policies(select, clear, url, data, *args):
    prop_id = dash.callback_context.triggered[0]["prop_id"]
    
    if "." == prop_id:
        if data:
            return data

        else:
            return [True, True] + [False for x in args[2:]]

    elif "select-all-policies-button" in prop_id:
        return [True for x in args]

    elif "clear-all-policies-button" in prop_id:
        return [True, True] + [False for x in args[2:]]

    else:
        return [x for x in args]

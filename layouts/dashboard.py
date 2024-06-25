import logging
import random
import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import ALL, Input, Output, State, dcc, html
from plotly import graph_objects as go

from app import app, layout
from components.clear_scorecard import clear_scorecard_button
from components.load_scorecards import load_scorecard_modal
from components.policy_options import policy_categories
from components.save_scorecard import save_scorecard_form
from components.spend_type_div import spend_type_div
from layouts.functions.utils import lens_1_categories, lens_2_categories

from layouts.functions.prep_data import import_data, calculate_percentage_costs
from layouts.functions.utils import get_username
from layouts.functions.graph import get_treemap

df = import_data("policy_costs_scalable.csv")
df["cost"] = df["medium"]
df["id"] = df["policy_options"].str.lower().str.replace(" ", "-")
df["flag"] = df["flag"].str.strip(" ")


left_panel = [
    html.Div(
        [
            dcc.Store(id="save-scorecard-store", storage_type="session", data=[]),
            dmc.TextInput(
                placeholder="Search...",
                style={"width": 250},
                id="search-input",
                size="xs",
            ),
            dmc.SegmentedControl(
                id="policy-lens",
                value="lens_1",
                size="xs",
                color="pink",
                data=[
                    {"value": "lens_1", "label": "Domain Lens"},
                    {"value": "lens_2", "label": "Capability Lens"},
                ],
            ),
            save_scorecard_form(),
            load_scorecard_modal(),
            clear_scorecard_button(),
        ],
        style={"display": "flex", "gap": "0.5rem", "align-items": "center"},
    ),
    html.Div(
        id="policy-options-container",
        style={"display": "flex", "flex-direction": "column"},
    ),
]

layout.add_half_page(
    path="policy-builder",
    title="",
    left_panel=left_panel,
    right_panel=[
        html.Div(
            [
                html.Div(
                    [
                        dmc.Text(
                            "Total package cost:",
                            weight=450,
                            style={"font-size": "20px"},
                        ),
                        dmc.Text(
                            "-",
                            id="total-package-cost",
                            weight=750,
                            style={"font-size": "30px", "color": "#c80678"},
                        ),
                    ],
                    style={"display": "flex", "gap": "1rem", "align-items": "center"},
                ),
                html.Div(
                    id="package-split", style={"display": "flex", "flex-wrap": "wrap"}
                ),
                dmc.Divider(),
                dmc.Modal(
                    id="modal-graph",
                    size="85%",
                    zIndex=10000,
                    children=[
                        dcc.Graph(id="fullscreen-graph", style={"height": "75vh"})
                    ],
                ),
                dcc.Graph(id="budget-graph", style={"height": "70vh", "width": "100%"}),
                dmc.Button(
                    "Full screen",
                    compact=True,
                    id="fullscreen-button",
                    style={"margin-left": "15px"},
                ),
            ],
            style={
                "position": "fixed",
                "top": "70px",
                "width": f"50%",
            },
        )
    ],
)


def get_policies_on(policy_options_checked, policy_ids, scalable_options):
    total_policies = df.copy()
    total_policies = total_policies.drop(columns=["on_off"])

    policy_dicts = []
    for i, policy_id in enumerate(policy_ids):
        policy_row_dict = {
            "id": policy_ids[i]["index"],
            "on_off": policy_options_checked[i],
            "option": scalable_options[i] if scalable_options[i] != None else "medium",
        }
        policy_dicts.append(policy_row_dict)

    policy_df = pd.DataFrame(policy_dicts)
    policies_on_df = policy_df[policy_df["on_off"] == True]

    if policies_on_df.empty:
        return go.Figure()

    policies_on_w_costs = policies_on_df.merge(total_policies, on="id", how="left")

    return policies_on_w_costs


# CALLBACKS
@app.callback(
    Output("budget-graph", "figure"),
    Output("fullscreen-graph", "figure"),
    Output("save-scorecard-store", "data"),
    Output("total-package-cost", "children"),
    Output("package-split", "children"),
    Input({"type": "policy-option", "index": ALL}, "checked"),
    Input({"type": "policy-option", "index": ALL}, "id"),
    Input({"type": "cost-dropdown", "index": ALL}, "value"),
    State("policy-lens", "value"),
    State("10ds-url", "href"),
    prevent_initial_call=True,
)
def update_figure(
    policy_options_checked, policy_ids, scalable_options, policy_lens, href
):
    if True in policy_options_checked:
        logging.warning(f"Policies being selected by {get_username(href)}")
        policies_on_w_costs = get_policies_on(
            policy_options_checked, policy_ids, scalable_options
        )

        # This createst the cost column
        # If it is scalable, option could be (v. low, low, medium, high)
        # If not scalable, option will be medium by default
        # It takes the option and then creates the "cost" column with the correct number
        policies_on_w_costs["cost"] = policies_on_w_costs.apply(
            lambda row: row[row["option"]], axis=1
        )
        total_cost = round(policies_on_w_costs["cost"].sum(), 1)
        policies_on_w_costs["type"] = f"Total (€{total_cost}mn)"

        policies_to_plot_df = policies_on_w_costs.copy()
        fig = get_treemap(policies_to_plot_df)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=20))

        # Breaks down the policy options by the lens category
        lens_categories = (
            lens_1_categories if policy_lens == "lens_1" else lens_2_categories
        )
        percentage_costs = calculate_percentage_costs(policies_to_plot_df, policy_lens)
        category_outputs = [
            spend_type_div(category, percentage_costs.get(category, {"%": 0, "€": 0}))
            for category in lens_categories
        ]

        return (
            fig,
            fig,  # full-screen graph
            policies_on_w_costs.to_dict("records"),  # to the datastore
            f"€{total_cost}mn",
            category_outputs,
        )

    else:
        return go.Figure(), go.Figure(), [], "-", []


@app.callback(
    Output("policy-options-container", "children"),
    Input("load-scorecard-button-submit", "n_clicks"),
    Input("10ds-url", "pathname"),
    Input("clear-scorecard-button", "n_clicks"),
    Input("policy-lens", "value"),
    State("save-scorecard-store", "data"),
    State("load-scorecard-select", "value"),
)
def loading_saving_and_inprogress_packages(
    submit, pathname, clear_scorecard, policy_lens, saved_data, selected_values
):
    total_policies = df.copy()

    prop_id = dash.callback_context.triggered[0]["prop_id"]
    lens_categories = (
        lens_1_categories if policy_lens == "lens_1" else lens_2_categories
    )

    logging.info(prop_id)
    # resurrecting an old save
    if "load-scorecard-button-submit" in prop_id:
        saved_policies = import_data(f"saved_scorecards/{selected_values}.csv")
        df_categories = df.copy()[["id", policy_lens]]
        saved_policies = saved_policies.merge(df_categories, on="id", how="left")

        total_policies = total_policies.drop(columns=["on_off"])
        policies_to_load = total_policies.merge(
            saved_policies[["id", "on_off", "option"]], on="id", how="left"
        )
        policies_to_load["option"] = policies_to_load["option"].fillna("medium")

        return [
            policy_categories(
                category,
                policies_to_load[policies_to_load[policy_lens] == category],
            )
            for category in lens_categories
        ]

    # if policy checklist is being cleared or nothing is stored
    elif ("clear-scorecard-button" in prop_id) | (not bool(saved_data)):
        total_policies["on_off"] = total_policies["default"]
        total_policies["option"] = "medium"

        return [
            policy_categories(
                category,
                total_policies[total_policies[policy_lens] == category],
            )
            for category in lens_categories
        ]

    # If the page is refreshed then this loads the session stored data
    elif bool(saved_data):
        df_options = pd.DataFrame(saved_data)
        total_policies = total_policies.drop(columns=["on_off"])
        policies_to_load = total_policies.merge(
            df_options[["id", "on_off", "option"]], on="id", how="left"
        )
        policies_to_load["option"] = policies_to_load["option"].fillna("medium")
        return [
            policy_categories(
                category,
                policies_to_load[policies_to_load[policy_lens] == category],
            )
            for category in lens_categories
        ]


@app.callback(
    Output("modal-graph", "opened"),
    Input("fullscreen-button", "n_clicks"),
    State("modal-graph", "opened"),
    prevent_initial_call=True,
)
def open_fullscreen_graph(n_clicks, opened):
    return not opened


@app.callback(
    [Output({"type": "policy-option-div", "index": ALL}, "style")],
    Input("search-input", "value"),
    State({"type": "policy-option-div", "index": ALL}, "id"),
)
def search_filter_policies(search, ids):
    search = search.lower().replace(" ", "-")
    DEFAULT_STYLE = {}

    if (search == "") | (search == None):
        styles = [DEFAULT_STYLE for x in ids]

    else:
        styles = []
        for policy in ids:
            if search in policy["index"]:
                styles.append(DEFAULT_STYLE)
            else:
                styles.append({"display": "none"})

    return [styles]

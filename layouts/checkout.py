import logging
import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import dash_table
from dash import ALL, Input, Output, State, dcc, html
from plotly import graph_objects as go

from app import app, layout
from components.clear_scorecard import clear_scorecard_button
from components.load_scorecards import load_scorecard_dropdown_options
from components.policy_options import policy_categories
from components.save_scorecard import save_scorecard_form
from components.table import create_dashboard_detail_table
from components.spend_type_div import spend_type_div

from layouts.functions.prep_data import import_data, calculate_percentage_costs
from layouts.functions.utils import get_username
from layouts.functions.prep_data import (
    json_from_s3,
    write_file,
    get_saved_scorecards_metadata,
)
from layouts.functions.graph import get_treemap
from layouts.functions.utils import lens_1_categories, lens_2_categories

full_df = import_data("policy_costs_scalable.csv")
full_df["cost"] = full_df["medium"]
full_df["id"] = full_df["policy_options"].str.lower().str.replace(" ", "-")
full_df["flag"] = full_df["flag"].str.strip(" ")


layout.add_full_page(
    path="policy-checkout",
    title="",
    children=[
        html.Div(
            [
                dmc.Text("View total package as:", size="sm", weight=500, mb=0),
                dmc.SegmentedControl(
                    id="full-package-segmented",
                    value="placemat",
                    color="pink",
                    data=[
                        {"value": "placemat", "label": "Placemat"},
                        {"value": "table", "label": "Table"},
                    ],
                    mt=10,
                ),
                dcc.Dropdown(
                    id="policy-checkout-select",
                    searchable=True,
                    multi=True,
                    placeholder="Select already saved packages...",
                    optionHeight=65,
                    maxHeight=550,
                    style={
                        "max-height": "150px",
                    },
                ),
            ],
            style={
                "display": "flex",
                "flex-direction": "column",
                "gap": "0.5rem",
            },
        ),
        dmc.RadioGroup(
            [
                dmc.Radio(l, value=k)
                for k, l in [
                    ["domain", "Domain"],
                    ["capability", "Capability"],
                    ["package", "Region"],
                ]
            ],
            id="radiogroup-placemat",
            value="domain",
            label="Group by:",
            size="sm",
            mb=15,
        ),
        html.Div(
            id="policy-placemat-div",
            children=[
                html.Div(
                    id="policy-checkout-package-split",
                    style={"display": "flex", "flex-wrap": "wrap"},
                ),
                dcc.Graph(
                    id="policy-checkout-graph",
                    style={"height": "70vh", "width": "100%"},
                ),
            ],
        ),
        html.Div(
            id="policy-checkout-tables",
            children=[
                dmc.Table(
                    id="domain-breakdown-checkout-tables",
                    highlightOnHover=True,
                    withBorder=False,
                    withColumnBorders=True,
                    striped=True,
                    style={"margin-bottom": "2rem"},
                ),
                dmc.Title("Options Breakdown", order=2, style={"text-align": "center"}),
                dmc.Table(
                    id="policy-breakdown-checkout-tables",
                    highlightOnHover=True,
                    withBorder=False,
                    withColumnBorders=True,
                    striped=True,
                ),
            ],
        ),
    ],
    style={"margin-bottom": "20vh"},
)


@app.callback(
    Output("policy-placemat-div", "style"),
    Output("policy-checkout-tables", "style"),
    Input("full-package-segmented", "value"),
)
def update_graph_style(value):
    if value == "placemat":
        return {}, {"display": "none"}
    else:
        return {"display": "none"}, {}


# populating saved government dropdowns in load gov and compare gov features
@app.callback(
    Output("policy-checkout-select", "options"),
    Input("policy-checkout-select", "value"),
)
def update_select_data(trigger):
    # find latest baseline gov based on storage
    # which is already sorted by gov date
    saved_score_cards_metadata = get_saved_scorecards_metadata()
    if len(saved_score_cards_metadata) == 0:
        return []

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
    return load_scorecard_options


@app.callback(
    Output("policy-checkout-graph", "figure"),
    Input("policy-checkout-select", "value"),
    Input("radiogroup-placemat", "value"),
)
def update_graph(saved_scorecards, radio_value):
    if not saved_scorecards:
        return go.Figure()

    if radio_value == "package":
        groupby_value = "package_with_cost"
    elif radio_value == "domain":
        groupby_value = "lens_1"
    else:
        groupby_value = "lens_2"

    # append the saved scorecards to the full_df
    df = pd.DataFrame()
    for file in saved_scorecards:
        package_df = import_data(f"saved_scorecards/{file}.csv")

        # costs of policies have changed over time so we only need whether the choice was Low, Medium or High
        package_df = package_df[["id", "option"]]
        package_df = package_df.merge(full_df, on="id", how="left")

        cost = []
        for row in package_df.to_dict("records"):
            cost.append(row[row["option"]])

        package_df["cost"] = cost

        # take only options that are still in play
        package_df = package_df[package_df["id"].isin(full_df["id"])]
        package_df = package_df.dropna(subset=["lens_1", "lens_2"])

        # add package name to dataframe
        metadata_dict = json_from_s3(f"saved_scorecards/metadata/{file}.json")
        package_total = round(package_df["cost"].sum(), 1)
        package_df["package"] = f"{metadata_dict['name']}"
        package_df[
            "package_with_cost"
        ] = f"{metadata_dict['name']} (€{package_total}mn)"

        # append to df
        df = df.append(package_df)

    df = df.reset_index()

    # groupby the radio value
    domain_df = df.copy()
    domain_groupby_df = domain_df.groupby([groupby_value]).sum().reset_index()
    domain_groupby_df = domain_groupby_df.sort_values("cost", ascending=False)

    domain_groupby_df["percentage_cost"] = round(
        (domain_groupby_df["cost"] / domain_groupby_df["cost"].sum() * 100), 1
    )
    domain_groupby_df["cost"] = "€" + round(domain_groupby_df["cost"], 1).astype(str) + "mn"
    domain_groupby_df["percentage_cost"] = (
        domain_groupby_df["percentage_cost"].astype(str) + "%"
    )
    domain_groupby_df = domain_groupby_df[[groupby_value, "cost", "percentage_cost"]]
    domain_groupby_df.columns = ["domain", "Cost (mn)", "% of total cost"]

    total_cost = round(df["cost"].sum(), 1)
    df["type"] = f"Total (€{total_cost}mn)"

    # if it is one of the lenses, then merge the latest full dataset if any changes
    if (groupby_value == "lens_1") | (groupby_value == "lens_2"):
        df = df.merge(
            domain_groupby_df, left_on=groupby_value, right_on="domain", how="left"
        )
        df[groupby_value] = (
            df["domain"] + " - " + df["Cost (mn)"] + " (" + df["% of total cost"] + ")"
        )
        # Find duplicate rows based on 'domain' and 'policy_option' columns
        duplicates = df.duplicated(subset=["lens_1", "policy_options"], keep=False)
        # Modify the 'domain' column by adding a string from the 'description' column for duplicates
        df.loc[duplicates, "policy_options"] = (
            df["policy_options"] + " (*" + df["package"] + " package)"
        )

    fig = get_treemap(
        df.reset_index(), path=["type", groupby_value, "policy_options"], length=15
    )

    return fig


@app.callback(
    Output("policy-breakdown-checkout-tables", "children"),
    Output("domain-breakdown-checkout-tables", "children"),
    Input("policy-checkout-select", "value"),
    Input("radiogroup-placemat", "value"),
)
def update_tables(saved_scorecards, radio_value):
    if not saved_scorecards:
        return [], []

    if radio_value == "package":
        groupby_value = "package_with_cost"
    elif radio_value == "domain":
        groupby_value = "lens_1"
    else:
        groupby_value = "lens_2"

    # get data
    df = pd.DataFrame()
    for file in saved_scorecards:
        package_df = import_data(f"saved_scorecards/{file}.csv")
        package_df = package_df[["id", "option"]]
        package_df = package_df.merge(full_df, on="id", how="left")

        cost = []
        for row in package_df.to_dict("records"):
            cost.append(row[row["option"]])

        package_df["cost"] = cost
        package_df = package_df[package_df["id"].isin(full_df["id"])]
        package_df = package_df.dropna(subset=["lens_1", "lens_2"])
        metadata_dict = json_from_s3(f"saved_scorecards/metadata/{file}.json")
        package_total = round(package_df["cost"].sum(), 1)
        package_df["package"] = f"{metadata_dict['name']}"
        package_df[
            "package_with_cost"
        ] = f"{metadata_dict['name']} (€{package_total}mn)"

        df = df.append(package_df)

    df = df.reset_index()

    policy_df = df.copy()
    policy_df["percentage_cost"] = round(
        (policy_df["cost"] / policy_df["cost"].sum() * 100), 1
    )
    policy_df["percentage_cost"] = policy_df["percentage_cost"].astype(str) + "%"
    policy_df = policy_df.sort_values("cost", ascending=False)
    policy_df["cost"] = "€" + policy_df["cost"].astype(str) + "mn"

    table_policy_df = policy_df[
        [
            "package_with_cost",
            "policy_options",
            groupby_value,
            "cost",
            "percentage_cost",
        ]
    ]
    table_policy_df.columns = [
        "Package",
        "Policy",
        "domain",
        "Cost (€mn)",
        "% of total cost",
    ]

    if radio_value == "package":
        table_policy_df = table_policy_df.drop(columns=["Package"])

    table = create_dashboard_detail_table(table_policy_df)

    domain_df = df.copy()
    domain_groupby_df = domain_df.groupby([groupby_value]).sum().reset_index()
    domain_groupby_df = domain_groupby_df.sort_values("cost", ascending=False)

    domain_groupby_df["percentage_cost"] = round(
        (domain_groupby_df["cost"] / domain_groupby_df["cost"].sum() * 100), 1
    )
    domain_groupby_df["cost"] = "€" + round(domain_groupby_df["cost"], 2).astype(str) + "mn"
    domain_groupby_df["percentage_cost"] = (
        domain_groupby_df["percentage_cost"].astype(str) + "%"
    )
    domain_groupby_df = domain_groupby_df[[groupby_value, "cost", "percentage_cost"]]
    domain_groupby_df.columns = ["domain", "Cost (€mn)", "% of total cost"]

    total_df = pd.DataFrame(
        {
            "domain": ["Total"],
            "Cost (€mn)": ["€" + round(domain_df["cost"].sum(), 2).astype(str) + "mn"],
            "% of total cost": ["-"],
        }
    )
    domain_table_df = pd.concat([total_df, domain_groupby_df], ignore_index=True)

    domain_table = create_dashboard_detail_table(domain_table_df)

    return table, domain_table

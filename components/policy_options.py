import math
from dash import html, dcc
import dash_mantine_components as dmc


def policy_option(row_dict, scalable_value="medium"):
    id = row_dict["id"]
    label = row_dict["policy_options"]
    on_or_off = row_dict["on_off"]

    if row_dict["flag"] == "awaiting":
        disabled = True
        color = "#d3d3d3"
    else:
        disabled = False
        color = ""

    if row_dict["flag"] == "scalable":
        options = []
        for scale in ["very-low", "low", "medium", "high"]:
            if not math.isnan(row_dict[scale]):
                options.append(
                    {
                        "label": f"€{round(row_dict[scale], 2)}mn ({scale.capitalize()})",
                        "value": scale,
                    }
                )

        cost = dcc.Dropdown(
            options=options,
            value=scalable_value,
            clearable=False,
            searchable=False,
            id={"type": "cost-dropdown", "index": f"{id}"},
        )

    else:
        cost_number = (
            f"€{row_dict['medium']:,.1f}mn"
            if not math.isnan(row_dict["medium"])
            else "TBC"
        )
        cost = dmc.Text(
            cost_number,
            size="md",
            weight=550,
            id={"type": "cost-dropdown", "index": f"{id}"},
        )

    return html.Div(
        [
            dmc.Divider(style={"margin": "6px 0"}),
            html.Div(
                [
                    html.Div(
                        [
                            dmc.Checkbox(
                                id={"type": "policy-option", "index": f"{id}"},
                                checked=on_or_off,
                                size="md",
                                disabled=disabled,
                            ),
                            dmc.Text(label, size="md", weight=450),
                        ],
                        style={
                            "display": "flex",
                            "gap": "1rem",
                            "align-items": "center",
                            "color": color,
                            "width": "60%",
                        },
                    ),
                    html.Div(cost, style={"width": "40%"}),
                ],
                style={
                    "display": "flex",
                    "gap": "2rem",
                    "align-items": "center",
                },
            ),
        ],
        id={"type": "policy-option-div", "index": f"{id}"},
    )


def policy_categories(category, categories_df):
    return html.Div(
        [
            dmc.Title(
                category.upper(),
                order=4,
                color="gray",
                style={"width": "100%", "text-align": "center"},
            ),
        ]
        + [
            policy_option(row_dict, scalable_value=row_dict["option"])
            for row_dict in categories_df.to_dict("records")
        ],
        style={"margin-bottom": "15px"},
    )

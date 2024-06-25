from dash import html
import dash_mantine_components as dmc

def spend_type_div(category, pricing_dict):
    return html.Div(
        [
            dmc.Text(
                f"{category}:",
                weight=450,
            ),
            dmc.Text(
                f"{pricing_dict['%']}%",
                weight=600,
            ),
            dmc.Text(f"(€{pricing_dict['€']}mn)", weight=450, size="xs"),
        ],
        style={
            "display": "flex",
            "align-items": "center",
            "gap": "5px",
            "margin-right": "30px",
        },
    )


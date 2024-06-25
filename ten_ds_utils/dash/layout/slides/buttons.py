from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify


def slide_button(button_label, link_id):
    # border radius for attachment to home button
    sx_props = {"borderRadius": "0px 4px 4px 0px"} if "Prev" in button_label else {}

    return dcc.Link(
        id=link_id,
        children=dmc.Button(
            button_label,
            disabled=True,
            color="pink",
            id=f"{link_id}-button",
            sx=sx_props,
        ),
        href="/",
    )


def home_button():
    return dcc.Link(
        id="home-link",
        children=dmc.Button(
            children=[DashIconify(icon="tabler:home", width=20)],
            color="pink",
            variant="filled",
            sx={
                "height": "36px",
                "width": "36px",
                "borderRadius": "4px 0px 0px 4px",
                "marginRight": "1px",
                "padding": "0px",
            },
            id=f"home-link-button",
        ),
        href="/",
    )


def control_panel():
    return html.Div(
        [
            html.Div(
                [
                    home_button(),
                    # previous slide button
                    slide_button(
                        button_label="← Prev.",
                        link_id="previous-slide-link",
                    ),
                ],
                style={"display": "flex"},
            ),
            # menu button which shows navigation menu on hover
            html.Div(
                [
                    html.Div(
                        [
                            dmc.Text(
                                id="current-slide-number",
                                style={"width": "1rem"},
                            ),
                            dmc.Text("/", style={"width": "0.5rem"}),
                            dmc.Text(
                                id="total-slide-number",
                                style={"width": "1rem"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justify-content": "center",
                            "gap": "5px",
                            "text-align": "center",
                        },
                    ),
                    dmc.Progress(
                        size="md",
                        id="slide-progress",
                        color="pink",
                        radius=9999,
                        style={"width": "12vw"},
                    ),
                ],
                style={
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "center",
                },
            ),
            slide_button(button_label="Next →", link_id="next-slide-link"),
        ],
        style={"display": "flex", "gap": "1rem"},
    )

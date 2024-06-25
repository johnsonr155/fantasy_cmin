import dash_mantine_components as dmc
from dash import html
from dash_iconify import DashIconify

from ten_ds_utils.dash.layout.slides.table_of_contents.table_of_contents_item import (
    LINK_WIDTH_REM,
)


def table_of_contents(contents_max_number_of_columns):
    # sets width of table of contents card based on number of columns user has specified
    CARD_WIDTH = 20 + LINK_WIDTH_REM * 16 * contents_max_number_of_columns
    return dmc.HoverCard(
        withArrow=False,
        width=CARD_WIDTH,
        shadow="xl",
        position="top-start",
        offset=28,
        zIndex=1000,
        children=[
            # hovercard appears on hover over contents button
            dmc.HoverCardTarget(
                dmc.Paper(
                    children=[
                        html.Div(
                            [
                                DashIconify(icon="tabler:list-search", width=18),
                                dmc.Text("Contents", weight=400, size="sm"),
                            ],
                            style={
                                "display": "flex",
                                "padding": "0 18px",
                                "align-items": "center",
                                "gap": "0.5rem",
                                "color": "#e64980",
                                "height": "34px",
                            },
                        )
                    ],
                    p=0,
                    radius="sm",
                    sx={
                        "backgroundColor": "#fff",
                        "border": "1px solid #e64980",
                        "&:hover": {"backgroundColor": "#fcedf6", "cursor": "pointer"},
                        "border-radius": "4x",
                    },
                )
            ),
            # contents of table of contents pop-up is set by set_contents function in callback handler
            dmc.HoverCardDropdown(id="10ds-slide-contents"),
        ],
    )

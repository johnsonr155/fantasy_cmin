from dash import html, dcc
import dash_mantine_components as dmc
from dash_extensions import EventListener

from ten_ds_utils.dash.layout.utils import check_all_pages_exist
from ten_ds_utils.dash.layout.slides.callback_handler import slides_callback_handler
from ten_ds_utils.dash.layout.slides.buttons import control_panel, home_button
from ten_ds_utils.dash.layout.slides.table_of_contents.table_of_contents_component import (
    table_of_contents,
)
from ten_ds_utils.dash.layout.logging import logging_wrapper


def slides_nav_bar(
    left_nav_div_children,
    right_nav_div_children,
    contents_max_number_of_columns,
):
    """
    Return navigation bar containing, from left to right, custom left div (for e.g. dashboard title),
    previous slide button, button which shows navigation menu on hover,
    next slide button, custom right div (for e.g. dept logo)
    """
    if bool(left_nav_div_children) or bool(right_nav_div_children):
        min_width, width = "80rem", "100%"
    else:
        min_width, width = "55rem", ""

    return html.Div(
        [
            html.Div(
                id="10ds-slide-navigation",
                style={
                    "width": width,
                    "min-width": min_width,
                    "max-width": "85vw",
                    "border-radius": "9999px",
                    "padding": "15px 0px",
                    "background-color": "white",
                    "filter": "drop-shadow(0 10px 8px rgb(0 0 0 / 0.04)) drop-shadow(0 2px 4px rgb(0 0 0 / 0.1))",
                },
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "gap": "1rem",
                        },
                        children=[
                            # user's custom left div
                            html.Div(
                                children=[
                                    html.Div(
                                        children=left_nav_div_children,
                                        style={
                                            "display": "flex",
                                            "width": "100%",
                                            "justify-content": "center",
                                        },
                                    ),
                                    table_of_contents(contents_max_number_of_columns),
                                ],
                                style={
                                    "width": "35%",
                                    "padding-left": "1.5rem",
                                    "display": "flex",
                                    "justify-content": "space-between",
                                    "align-items": "center",
                                    "gap": "10px",
                                },
                            ),
                            control_panel(),
                            # user's custom right div
                            html.Div(
                                children=right_nav_div_children,
                                style={
                                    "width": "35%",
                                    "padding-right": "1.5rem",
                                    "display": "flex",
                                    "justify-content": "space-around",
                                    "align-items": "center",
                                    "gap": "10px",
                                },
                            ),
                        ],
                    ),
                ],
            )
        ],
        style={
            "display": "flex",
            "justify-content": "center",
            "position": "fixed",
            "left": "0px",
            "right": "0px",
            "bottom": "1vh",
            "width": "100vw",
            "z-index": "1000",
        },
    )


def default_slide_structure(
    self,
    landing_page,
    slides_dict,
    left_nav_div_children,
    right_nav_div_children,
    contents_max_height,
    contents_max_number_of_columns,
    contents_font_size,
):
    """
    Returns 10ds slide navigation panel and handles url changes
    """
    check_all_pages_exist(self.directory_manager, slides_dict)

    # Initialise the callbacks that handle the url and page content
    slides_callback_handler(
        self, landing_page, slides_dict, contents_max_height, contents_font_size
    )
    return logging_wrapper(
        self,
        html.Div(
            [
                dcc.Location(id="10ds-url", refresh=False),
                EventListener(
                    id="10ds-keydown-listener",
                    events=[{"event": "keydown", "props": ["key", "repeat"]}],
                    logging=False,
                ),
                html.Div(
                    [
                        html.Div(
                            html.Div(id="10ds-page-content"),
                            id="10ds-page-content-wrapper",
                            style={"width": "100%"},
                        ),
                        # buffer for bottom slider to appear under content if over ~90vh
                        html.Div(style={"height": "6vh"}),
                    ],
                    style={"display": "flex"},
                ),
                slides_nav_bar(
                    left_nav_div_children,
                    right_nav_div_children,
                    contents_max_number_of_columns,
                ),
            ],
            style={"width": "100%"},
        ),
    )

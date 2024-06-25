# third party
from dash import html
from dash.html import Div
from typeguard import typechecked
import dash_mantine_components as dmc

DEFAULT_STYLE = {
    "margin-left": "2.5%",
    "margin-right": "2.5%",
    "margin-top": "1%",
    "margin-bottom": "1%",
}


@typechecked
def full_page(title: str = "", children: list = [], style: dict = {}) -> Div:
    if title != "":
        title_component = dmc.Title(title, order=2, style={"margin-bottom": "10px"})
    else:
        title_component = html.Div()

    return html.Div(
        [
            title_component,
            html.Div(children, style={"display": "grid", "gap": "10px"}),
        ],
        style=DEFAULT_STYLE | style,
    )


@typechecked
def ratio_page(
    title: str = "",
    left_panel: list = [],
    right_panel: list = [],
    left_proportion: float = 1 / 3,
) -> Div:
    panel_styles = {"display": "grid", "gap": "10px", "height": "100%"}
    children = [
        html.Div(left_panel, style=panel_styles | {"width": f"{left_proportion*100}%"}),
        html.Div(
            right_panel, style=panel_styles | {"width": f"{(1-left_proportion)*100}%"}
        ),
    ]

    return html.Div(
        [
            dmc.Title(title, order=2, style={"margin-bottom": "10px"}),
            html.Div(
                children,
                style={
                    "display": "flex",
                    "justify-content": "space-between",
                    "gap": "10px",
                },
            ),
        ],
        style=DEFAULT_STYLE,
    )


@typechecked
def one_third_page(
    title: str = "",
    left_panel: list = [],
    right_panel: list = [],
    swap_panel_widths: bool = True,
) -> Div:

    left_proportion = 2 / 3 if swap_panel_widths else 1 / 3
    return ratio_page(title, left_panel, right_panel, left_proportion=left_proportion)


@typechecked
def half_page(title: str = "", left_panel: list = [], right_panel: list = []) -> Div:
    return ratio_page(title, left_panel, right_panel, left_proportion=0.5)

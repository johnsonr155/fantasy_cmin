import pandas as pd
from dash import dcc, html
import dash_bootstrap_components as dbc

from ten_ds_utils.dash.app import create_app


statement = html.P(
    children=[
        "The information displayed here is ",
        html.Strong("OFFICIAL SENSITIVE."),
        " Do not share, copy or screenshot this data without permission.",
    ],
    style={"marginBottom": 0},
)


def official_sensitive_warning():
    """Warning label"""
    return html.Div(
        dbc.Alert(
            statement,
            color="warning",
            style={
                "textAlign": "center",
            },
            dismissable=True,
            fade=True,
        ),
        id="official-sensitive-warning",
        style={
            "position": "fixed",
            "top": "80px",
            "left": "0",
            "width": "100%",
            "z-index": "10",
        },
    )


def header_dropdown(labelText, optionsDF):
    """Nav bar dropdown component:
    labelText: str
    optionsDF: dataframe with label, id and href columns
    """
    return dbc.DropdownMenu(
        className="mx-4",
        label=labelText,
        children=[
            dbc.DropdownMenuItem(
                children=row.label,
                id=row.id + "-link",
                href=row.href,
            )
            for index, row in optionsDF.iterrows()
        ],
        nav=True,
        in_navbar=True,
    )


other_dashboards_df = pd.DataFrame(
    [
        {
            "label": "Electives Stocktake",
            "id": "electives-stocktake",
            "href": "/electives-stocktake/",
        },
        {
            "label": "Crime and Justice Stocktake",
            "id": "cjs-stocktake",
            "href": "/cjs-delivery/",
        },
        {
            "label": "Net Zero Stocktake",
            "id": "nz-stocktake",
            "href": "/nz-delivery/",
        },
    ]
)

about_10ds_df = pd.DataFrame(
    [
        {"label": "About us", "id": "about-nav", "href": "/about/"},
        {
            "label": "December Bulletin",
            "id": "bulletin-nav",
            "href": "/10DS-bulletin/",
        },
        {"label": "Contact us", "id": "contacts-nav", "href": "/contacts/"},
        {
            "label": "Analytical Quality Stamp",
            "id": "aqs-nav",
            "href": "/what-is-AQS/",
        },
        {
            "label": "Project rAPId",
            "id": "rapid-nav",
            "href": "/project-rapid/",
        },
        {
            "label": "Data Catalogue",
            "id": "data-catalogue-nav",
            "href": "/data-catalogue/",
        },
        {
            "label": "Data Science Fellowship",
            "id": "ds-fellows-nav",
            "href": "/data-science-fellows/",
        },
        {
            "label": "Innovation Fellowship",
            "id": "innovation-fellows-nav",
            "href": "/innovation-fellows/",
        },
    ]
)


logo_10ds = html.Img(
    src="/assets/10ds.svg", className="govuk-header-10ds__logotype-10ds"
)


def header_layout():
    """Common header for the top of the page - Navbar"""

    return html.Div(
        [
            html.Nav(
                [
                    html.A(
                        [
                            html.Span(
                                logo_10ds,
                                className="govuk-header-10ds__logotype",
                            ),
                        ],
                        href="/",
                    ),
                    html.Button(
                        html.Span(className="navbar-toggler-icon"),
                        className="navbar-toggler",
                        type="button",
                        **{
                            "data-toggle": "collapse",
                            "data-target": "#navbarNav",
                            "aria-controls": "navbarNav",
                            "aria-expanded": "false",
                            "aria-label": "Toggle navigation",
                        }
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Link(
                                        "Government Performance",
                                        id="government-performance-nav-link",
                                        className="government-performance-item nav-link mx-4",
                                        href="/government-performance/",
                                    ),
                                    header_dropdown("Delivery", other_dashboards_df),
                                    dcc.Link(
                                        "Meeting Planner",
                                        id="play-my-meeting",
                                        className="government-performance-item nav-link mx-4",
                                        href="/meeting-player/",
                                    ),
                                    dcc.Link(
                                        "Policy Tools",
                                        id="site-map-nav-link",
                                        className="government-performance-item nav-link mx-4",
                                        href="/navigation-page/",
                                    ),
                                    dcc.Link(
                                        "Other Dashboards",
                                        id="other-dashboards-nav-link",
                                        className="government-performance-item nav-link mx-4",
                                        href="/other-dashboards/",
                                    ),
                                    header_dropdown("About 10DS", about_10ds_df),
                                ],
                                className="navbar-nav",
                            ),
                        ],
                        className="navbar-collapse collapse",
                        id="navbarNav",
                    ),
                ],
                className="navbar navbar-expand-lg navbar-dark bg-primary",
            ),
            official_sensitive_warning(),
        ],
        style={"height": "80px"},
    )


if __name__ == "__main__":
    app = create_app()
    app.layout = header_layout()
    app.run_server(debug=True)

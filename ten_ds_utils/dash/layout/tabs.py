# std
import os

# third party
import dash
from dash import html, dcc, Input, Output, State, ALL
import dash_mantine_components as dmc

# 10ds
from ten_ds_utils.dash.utils import fetch_query_string, clean_pathname
from ten_ds_utils.dash.layout.logging import logging_wrapper
from ten_ds_utils.dash.layout.utils import check_all_pages_exist

PRIAMRY_PINK = "#c9348c"
SECONDARY_PINK = "#f4e1ed"
GRAY = "#f7f7f7"

PRIMARY_TAB_ACTIVE = {
    "backgroundColor": PRIAMRY_PINK,
    "borderBottomColor": PRIAMRY_PINK,
    "color": "#fff",
    "transition": "all 0.2s ease",
}

PRIMARY_TABS_STYLE_API = {
    "root": {
        "marginTop": "20px",
        "marginBottom": "5px",
        "position": "sticky",
        "top": "0px",
        "left": "0px",
        "zIndex": "100",
        "backgroundColor": "#fff",
        "color": "#55596c",
        "paddingTop": "5px",
    },
    "tabsList": {"borderBottomWidth": "3px", "borderBottomColor": PRIAMRY_PINK},
    "tab": {
        "marginBottom": "-3px",
        "marginRight": "5px",
        "marginLeft": "5px",
        "fontWeight": "500",
        "color": "#55596c",
        "backgroundColor": GRAY,
        "borderBottom": f"3px solid {PRIAMRY_PINK}",
        "&[data-active]": PRIMARY_TAB_ACTIVE,
        "&[data-active]:hover": PRIMARY_TAB_ACTIVE,
        "&:hover": PRIMARY_TAB_ACTIVE,
    },
}

SECONDARY_TAB_ACTIVE = {
    "backgroundColor": SECONDARY_PINK,
    "borderRightColor": PRIAMRY_PINK,
    "transition": "all 0.4s ease",
}

SECONDARY_TABS_STYLE_API = {
    "root": {
        "color": "#55596c",
        "width": "15%",
        "marginTop": "10px",
        "minWidth": "150px",
        "minHeight": "200px",
    },
    "tabsList": {
        "display": "block",
        "width": "100%",
        "height": "100vh",
        "borderWidth": "0px",
        "position": "sticky",
        "top": "60px",
    },
    "tab": {
        "display": "flex",
        "justifyContent": "end",
        "fontSize": "1.1rem",
        "width": "100%",
        "marginLeft": "5px",
        "marginBottom": "5px",
        "borderRadius": "0px",
        "color": "#55596c",
        "borderRight": f"4px solid rgb(222, 226, 230)",
        "backgroundColor": GRAY,
        "&[data-active]": SECONDARY_TAB_ACTIVE | {"fontWeight": "550"},
        "&[data-active]:hover": SECONDARY_TAB_ACTIVE,
        "&:hover": SECONDARY_TAB_ACTIVE,
    },
    "tabLabel": {"whiteSpace": "normal", "text-align": "right"},
}


def create_primary_tab(label, path):
    """Creates a primary tab with an hrefs wrapped around it to work with the directory manager"""
    prefix_url = os.environ.get("PREFIX_URL", "/")

    if path != "/":
        value = path.split("/")[0]
        href = f"{prefix_url}{path}/"
    else:
        value = "/"
        href = prefix_url

    return dcc.Link(
        dmc.Tab(
            children=[label],
            value=value,
            style={"font-size": "1.2rem"},
        ),
        href=href,
        id={"type": f"10ds-primary-tab", "index": path},
        style={
            "text-decoration": "none",
        },
    )


def create_secondary_tab(label, path):
    """Creates a secondary tab wrapped in an href to work with the directory manager"""
    prefix_url = os.environ.get("PREFIX_URL", "/")
    return dcc.Link(
        dmc.Tab(
            children=[label],
            value=f"{path}",
        ),
        href=f"{prefix_url}{path}",
        id={
            "type": f"10ds-secondary-tab",
            "index": f"{path}",
        },
        style={
            "text-decoration": "none",
        },
    )


def tabs_callback_handler(self, secondary_tabs_dict, landing_page_path):
    """
    Handles neccessary callbacks for tab layout to function:
     * multi_page_directory_with_sidebar - Retrieves page-content and sidebar if available
     * add_user_tokens_to_hrefs - Adds user's token to the hrefs of each tab so ensure continued access
     * set_primary_active_tab - Highlights the tab the user has landed on based on the pathname
    """
    if isinstance(landing_page_path, list):
        landing_page_path = "/".join(landing_page_path)

    @self.app.callback(
        [
            Output("10ds-page-content", "children"),
            Output("10ds-page-content-wrapper", "style"),
            Output("10ds-secondary-tabs-wrapper", "children"),
            Output("10ds-secondary-tabs-wrapper", "className"),
            Output("10ds-secondary-tabs-wrapper", "value"),
        ],
        [Input("10ds-url", "href"), Input("10ds-url", "pathname")],
    )
    def multi_page_directory_with_sidebar(href, pathname):
        """
        Secondary tabs added to a dictionary based on their path.
        This callback checks if there is a secondary tab in the
        dictionary and returns it if the key exists in `secondary_tabs_dict`.

        Also sets the relevant secondary tab to be active depending on the link
        """
        if self.prefix_url != "/":
            pathname = pathname.replace(self.prefix_url, "/")

        # landing page accounting for prefix_url being replaced
        if pathname == "/":
            pathname = landing_page_path

        pathname = pathname.strip("/")
        default_page = self.directory_manager._url_objects[landing_page_path]
        page_layout = self.directory_manager._url_objects.get(pathname, default_page)

        primary_pathname = pathname.split("/")[0]
        secondary_tab_active = pathname

        # class name is used here as we need to keep the dmc.Tabs wrapper styling
        # d-none is equivalent to adding {"display": "none"}

        if primary_pathname in secondary_tabs_dict.keys():
            class_name = ""
            page_content_style = {"width": "85%"}

        else:
            class_name = "d-none"
            page_content_style = {"width": "100%"}

        secondary_tab_children = secondary_tabs_dict.get(
            primary_pathname, dash.no_update
        )

        return (
            page_layout,
            page_content_style,
            secondary_tab_children,
            class_name,
            secondary_tab_active,
        )

    @self.app.callback(
        [
            Output({"type": "10ds-primary-tab", "index": ALL}, "href"),
            Output({"type": "10ds-secondary-tab", "index": ALL}, "href"),
        ],
        [Input("10ds-url", "href"), Input("10ds-url", "pathname")],
        [
            State({"type": "10ds-primary-tab", "index": ALL}, "href"),
            State({"type": "10ds-secondary-tab", "index": ALL}, "href"),
        ],
    )
    def add_user_tokens_to_hrefs(
        href, pathname, create_primary_tab_hrefs, secondary_create_primary_tab_hrefs
    ):
        "Updates all tab hrefs to include the user token so token is passed to the iframe"
        pathname = clean_pathname(pathname, self.prefix_url)
        full_hrefs_list = list(create_primary_tab_hrefs) + list(
            secondary_create_primary_tab_hrefs
        )
        user_token = fetch_query_string(href)

        href_links = list(
            map(
                lambda tab_href: tab_href.split("?")[0] + "?" + user_token,
                full_hrefs_list,
            )
        )

        len_primary_hrefs = len(create_primary_tab_hrefs)
        primary_href_links = href_links[:len_primary_hrefs]
        secondary_href_links = href_links[len_primary_hrefs:]

        return [primary_href_links, secondary_href_links]

    @self.app.callback(
        Output("10ds-primary-tabs-wrapper", "value"),
        [Input(f"10ds-url", "href"), Input(f"10ds-url", "pathname")],
    )
    def set_primary_active_tab(href, pathname):
        """Sets the correct primary tab to be active depending on the url path"""
        pathname = clean_pathname(pathname, self.prefix_url)
        if pathname != "/":
            active_tab = pathname.strip("/").split("/")[0]
        else:
            active_tab = landing_page_path.split("/")[0]

        return active_tab


def default_tab_structure(self, landing_page, tabs_dict, **kwargs):
    check_all_pages_exist(self.directory_manager, tabs_dict)

    create_primary_tabs_list = []
    secondary_tabs_dict = {}

    for path, children in tabs_dict.items():
        # If the child is a dictionary then create subtabs
        if isinstance(children, dict):
            secondary_tabs = children["section-pages"]
            secondary_tabs_dict[path] = [
                dmc.TabsList(
                    [
                        create_secondary_tab(label, path=f"{path}/{secondary_path}")
                        for secondary_path, label in secondary_tabs.items()
                    ],
                )
            ]
            path = f"{path}/{list(secondary_tabs.keys())[0]}"
            create_primary_tab_label = children["section-title"]

        # No subtabs pass children as the label
        else:
            create_primary_tab_label = children

        # Add primary tab to list
        create_primary_tabs_list.append(
            create_primary_tab(
                label=create_primary_tab_label,
                path=path,
            )
        )

    # Initialise the callbacks that handle the url, page content, sidebars
    tabs_callback_handler(self, secondary_tabs_dict, landing_page)

    return logging_wrapper(
        self,
        html.Div(
            [
                dcc.Location(id="10ds-url", refresh=False),
                dmc.Tabs(
                    [
                        dmc.TabsList(
                            create_primary_tabs_list,
                        )
                    ],
                    id="10ds-primary-tabs-wrapper",
                    orientation="horizontal",
                    styles=PRIMARY_TABS_STYLE_API,
                    **kwargs,
                ),
                html.Div(
                    [
                        # seondary tabs appear here and are populated
                        # using a callback if subtabs are available
                        dmc.Tabs(
                            [],
                            orientation="vertical",
                            id="10ds-secondary-tabs-wrapper",
                            color="pink",
                            styles=SECONDARY_TABS_STYLE_API,
                        ),
                        html.Div(
                            html.Div(id="10ds-page-content"),
                            id="10ds-page-content-wrapper",
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ],
            style={"width": "100%"},
        ),
    )

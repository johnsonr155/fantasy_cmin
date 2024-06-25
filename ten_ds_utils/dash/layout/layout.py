# std
import os
from dataclasses import dataclass

# third party
from dash import dcc, html, Dash
from typeguard import typechecked

# project
from ten_ds_utils.dash.directory_manager import DashDirectoryManager
from ten_ds_utils.dash.layout.pages import (
    full_page,
    one_third_page,
    half_page,
    ratio_page,
)
from ten_ds_utils.dash.layout.tabs import default_tab_structure
from ten_ds_utils.dash.layout.slides import default_slide_structure
from ten_ds_utils.dash.layout.logging import logging_wrapper
from ten_ds_utils.config.dash import DashConfig


@typechecked
@dataclass
class Layout:
    app: Dash

    def __post_init__(self):
        self.prefix_url = os.environ.get("PREFIX_URL", "/")
        self.conf = DashConfig()
        self.directory_manager = DashDirectoryManager()

    def get_page_from_directory(self, path: str):
        """Returns dash object from the directory manager depending on given path"""
        return self.directory_manager._url_objects.get(path)

    def add_full_page(
        self, path: str | list, title: str, children: list, style: dict = {}
    ):
        """Adds a full width page to the directory manager"""
        page_layout = full_page(title, children, style)
        self.directory_manager.add_url_to_directory(path, page_layout)

    def add_one_third_page(
        self,
        path: str | list,
        title: str,
        left_panel: list,
        right_panel: list,
        swap_panel_widths: bool = False,
    ):
        """Adds a page layout split by 1:2 to the directory manager"""
        page_layout = one_third_page(title, left_panel, right_panel, swap_panel_widths)
        self.directory_manager.add_url_to_directory(path, page_layout)

    def add_half_page(
        self, path: str | list, title: str, left_panel: list, right_panel: list
    ):
        """Adds a half and half page to the directory manager"""
        page_layout = half_page(title, left_panel, right_panel)
        self.directory_manager.add_url_to_directory(path, page_layout)

    def add_ratio_page(
        self,
        path: str | list,
        title: str,
        left_panel: list,
        right_panel: list,
        left_proportion: float,
    ):
        """Adds a half and half page to the directory manager"""
        page_layout = ratio_page(title, left_panel, right_panel, left_proportion)
        self.directory_manager.add_url_to_directory(path, page_layout)

    def build_single_page(self) -> html.Div:
        """
        Returns a html.Div that can be used to return pages stored from the directory manager.

        Can be helpful when initialising a project or you want to only have a single page app
        """
        self.directory_manager.multi_page_directory_callback(
            self.app,
            default_page_id="/",
            dashboard_layout_id=f"10ds-page-content",
            location_component_id=f"10ds-url",
        )

        return html.Div(
            logging_wrapper(
                self,
                html.Div(
                    [dcc.Location(id="10ds-url"), html.Div(id="10ds-page-content")]
                ),
            )
        )

    def build_tabs(self, landing_page: str | list, tabs_dict: dict, **kwargs):
        """
        Loops through a dictionary to create a default layout of tabs and
        sub-tabs (optional) with the ability to link to and tab and sub-tab.

        Args:
            tabs_dict (dict): Keys are paths and nested dictionary keys are sub paths.
                Values are either string (tab label) or a dictionary (signifies sub-tabs).
                Identical to the slides_dict argument in `build_slides` - the same dict will work for both.

                Example:
                    tabs_dict = {
                        "overview": "Executive Summary",
                        "example-page": "Example Single Page",
                        "policy-section-example": {
                            "section-title": "Another tab example",
                            "section-pages": {
                                "policy-explorer": "Policy Explorer",
                                "annex": "Annex",
                            },
                        },
                    }

            tab_className (str): Option to pass a className to add additional styling

            **kwargs (dict): key word arguments can be passed to the primary tabs

        Returns:
            Div: Multipage app with tabs that is controlled by the url and tabs
        """

        if "/" in tabs_dict.keys():
            raise Exception(
                f""""/" cannot be a key in `tabs_dict`, use `landing_page` to determine the default page"""
            )

        return default_tab_structure(self, landing_page, tabs_dict, **kwargs)

    def build_slides(
        self,
        landing_page,
        slides_dict,
        left_nav_div_children=html.Div(),
        right_nav_div_children=html.Div(),
        table_contents_height="25rem",
        table_contents_column=3,
        table_contents_font_size="1rem",
    ):
        """
        Loops through a dictionary to create a layout of slides and
        slides in subsections (optional) with the ability to link to each slide and sub-section slide.

        Args:
            slides_dict (dict): Keys are paths and nested dictionary keys are sub paths.
                Values are either string (slide label) or a dictionary (signifies a sub-section).
                Identical to the tabs_dict argument in `build_tabs` - the same dict will work for both.

                Example:
                    slides_dict = {
                        "overview": "Executive Summary",
                        "example-page": "Example Single Page",
                        "policy-section-example": {
                            "section-title": "Another tab example",
                            "section-pages": {
                                "policy-explorer": "Policy Explorer",
                                "annex": "Annex",
                            },
                        },
                    }

            table_contents_height (str): option to pass a max height to the slide table of contents
            table_contents_column (int): change the max number of columns displayed in the table of contents (default 3)

            **kwargs (dict): key word arguments can be passed to the primary tabs

        Returns:
            Div: Multipage app with tabs that is controlled by the url and tabs
        """

        if "/" in slides_dict.keys():
            raise Exception(
                f""""/" cannot be a key in `slides_dict`, use `landing_page` to determine the default page"""
            )

        return default_slide_structure(
            self,
            landing_page,
            slides_dict,
            left_nav_div_children,
            right_nav_div_children,
            table_contents_height,
            table_contents_column,
            table_contents_font_size,
        )

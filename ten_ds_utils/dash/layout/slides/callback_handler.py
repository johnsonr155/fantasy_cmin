import logging
import os

from dash import ALL, Input, Output, State
from dash.exceptions import PreventUpdate

from ten_ds_utils.dash.utils import clean_pathname, fetch_query_string
from ten_ds_utils.dash.layout.slides.table_of_contents.set_table_of_contents import (
    set_table_of_contents,
)


def create_slides_order(slides_dict):
    """
    Makes the slide dictionary, which is structured by section,
    into a flat list with just slide hrefs in order
    """
    slide_order_list = []
    for section_title in slides_dict:
        section = slides_dict[section_title]
        if isinstance(section, dict):
            for subsection in section["section-pages"]:
                slide_order_list.append(f"{section_title}/{subsection}")

        else:
            slide_order_list.append(f"{section_title}")

    return slide_order_list


def slides_callback_handler(
    self, landing_page_path, slides_dict, contents_max_height, contents_font_size
):
    """
    Handles neccessary callbacks for tab layout to function:
     * add_user_tokens_to_menu_hrefs - Adds user's token to the hrefs of each tab so ensure continued access
     * set_next_slide_previous_slide_href - Sets links for next slide and previous slide based on current slide, and adds user's token to hrefs
     * update_slide_count_button - Updates the slide number displayed on the menu button
    """

    # set constants
    if isinstance(landing_page_path, list):
        landing_page_path = "/".join(landing_page_path)

    slides_order_list = create_slides_order(slides_dict)
    slides_count = len(slides_order_list)

    @self.app.callback(
        Output("10ds-page-content", "children"),
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
        default_page_layout = self.directory_manager._url_objects[landing_page_path]
        page_layout = self.directory_manager._url_objects.get(
            pathname, default_page_layout
        )

        return page_layout

    @self.app.callback(
        [
            Output("slide-progress", "value"),
            Output("current-slide-number", "children"),
            Output("total-slide-number", "children"),
        ],
        [Input("10ds-url", "href"), Input("10ds-url", "pathname")],
    )
    def update_progress_bar(href, pathname):
        pathname = clean_pathname(pathname, self.prefix_url)

        if pathname == "/":
            current_slide_id = landing_page_path
        else:
            current_slide_id = pathname.lstrip("/")

        current_slide_position = slides_order_list.index(current_slide_id)
        progress = (current_slide_position + 1) / slides_count * 100

        return progress, (current_slide_position + 1), slides_count

    @self.app.callback(
        [
            Output("previous-slide-link", "href"),
            Output("previous-slide-link-button", "disabled"),
            Output("next-slide-link", "href"),
            Output("next-slide-link-button", "disabled"),
            Output("home-link", "href"),
            Output("home-link-button", "disabled"),
        ],
        [Input("10ds-url", "pathname"), Input("10ds-url", "href")],
    )
    def set_next_slide_previous_slide_button_hrefs(pathname, href):
        pathname = clean_pathname(pathname, self.prefix_url)

        if pathname == "/":
            current_slide_id = landing_page_path
        else:
            current_slide_id = pathname.lstrip("/")

        current_slide_position = slides_order_list.index(current_slide_id)

        if current_slide_position == 0:
            prev_button_disabled = True
            prev_slide_id = current_slide_id

        else:
            prev_button_disabled = False
            prev_slide_id = slides_order_list[current_slide_position - 1]

        if current_slide_position + 1 == slides_count:
            next_slide_id = current_slide_id
            next_button_disabled = True

        else:
            next_slide_id = slides_order_list[current_slide_position + 1]
            next_button_disabled = False

        user_token = fetch_query_string(href)
        prefix_url = os.environ.get("PREFIX_URL", "/")
        prev_slide_href = f"{prefix_url}{prev_slide_id}?{user_token}"
        next_slide_href = f"{prefix_url}{next_slide_id}?{user_token}"
        home_button_href = f"{prefix_url}{landing_page_path}?{user_token}"

        # home button disabled
        home_button_disabled = current_slide_id == landing_page_path

        return (
            prev_slide_href,
            prev_button_disabled,
            next_slide_href,
            next_button_disabled,
            home_button_href,
            home_button_disabled,
        )

    @self.app.callback(
        [
            Output("10ds-url", "href"),
            Output("10ds-url", "pathname"),
        ],
        [
            Input("10ds-keydown-listener", "n_events"),
            Input("10ds-keydown-listener", "event"),
        ],
        [
            State("previous-slide-link", "href"),
            State("previous-slide-link-button", "disabled"),
            State("next-slide-link", "href"),
            State("next-slide-link-button", "disabled"),
        ],
    )
    def slide_controls(
        n_events,
        event,
        prev_href,
        prev_button_disabled,
        next_href,
        next_button_disabled,
    ):
        if event is None:
            raise PreventUpdate()

        key_event = event["key"]
        if key_event == "ArrowLeft" and not prev_button_disabled:
            return prev_href, prev_href.split("?")[0]

        elif key_event == "ArrowRight" and not next_button_disabled:
            return next_href, next_href.split("?")[0]

        else:
            raise PreventUpdate()

    @self.app.callback(
        [
            Output("10ds-slide-contents", "children"),
            Input("10ds-url", "pathname"),
            Input("10ds-url", "href"),
        ]
    )
    def set_contents_layout(pathname, href):
        pathname = clean_pathname(pathname, self.prefix_url)
        logging.info(pathname)

        if pathname == "/":
            current_slide_id = landing_page_path
        else:
            current_slide_id = pathname.lstrip("/")

        user_token = fetch_query_string(href)
        prefix_url = os.environ.get("PREFIX_URL", "/")

        return set_table_of_contents(
            slides_dict,
            current_slide_id,
            prefix_url,
            user_token,
            contents_max_height,
            contents_font_size,
        )

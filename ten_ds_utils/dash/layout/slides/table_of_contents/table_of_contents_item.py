from dash import html, dcc
import dash_mantine_components as dmc


# style constants
ACTIVE_INDICATOR_WIDTH = "0.75rem"
ACTIVE_INDICATOR_MARGIN_LEFT = "-0.43rem"
LINK_WIDTH_REM = 16


def table_of_contents_section_title(section_title):
    """
    Displays name of section header
    """

    return dmc.Text(
        section_title.upper(),
        weight=500,
        color="black",
        size="sm",
        style={"padding-top": "0.5rem", "padding-bottom": "0.125rem"},
    )


def table_of_contents_slide_title(
    slide_title,
    slide_number,
    href,
    prefix_url,
    user_token,
    slide_after_subsection,
    active=False,
):
    """
    Link to a slide in the table of contents
    Includes a marker for whether this slide is active or not
    """

    margin_top = "1.5rem" if slide_after_subsection else "0rem"

    if active:
        active_indicator = html.Div(
            style={
                "border-radius": "100%",
                "border": "3px solid #e64980",
                "background-color": "white",
                "width": ACTIVE_INDICATOR_WIDTH,
                "height": ACTIVE_INDICATOR_WIDTH,
                "margin-left": ACTIVE_INDICATOR_MARGIN_LEFT,
            }
        )
        font_color = "#e64980"
        font_weight = 400
        background_color = "#fff0f6"

    else:
        active_indicator = html.Div(
            style={
                "width": ACTIVE_INDICATOR_WIDTH,
                "margin-left": ACTIVE_INDICATOR_MARGIN_LEFT,
            }
        )
        font_color = "#7a8a9c"
        font_weight = 300
        background_color = "#fff"

    return dmc.Paper(
        children=[
            dcc.Link(
                [
                    html.Div(
                        [
                            active_indicator,
                            dmc.Text(
                                [
                                    dmc.Text(f"{slide_number}. ", size="sm", span=True),
                                    slide_title,
                                ],
                                weight=font_weight,
                                style={
                                    "padding-left": "0.5rem",
                                    "color": font_color,
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "border-left": "2px solid #e9ecef",
                            "border-right": "4px solid #fff",
                            "width": f"{LINK_WIDTH_REM}rem",
                        },
                    )
                ],
                href=f"{prefix_url}{href}?{user_token}",
                style={"text-decoration": "none"},
            )
        ],
        radius=0,
        shadow=None,
        sx={
            "backgroundColor": background_color,
            "&:hover": {"backgroundColor": "#f8f9fa"},
            "marginTop": margin_top,
        },
    )


def table_of_contents_item(
    item_metadata, prefix_url=None, user_token=None, active=False
):
    """
    Wrapper function for either section header or slide title
    Depending on item metadata
    """

    if item_metadata["type"] == "section-header":
        return table_of_contents_section_title(item_metadata["title"])
    else:
        return table_of_contents_slide_title(
            slide_title=item_metadata["title"],
            slide_number=item_metadata["slide_number"],
            href=item_metadata["href"],
            prefix_url=prefix_url,
            user_token=user_token,
            slide_after_subsection=(item_metadata["type"] == "slide-after-subsection"),
            active=active,
        )

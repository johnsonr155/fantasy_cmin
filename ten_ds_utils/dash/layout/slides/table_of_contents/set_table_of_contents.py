from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from ten_ds_utils.dash.layout.slides.table_of_contents.table_of_contents_item import (
    table_of_contents_item,
    LINK_WIDTH_REM,
)


def set_table_of_contents(
    slides_dict,
    current_slide_id,
    prefix_url,
    user_token,
    contents_max_height,
    contents_font_size,
):
    """
    Function takes a slide dict and some other information e.g. which tab is active
    Processes it to work out the type of link we need for each slide in the deck
    Then outputs a table of contents to fit in the contents component hovercard
    """

    slide_info_list = []
    slide_count = 1
    for section_title in slides_dict:
        section = slides_dict[section_title]
        if isinstance(section, dict):
            # add a section header here (link goes to first slide, or no link)
            section_header_metadata = {
                "type": "section-header",
                "title": section.get("section-title", ""),
                "href": None,
            }
            slide_info_list.append(section_header_metadata)

            # then add a link for each slide
            for subsection in section["section-pages"]:
                slide_metadata = {
                    "type": "subsection-slide",
                    "title": section["section-pages"][subsection],
                    "href": f"{section_title}/{subsection}",
                    "slide_number": slide_count,
                }
                slide_info_list.append(slide_metadata)
                # uptick slide count
                slide_count += 1

        else:
            # if it's just a string, then its a standalone slide

            # check if previous slide was in a section - if so, need to format this one slightly differently
            previous_slide = slide_info_list[-1] if slide_info_list else None
            if previous_slide:
                if previous_slide["type"] == "subsection-slide":
                    slide_type = "slide-after-subsection"
                else:
                    slide_type = "slide"
            else:
                slide_type = "slide"

            slide_metadata = {
                "type": slide_type,
                "title": section,
                "href": section_title,
                "slide_number": slide_count,
            }
            slide_info_list.append(slide_metadata)
            # uptick slide count
            slide_count += 1

    return [
        html.Div(
            [
                html.Div(
                    [
                        DashIconify(icon="tabler:list-search", width=24),
                        dmc.Text(
                            "Table of contents", size="lg", color="black", weight=400
                        ),
                    ],
                    style={
                        "display": "flex",
                        "gap": "0.5rem",
                        "align-items": "center",
                        "padding-bottom": "1rem",
                    },
                ),
                html.Div(
                    [
                        table_of_contents_item(
                            item,
                            prefix_url=prefix_url,
                            user_token=user_token,
                            active=(item["href"] == current_slide_id),
                        )
                        for item in slide_info_list
                    ],
                    style={
                        "display": "flex",
                        "flex-direction": "column",
                        "max-height": contents_max_height,
                        "font-size": contents_font_size,
                        "flex-wrap": "wrap",
                        "max-width": f"{LINK_WIDTH_REM}rem",
                    },
                ),
            ],
        )
    ]

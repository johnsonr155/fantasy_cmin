# std
import os
import logging

# third party
from dash import html, dcc
import dash_mantine_components as dmc

# project
import components
from app import app, layout, server, conf, prefix_url

# initialise pages to add to directory
import layouts.dashboard
import layouts.transport_map.full_map
import layouts.checkout

logging.info("Setting main layout")

# main layout of the index page
app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Fantasy CMIN25</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

page_dict = {
    "policy-builder": "Programme Builder",
    "policy-checkout": "UK CMIN Basket",
    #"transport-map": "Transport Map",
}

app.layout = html.Div(
    [

        layout.build_tabs(
            landing_page="policy-builder",
            tabs_dict=page_dict
            ),
    ]
)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=os.environ.get("PORT", 8080))

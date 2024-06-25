#!/usr/bin/env python3
# third party
import dash_core_components as dcc
from dash import html
import dash_bootstrap_components as dbc
import dash


logos = {
    "Cabinet Office": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#005abb",
    },
    "Department for Business, Energy & Industrial Strategy": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#003479",
    },
    "Department for Education": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#003a69",
    },
    "Department for Environment Food & Rural Affairs": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#00a33b",
    },
    "Department for Levelling Up, Housing & Communities": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#099",
    },
    "Department for Transport": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#006c56",
    },
    "Department for Work & Pensions": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#00beb7",
    },
    "Department for Health & Social Care": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#00ad93",
    },
    "Foreign, Commonwealth & Development Office": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#012169",
    },
    "HM Treasury": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#af292e",
    },
    "Home Office": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/ho_crest_27px_x2.png",
        "color": "#9325b2",
    },
    "Ministry of Defence": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/mod_crest_27px_x2.png",
        "color": "#00ad93",
    },
    "Ministry of Justice": {
        "icon": "https://raw.githubusercontent.com/alphagov/govuk_frontend_toolkit/master/images/crests/org_crest_27px_x2.png",
        "color": "#231f20",
    },
}


def logo(dept):

    return html.Div(
        [
            html.Img(
                src=logos[dept]["icon"],
                style={"width": "35px", "left": "2px"},
                draggable="false",
                className="ml-1",
            ),
            dbc.Row(dept, className="ml-1", style={"color": "#000000"}),
        ],
        style={
            "max-width": "15vh",
            "border-left-style": "solid",
            "border-left-color": logos[dept]["color"],
            "border-left-width": "3px",
        },
        className="ml-4 mt-1 mr-2",
    )


def author(prj_lead, dept_lead, last_updated):
    text = f"""
    **Project Lead**: {prj_lead}  
    **Department Lead**: {dept_lead}

    Updated: {last_updated}
    """

    return dcc.Markdown(text)


AQS_definitions = {
    "Pre-assessed": {
        "logo": "/assets/AQS/pre_assessed_badges.svg",
        "color": "#000000",
        "Definition": "Not QA’d or assessed against AQS considerations. Typically for quick estimates, short notes, and comments on other work, and suitable for an early, initial analytical view on an issue.",
    },
    "Locally Assured": {
        "logo": "/assets/AQS/LA_badges.svg",
        "color": "#CD7F32",
        "Definition": "Assessed with reference to AQS considerations within the unit producing the analysis and signed off by Head of Department / SCS1. Typically for work supporting internal decisions, investment in further policy or analytical work.",
    },
    "Departmental QA": {
        "logo": "/assets/AQS/QA_badges.svg",
        "color": "#C0C0C0",
        "Definition": "Quality assured via a departmental review committee or Director of Analysis or delegate. Typically for significant analytical products and work supporting critical policy or operational decisions, including by Minsters.",
    },
    "Externally Reviewed": {
        "logo": "/assets/AQS/ER_badges.svg",
        "color": "#C9AE5D",
        "Definition": "Subject to external review, challenge, and QA. For the most substantial analysis and research.",
    },
}


def aqs_footer(qa_level=None, qa_comments=None):

    if qa_level != None:
        comments = f"Comments: {qa_comments}" if qa_comments != None else ""
        footer = dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=AQS_definitions[qa_level]["logo"],
                            style={"left": "2px"},
                            draggable="false",
                            className="ml-1",
                        ),
                        dbc.Row(
                            qa_level,
                            className="ml-1",
                            style={
                                "color": AQS_definitions[qa_level]["color"],
                                "font-weight": "bold",
                            },
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dcc.Markdown(comments),
                    ],
                    width=6,
                ),
                dcc.Markdown(
                    AQS_definitions[qa_level]["Definition"],
                    className="pl-3 ml-1",
                ),
            ],
            style={
                "max-width": "50vh",
                "border-left-style": "solid",
                "border-left-color": AQS_definitions[qa_level]["color"],
                "border-left-width": "3px",
            },
            className="ml-4 mt-1 mr-2 w-100",
        )

    else:
        footer = html.Div()

    return footer


def footer(dept, prj_lead, dept_lead, last_updated, qa_level=None, qa_comments=None):
    qa_stamp = "" if qa_level == None else "_Analytical Quality Stamp:_"

    return html.Div(
        [
            html.Hr(
                className="mb-2 mr-5",
                style={"background-color": "rgba(106, 106, 106, 0.5)"},
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Markdown("_In collaboration with:_", className="pl-4"),
                            dbc.Row(
                                [
                                    dbc.Col(logo(dept), width=6),
                                    dbc.Col(
                                        html.Div(
                                            author(
                                                prj_lead,
                                                dept_lead,
                                                last_updated,
                                            ),
                                            style={
                                                "bottom": "0px",
                                                "left": "-40px",
                                                "position": "absolute",
                                            },
                                        ),
                                        width=6,
                                    ),
                                ]
                            ),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            dcc.Markdown(qa_stamp, className="pl-4"),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        aqs_footer(qa_level, qa_comments),
                                        width=12,
                                    ),
                                ]
                            ),
                        ],
                        width=8,
                    ),
                ]
            ),
        ],
        className="w-100",
        style={"color": "rgba(106, 106, 106, 0.5)"},
    )


external_js = [
    "https://code.jquery.com/jquery-3.4.1.slim.min.js",
    "https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js",
]


if __name__ == "__main__":
    app = dash.Dash(
        __name__,
        external_scripts=external_js,
        external_stylesheets=[dbc.themes.LUX],
    )
    app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>10DS Policy Tool</title>
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
    app.layout = footer(
        dept="Cabinet Office",
        prj_lead="Lewis",
        dept_lead="Testing",
        last_updated="fill this automatically",
    )
    app.run_server()

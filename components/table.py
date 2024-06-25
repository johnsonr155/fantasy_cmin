from dash import html
import pandas as pd


def create_dashboard_detail_table(df):
    columns, values = df.columns, df.values

    header = [
        html.Tr(
            [
                html.Th(
                    col,
                    style={
                        "text-align": "center",
                        "color": "#000",
                        "font-size": 14,
                        "padding": "5px 5px 5px 5px",
                        "text-transform": "none",
                    },
                )
                for col in columns
            ]
        )
    ]

    rows = [
        html.Tr(
            [
                html.Td(
                    value,
                    style={
                        "padding": "4px 4px 4px 4px",
                        "font-size": "0.75rem",
                        "max-width": "20rem",
                        "overflow": "clip",
                    },
                )
                for value in row
            ]
        )
        for row in values
    ]

    table = [
        html.Thead(header),
        html.Tbody(rows, style={"text-align": "center"}),
    ]

    return table
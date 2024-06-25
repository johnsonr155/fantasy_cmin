# std
import logging

# third party
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from pandas import DataFrame


def validate_figure_traces(figure):
    """
    Check if a figure has traces that have x, y and name keys.
    """

    if figure is not None:
        if "data" not in figure.keys():
            return False

        else:
            for trace in figure["data"]:
                if all(key in trace.keys() for key in ["x", "y", "name"]):
                    return True

    return False


def extract_data_from_traces(figure):
    """
    Extract data from traces in a figure.
    """
    valid_trace = []
    # collect valid traces
    for trace in figure["data"]:
        if all(key in trace.keys() for key in ["x", "y", "name"]):
            trace_df = DataFrame({"x": trace["x"], trace["name"]: trace["y"]})
            valid_trace.append(trace_df)

    # merge valid traces
    if len(valid_trace) > 1:
        output_df = valid_trace[0]
        for trace_df in valid_trace[1:]:
            output_df = output_df.merge(trace_df, on="x", how="outer")

    else:
        output_df = valid_trace[0]

    return output_df


def download_graph_data_button(
    app,
    figure_id: str,
    button_text: str | None = "Download graph data",
) -> html.Div:
    """
    Returns an html.Div containing a button to download data from a dcc.Graph figure.
    Clicking the returned button downloads an excel file of all traces that are named.
    """

    @app.callback(
        Output(f"10ds-graph-download-{figure_id}", "data"),
        Input({"type": "10ds-graph-download-button", "index": figure_id}, "n_clicks"),
        State(figure_id, "figure"),
        prevent_initial_callback=True,
    )
    def download_data_from_figure(n_clicks, figure):
        if n_clicks is None:
            raise PreventUpdate

        if n_clicks > 0:
            if validate_figure_traces(figure):
                output_df = extract_data_from_traces(figure)

            else:
                output_df = DataFrame(
                    f"Unable to extract data from figure {figure_id}. At least one trace needs the name attribute."
                )
                logging.warning(f"Unable to extract data from figure {figure_id}")

            return dcc.send_data_frame(
                output_df.to_excel, f"{figure_id}.xlsx", index=False
            )

    @app.callback(
        Output({"type": "10ds-graph-download-button", "index": figure_id}, "style"),
        Input(figure_id, "figure"),
        prevent_initial_callback=False,
    )
    def check_traces_for_content(figure):
        """
        Check all traces in figure. If none match the criteria, return a button that
        has no styling.
        """

        if not validate_figure_traces(figure):
            return {"display": "none"}

        raise PreventUpdate

    if button_text is None:
        button_component = dmc.ActionIcon(
            DashIconify(icon="mdi:download", color="white"),
            id={"type": "10ds-graph-download-button", "index": figure_id},
            variant="filled",
            color="pink",
        )

    else:
        button_component = dmc.Button(
            children=button_text,
            id={"type": "10ds-graph-download-button", "index": figure_id},
            color="pink",
            rightIcon=DashIconify(icon="mdi:download", color="white", height=20),
            size="sm",
        )

    return html.Div(
        [
            dcc.Download(id=f"10ds-graph-download-{figure_id}"),
            button_component,
        ]
    )

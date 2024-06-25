import logging
import os
from typing import List

from dash import html, Output, Input, callback
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from flask import send_from_directory

from ten_ds_utils.config.dash import DashConfig
from ten_ds_utils.filesystem.s3 import S3Filesystem


BUTTON = dmc.Button(
    "Presentations",
    id="presentations-drawer-button",
    leftIcon=[DashIconify(icon="ph:presentation-chart", width=25)],
    variant="outline",
    color="pink",
)


BUTTON_CONTAINER_STYLE = {
    "width": "100%",
    "display": "flex",
    "flex-direction": "row-reverse",
}


def create_local_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def download_files(fs: S3Filesystem, app_name: str, static_path: str, data_bucket: str):
    logging.info("Downloading presentation files")

    key = f"presentations/{app_name}"
    path = fs.path(data_bucket, key)

    create_local_path(static_path)

    for file in fs.list_objects(path, as_list=True):
        file_name = file.split("/")[-1]
        fs.client.download_file(data_bucket, file, os.path.join(static_path, file_name))

    logging.info("Finished downloading presentation files")


def generate_slides_href(prefix_url: str, file: str, query_string: str):
    return f"{prefix_url}slides/{file}?{query_string}"


def generate_presentation_anchors(
    static_path: str, query_string: str, prefix_url: str
) -> List[html.Div]:
    file_ending = ".html"
    return [
        html.Div(
            [
                dmc.Anchor(
                    file.rstrip(file_ending).title(),
                    href=generate_slides_href(prefix_url, file, query_string),
                    color="pink",
                    target="_blank",
                ),
                html.Div(
                    [
                        dmc.Anchor(
                            DashIconify(icon="ph:presentation-chart", width=25),
                            href=generate_slides_href(prefix_url, file, query_string),
                            color="pink",
                            target="_blank",
                        ),
                        dmc.Anchor(
                            DashIconify(icon="bxs:file-pdf", width=25),
                            href=generate_slides_href(
                                prefix_url,
                                f"download/{file.replace('.html', '.pdf')}",
                                query_string,
                            ),
                            color="pink",
                        ),
                    ],
                    style={
                        "width": "30%",
                        "justify-content": "space-around",
                        "display": "flex",
                    },
                ),
            ],
            style={
                "width": "100%",
                "display": "flex",
                "align-items": "space-between",
                "justify-content": "space-between",
            },
        )
        for file in os.listdir(static_path)
        if file.endswith(file_ending)
    ]


def setup_presentations(conf: DashConfig, prefix_url: str, server):

    if not conf.is_local():
        download_files(
            conf.filesystem(), conf.app_name(), conf.static_path(), conf.data_bucket()
        )

    @server.route(f"{prefix_url}slides/<path:path>")
    def serve_slides(path):
        return send_from_directory(conf.static_path(), path)

    @server.route(f"{prefix_url}slides/download/<path:path>")
    def serve_slides_download(path):
        return send_from_directory(conf.static_path(), path, as_attachment=True)


def render_presentations(
    conf: DashConfig,
    query_string: str,
    prefix_url: str,
    button: dmc.Button = BUTTON,
    button_container_style: dict = BUTTON_CONTAINER_STYLE,
) -> html.Div:

    return html.Div(
        [
            html.Div(
                button,
                style=button_container_style,
            ),
            dmc.Drawer(
                dmc.Stack(
                    generate_presentation_anchors(
                        conf.static_path(), query_string, prefix_url
                    )
                ),
                title="Presentations",
                id="presentations-drawer",
                padding="md",
                position="right",
            ),
        ]
    )


@callback(
    Output("presentations-drawer", "opened"),
    Input("presentations-drawer-button", "n_clicks"),
    prevent_initial_call=True,
)
def open_presenetation_drawer(n_clicks):
    return True

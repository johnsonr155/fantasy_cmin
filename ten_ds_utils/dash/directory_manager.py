# std
import os
import logging
from dataclasses import dataclass, field

# third party
from dash import Input, Output


@dataclass
class DashDirectoryManager:
    _url_objects: dict = field(default_factory=dict)

    def add_url_to_directory(self, id, object):
        id = "/".join(id) if isinstance(id, list) else id
        if id in self._url_objects.keys():
            raise Exception(f"URL {id} already exists.")
        else:
            self._url_objects.update({id: object})
            
    def multi_page_directory_callback(
        self, app, location_component_id, default_page_id, dashboard_layout_id
    ):
        if isinstance(default_page_id, list):
            default_page_id = "/".join(default_page_id)
            
        @app.callback(
            Output(dashboard_layout_id, "children"),
            Input(location_component_id, "pathname"),
        )
        def update_page(pathname):
            # get everything after the last slash in pathname
            # (important bc on deployment pathname looks like: education-delivery/page-id)
            prefix_url = os.environ.get("PREFIX_URL", "/")
            if prefix_url != "/":
                pathname = pathname.replace(prefix_url, "")            
            pathname = pathname.strip("/")

            default_page_layout = self._url_objects[default_page_id]
            return self._url_objects.get(pathname, default_page_layout)

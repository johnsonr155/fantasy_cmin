import os
from datetime import datetime as dt
import json
import logging

from dash.exceptions import PreventUpdate
from dash import html, Output, Input, State
from dash_extensions import EventListener

# Taken from:
# https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility

def check_if_new_log_level_exists(levelName, methodName):
    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present
    """

    if not methodName:
        methodName = levelName.lower()

    # check if logs level already exists
    check_if_new_log_level_exists(levelName, methodName)

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def logging_wrapper(self, children):
    addLoggingLevel("DASH_LOGS", 35)
    logging.getLogger(__name__).setLevel("DASH_LOGS")

    event = {
        "event": "click",
        "props": [
            "srcElement.innerText",
            "srcElement.classList",
        ],
    }

    if not self.conf.is_local():
        @self.app.callback(
            Output("10ds-logs-output", "children"),
            Input("10ds-dash-logger", "event"),
            Input("10ds-dash-logger", "n_events"),
            State("10ds-url", "pathname"),
            State("10ds-url", "href"),
        )
        def log_action(event, n_events, pathname, href):
            if event == None:
                raise PreventUpdate

            logging_package = {
                "level": logging.DASH_LOGS,
                "username": href.split("username=")[-1],
                "app": os.environ.get("PREFIX_URL", "/"),
                "page": pathname,
                "datetime": dt.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "srcElement_innerText": event.get("srcElement.innerText", None),
                "srcElement_classList": [
                    class_name
                    for key, class_name in event.get("srcElement.classList", []).items()
                ],
            }

            logging.dash_logs(json.dumps(logging_package))
            return True

    return EventListener(
        [html.Div(id="10ds-logs-output"), children],
        events=[event],
        logging=False,
        id="10ds-dash-logger",
    )

from dash.html import Iframe, H4


def iframe_layout(url: str) -> Iframe:

    if url is None:
        iframe = H4(
            f"This is a placeholder iframe. It is appearing because there is no url. This is expected behaviour if you are iframing a deployed app locally."
        )
    else:
        iframe = Iframe(
            src=url,
            className="aws-iframe px-3 pt-2",
            style={"border": "0", "width": "100%", "height": "1000px"},
        )
    return iframe

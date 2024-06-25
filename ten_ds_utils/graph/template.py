import plotly.graph_objects as go
import plotly.io as pio


pio.templates["10ds"] = go.layout.Template(
    layout={
        "margin": {"t": 30, "b": 15},
        "annotationdefaults": {"font": {"size": 16}},
        "coloraxis": {
            "colorbar": {
                "outlinewidth": 0,
                "tickcolor": "#000000",
                "ticklen": 6,
                "ticks": "inside",
            }
        },
        "colorscale": {
            "sequential": [[0, "#ffd5e7"], [1, "#c80678"]],
            "sequentialminus": [[0, "#ffd5e7"], [1, "#c80678"]],
        },
        "colorway": [
            "#c80678",
            "#218380",
            "#fbb13c",
            "#3a9cbb",
            "#9a9a9a",
            "#eb8eb7",
            "#72b8b5",
            "#f2cea3",
            "#73d2de",
            "#000000",
        ],
        "font": {"color": "#333333", "family": "Lato", "size": 16},
        "legend": {"font": {"size": 16}, "bgcolor": "rgba(0,0,0,0)"},
        "hoverlabel": {"align": "left", "font_family": "Lato"},
        "hovermode": "closest",
        "paper_bgcolor": "rgba(255,255,255,0)",
        "plot_bgcolor": "rgba(255,255,255,0)",
        "polar": {
            "angularaxis": {
                "gridcolor": "#ffffff",
                "linecolor": "#ffffff",
                "showgrid": True,
                "tickcolor": "#333333",
                "ticks": "outside",
            },
            "bgcolor": "rgb(237,237,237)",
            "radialaxis": {
                "gridcolor": "#ffffff",
                "linecolor": "#ffffff",
                "showgrid": True,
                "tickcolor": "#333333",
                "ticks": "outside",
            },
        },
        "title": {"font": {"size": 24}},
        "xaxis": {
            "automargin": True,
            "gridcolor": "#ffffff",
            "linecolor": "#ffffff",
            "showgrid": True,
            "tickcolor": "#333333",
            "tickfont": {"size": 16},
            "ticks": "outside",
            "title": {"standoff": 15, "font": {"size": 20}},
        },
        "yaxis": {
            "automargin": True,
            "gridcolor": "#e3e3e3",
            "linecolor": "#e3e3e3",
            "showgrid": True,
            "tickcolor": "#333333",
            "tickfont": {"size": 16},
            "ticks": "outside",
            "title": {"standoff": 15, "font": {"size": 20}},
        },
    }
)

pio.templates.default = "10ds"

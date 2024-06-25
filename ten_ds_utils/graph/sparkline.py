# std
from dataclasses import dataclass

# third party
from pandas import Series
import plotly.express as px
import plotly.graph_objects as go

# template
from ten_ds_utils.graph.template import *


@dataclass
class Sparkline:
    x: list | Series
    y: list | Series

    def __post_init__(self):
        if isinstance(self.x, Series):
            self.x = list(self.x)
        if isinstance(self.y, Series):
            self.y = list(self.y)

        self.figure = px.line(x=self.x, y=self.y)
        self.first_point = self.x[0]
        self.last_point = self.x[-1]

    def add_marker(
        self,
        x,
        y,
        color,
        annotation=None,
        font_size=12,
        hovertemplate="<b>%{x}</b>: %{y:.0f}<extra></extra>",
        yshift=0,
        xshift=-5,
        kwargs_for_trace={},
        kwargs_for_annotation={},
    ):
        marker = dict(marker=dict(size=10, color=color))
        marker_kwargs = marker | kwargs_for_trace
        self.figure.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers",
                hovertemplate=hovertemplate,
                **marker_kwargs
            )
        )

        if annotation:
            default_font = dict(font=dict(color=color, size=font_size))
            # Overwrite any fonts from kwargs
            annotation_kwargs = default_font | kwargs_for_annotation

            self.figure.add_annotation(
                x=x,
                y=y,
                xref="x",
                yref="y",
                text=annotation,
                showarrow=False,
                yshift=yshift,
                xshift=xshift,
                xanchor="left",
                **annotation_kwargs
            )

    def add_xaxis_tickvals(self, key_points_on_xaxis=[]):
        ticks_on_axis = [self.first_point] + key_points_on_xaxis + [self.last_point]
        self.figure.update_xaxes(tickvals=ticks_on_axis)

    def define_default_layout(
        self,
        margin,
        show_y_axis,
        hovertemplate="<b>%{x}</b>: %{y:.0f}<extra></extra>",
        **kwargs
    ):
        """Generates standard formatting for sparklines. X-axis is Month - Year"""
        self.figure.update_traces(hovertemplate=hovertemplate)
        self.figure.update_layout(
            showlegend=False,
            yaxis=dict(
                title="",
                showticklabels=show_y_axis,
                showgrid=show_y_axis,
                zeroline=False,
                ticklen=0,
                tickfont=dict(size=12),
            ),
            xaxis=dict(
                title="",
                tickformat="%b %Y",
                ticklen=0,
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=12),
            ),
            margin=margin,
            **kwargs
        )

    def apply_default_settings(
        self,
        color="#c80678",
        key_points_on_xaxis=[],
        font_size=14,
        annotation_end=None,
        annotation_start=None,
        show_y_axis=False,
        xshift_end=5,
        yshift_end=0,
        xshift_start=5,
        yshift_start=0,
        margin={"r": 50, "t": 0, "l": 50, "b": 0, "pad": 0},
    ):
        """Calls all functions within the Sparkline subclass"""
        # Add end waypoint
        self.add_marker(
            x=self.x[-1],
            y=self.y[-1],
            color=color,
            font_size=font_size,
            annotation=annotation_end,
            yshift=yshift_end,
            xshift=xshift_end,
        )

        # Add start waypoint
        self.add_marker(
            x=self.x[0],
            y=self.y[0],
            color=color,
            font_size=font_size,
            annotation=annotation_start,
            yshift=yshift_start,
            xshift=xshift_start,
        )
        self.add_xaxis_tickvals(key_points_on_xaxis=key_points_on_xaxis)
        self.define_default_layout(margin=margin, show_y_axis=show_y_axis)

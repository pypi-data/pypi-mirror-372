from typing import Dict, Any, Literal, Optional, Union
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
import funcnodes as fn
import funcnodes_images as fn_img
from .utils import clone_trace, clone_figure


@fn.NodeDecorator("plotly.make_figure", name="Make Figure")
def make_figure() -> go.Figure:
    """
    Create a simple figure object.

    Parameters
    ----------
    data : List[go.Scatter]
        The data to be plotted.
    layout : Dict[str, Any]
        The layout of the plot.

    Returns
    -------
    go.Figure
        The figure object.
    """

    return go.Figure()


@fn.NodeDecorator(
    "plotly.add_trace",
    name="Add Trace to Figure",
    default_render_options={
        "data": {"src": "new figure"},
    },
    outputs=[{"name": "new figure"}],
)
def add_trace(
    trace: Union[BaseTraceType | go.Figure],
    figure: Optional[go.Figure] = None,
) -> go.Figure:
    """
    Add a trace to a figure object.

    Parameters
    ----------
    figure : go.Figure
        The figure object to add the trace to.
    trace : go.Scatter
        The trace to be added to the figure.

    Returns
    -------
    go.Figure
        The figure object with the added trace.
    """
    # clone the figure object

    if figure is None:
        figure = go.Figure()
    else:
        figure = clone_figure(figure)

    if isinstance(trace, go.Figure):
        trace = trace.data[0]
    trace = clone_trace(trace)

    figure.add_trace(trace)
    return figure


@fn.NodeDecorator(
    "plotly.plot", name="Plot", default_render_options={"data": {"src": "figure"}}
)
def plot(figure: go.Figure) -> go.Figure:
    """
    Plot a figure object.

    Parameters
    ----------
    figure : go.Figure
        The figure object to be plotted.
    """
    return figure


@fn.NodeDecorator(
    "plotly.to_json",
    name="To JSON",
)
def to_json(figure: go.Figure) -> Dict[str, Any]:
    """
    Convert a figure object to a JSON object.
    """
    return figure.to_plotly_json()


@fn.NodeDecorator(
    "plotly.to_img",
    name="To Image",
    default_render_options={"data": {"src": "img"}},
    outputs=[
        {
            "name": "img",
        }
    ],
)
def to_img(
    figure: go.Figure,
    format: Literal["png", "jpeg"] = "png",
    width: int = 700,
    height: int = 500,
) -> fn_img.ImageFormat:
    """
    Convert a figure object to an image.

    Parameters
    ----------
    figure : go.Figure
        The figure object to be converted to an image.
    format : str
        The format of the image. One of "png", "jpeg", or "webp".

    Returns
    -------
    fn_img.ImageFormat
        The image format.
    """
    base_width = 700
    scale = width / base_width

    if format in ["jpeg", "png"]:
        return fn_img.PillowImageFormat.from_bytes(
            figure.to_image(
                format=format, scale=scale, width=base_width, height=height // scale
            )
        )
    raise ValueError(f"Invalid image format: {format}")


NODE_SHELF = fn.Shelf(
    nodes=[make_figure, add_trace, plot, to_json, to_img],
    name="Figures",
    description="Nodes for creating and manipulating plotly figures.",
    subshelves=[],
)

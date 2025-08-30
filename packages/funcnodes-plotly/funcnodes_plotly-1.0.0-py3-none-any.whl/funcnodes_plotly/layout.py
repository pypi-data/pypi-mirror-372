import funcnodes as fn
from .utils import clone_figure
import plotly.graph_objects as go


@fn.NodeDecorator(
    "plotly.label_axis",
    name="Label Axis",
    description="Label the an axis of the plot.",
)
def label_axis(fig: go.Figure, label: str, axis: str = "xaxis") -> go.Figure:
    """
    Label the an axis of the plot.
    """
    fig = clone_figure(fig)
    fig.layout[axis].update(title_text=label)
    return fig


@fn.NodeDecorator(
    "plotly.title",
    name="Title",
    description="Add a title to the plot.",
)
def title(fig: go.Figure, title: str) -> go.Figure:
    """
    Add a title to the plot.
    """
    fig = clone_figure(fig)
    fig.update_layout(title_text=title)
    return fig


NODE_SHELF = fn.Shelf(
    nodes=[
        label_axis,
        title,
    ],
    name="Layout",
    description="Functions for manipulating the layout of the plot.",
    subshelves=[],
)

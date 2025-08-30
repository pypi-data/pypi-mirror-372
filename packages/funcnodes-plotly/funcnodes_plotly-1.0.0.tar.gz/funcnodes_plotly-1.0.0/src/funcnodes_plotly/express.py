import plotly.express as px

from typing import Optional, Literal

import funcnodes as fn

import plotly.graph_objects as go

import pandas as pd
import numpy as np

from .colors import ContinousColorScales, DiscreteColorScales
import plotly.colors as pc

from funcnodes import NoValue


@fn.NodeDecorator(
    "plotly.express.scatter",
    name="Scatter Plot",
    description="Create a scatter plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "color",
                        "size",
                        "symbol",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def scatter(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    size: Optional[str] = None,
    symbol: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a scatter plot.
    """

    return px.scatter(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        size=size,
        symbol=symbol,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.line",
    name="Line Plot",
    description="Create a line plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "color",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def line(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a line plot.
    """
    return px.line(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.bar",
    name="Bar Plot",
    description="Create a bar plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "color",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def bar(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a bar plot.
    """
    return px.bar(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.area",
    name="Area Plot",
    description="Create an area plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "color",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def area(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create an area plot.
    """
    return px.area(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.funnel",
    name="Funnel Plot",
    description="Create a funnel plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "color",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def funnel(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a funnel plot.
    """
    return px.funnel(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.timeline",
    name="Timeline Plot",
    description="Create a timeline plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x_start",
                        "x_end",
                        "y",
                        "color",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def timeline(
    data: pd.DataFrame,
    x_start: str,
    x_end: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a timeline plot. The x_start and x_end columns should be datetime objects.
    """
    return px.timeline(
        data,
        title=node.name if node else None,
        x_start=x_start,
        x_end=x_end,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.pie",
    name="Pie Chart",
    description="Create a pie chart.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "names",
                        "values",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def pie(
    data: pd.DataFrame,
    names: Optional[str] = None,
    values: Optional[str] = None,
    color: Optional[str] = None,
    hole: float = 0,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a pie chart.
    """
    return px.pie(
        data,
        title=node.name if node else None,
        names=names,
        values=values,
        color=color,
        hole=hole,
    )


@fn.NodeDecorator(
    "plotly.express.sunburst",
    name="Sunburst Chart",
    description="Create a sunburst chart.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "names",
                        "values",
                        "parents",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def sunburst(
    data: pd.DataFrame,
    names: str,
    values: str,
    parents: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a sunburst chart.
    """
    fig = px.sunburst(
        data,
        title=node.name if node else None,
        names=names,
        values=values,
        parents=parents,
        color=color,
    )
    fig.update_traces(root_color="lightgrey")
    return fig


@fn.NodeDecorator(
    "plotly.express.treemap",
    name="Treemap",
    description="Create a treemap.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "names",
                        "values",
                        "parents",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def treemap(
    data: pd.DataFrame,
    names: str,
    values: str,
    parents: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a treemap.
    """

    fig = px.treemap(
        data,
        title=node.name if node else None,
        names=names,
        values=values,
        parents=parents,
        color=color,
    )
    fig.update_traces(root_color="lightgrey")
    return fig


@fn.NodeDecorator(
    "plotly.express.icicle",
    name="Icicle Plot",
    description="Create an icicle plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "names",
                        "values",
                        "parents",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def icicle(
    data: pd.DataFrame,
    names: str,
    values: str,
    parents: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create an icicle plot.
    """
    fig = px.icicle(
        data,
        title=node.name if node else None,
        names=names,
        values=values,
        parents=parents,
        color=color,
    )
    fig.update_traces(root_color="lightgrey")
    return fig


@fn.NodeDecorator(
    "plotly.express.funnel_area",
    name="Funnel Area Plot",
    description="Create a funnel area plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "names",
                        "values",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def funnel_area(
    data: pd.DataFrame,
    names: str,
    values: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a funnel area plot.
    """
    return px.funnel_area(
        data,
        title=node.name if node else None,
        names=names,
        values=values,
        color=color,
    )


@fn.NodeDecorator(
    "plotly.express.histogram",
    name="Histogram",
    description="Create a histogram.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "color",
                        "pattern_shape",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def histogram(
    data: pd.DataFrame,
    x: str,
    color: Optional[str] = None,
    pattern_shape: Optional[str] = None,
    barmode: Literal[
        "group",
        "overlay",
        "relative",
    ] = "group",
    marginal: Literal[
        None,
        "rug",
        "box",
        "violin",
    ] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a histogram.
    """
    if marginal not in ["rug", "box", "violin"]:
        marginal = None
    return px.histogram(
        data,
        title=node.name if node else None,
        x=x,
        color=color,
        pattern_shape=pattern_shape,
        barmode=barmode,
        marginal=marginal,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.box",
    name="Box Plot",
    description="Create a box plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "color",
                        "y",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def box(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a box plot.
    """
    return px.box(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.violin",
    name="Violin Plot",
    description="Create a violin plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "color",
                        "y",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def violin(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a violin plot.
    """
    return px.violin(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.strip",
    name="Strip Plot",
    description="Create a strip plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "color",
                        "y",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def strip(
    data: pd.DataFrame,
    x: str,
    y: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a strip plot.
    """
    return px.strip(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.ecdf",
    name="ECDF Plot",
    description="Create an ECDF plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "color",
                        "y",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def ecdf(
    data: pd.DataFrame,
    x: str,
    color: Optional[str] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create an ECDF plot.
    """
    return px.ecdf(
        data,
        title=node.name if node else None,
        x=x,
        color=color,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.density_heatmap",
    name="Density Heatmap",
    description="Create a density heatmap.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "z",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def density_heatmap(
    data: pd.DataFrame,
    x: str,
    y: str,
    z: Optional[str] = None,
    histfunc: Optional[Literal["count", "sum", "avg", "min", "max"]] = None,
    color_continuous_scale: Optional[ContinousColorScales] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    nbinsx: Optional[int] = None,
    nbinsy: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a density heatmap.
    """
    if color_continuous_scale is not None:
        color_continuous_scale = ContinousColorScales.v(color_continuous_scale)
    return px.density_heatmap(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        z=z,
        histfunc=histfunc,
        color_continuous_scale=color_continuous_scale,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
        nbinsx=nbinsx,
        nbinsy=nbinsy,
    )


@fn.NodeDecorator(
    "plotly.express.density_contour",
    name="Density Contour",
    description="Create a density contour plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "z",
                        "facet_row",
                        "facet_col",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def density_contour(
    data: pd.DataFrame,
    x: str,
    y: str,
    z: Optional[str] = None,
    histfunc: Optional[Literal["count", "sum", "avg", "min", "max"]] = None,
    color_discrete_sequence: Optional[DiscreteColorScales] = None,
    facet_row: Optional[str] = None,
    facet_col: Optional[str] = None,
    facet_col_wrap: Optional[int] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a density contour plot.
    """
    if color_discrete_sequence is not None:
        color_discrete_sequence = DiscreteColorScales.v(color_discrete_sequence)
    return px.density_contour(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        z=z,
        histfunc=histfunc,
        color_discrete_sequence=color_discrete_sequence,
        facet_row=facet_row,
        facet_col=facet_col,
        facet_col_wrap=facet_col_wrap,
    )


@fn.NodeDecorator(
    "plotly.express.imshow",
    name="Image Plot",
    description="Create an image plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
)
def imshow(
    data: np.ndarray,
    scale: Optional[ContinousColorScales] = None,
    scale_midpoint: Optional[float] = None,
    value_text: bool = False,
    x: Optional[np.ndarray] = None,
    y: Optional[np.ndarray] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create an image plot.
    """
    color_continuous_scale = None
    if scale is not None:
        color_continuous_scale = ContinousColorScales.v(scale)
    if value_text:
        # show values in scientific notation
        value_text = ".2e"

    return px.imshow(
        data,
        title=node.name if node else None,
        color_continuous_scale=color_continuous_scale,
        color_continuous_midpoint=scale_midpoint,
        text_auto=value_text,
        x=x,
        y=y,
    )


@fn.NodeDecorator(
    "plotly.express.scatter_3d",
    name="3D Scatter Plot",
    description="Create a 3D scatter plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "z",
                        "color",
                        "symbol",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def scatter_3d(
    data: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    color: Optional[str] = None,
    symbol: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a 3D scatter plot.
    """
    return px.scatter_3d(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        z=z,
        color=color,
        symbol=symbol,
    )


@fn.NodeDecorator(
    "plotly.express.line_3d",
    name="3D Line Plot",
    description="Create a 3D line plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                        "y",
                        "z",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def line_3d(
    data: pd.DataFrame,
    x: str,
    y: str,
    z: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a 3D line plot.
    """
    return px.line_3d(
        data,
        title=node.name if node else None,
        x=x,
        y=y,
        z=z,
        color=color,
    )


@fn.NodeDecorator(
    "plotly.express.scatter_matrix",
    name="Scatter Matrix",
    description="Create a scatter matrix.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def scatter_matrix(
    data: pd.DataFrame,
    dimensions: Optional[str] = None,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a scatter matrix.
    """
    if dimensions is not None:
        dimensions_list = [s.strip() for s in dimensions.split(",")]
    else:
        dimensions_list = list(data.columns)

    if color is not None:
        if color in dimensions_list:
            dimensions_list.remove(color)

    return px.scatter_matrix(
        data,
        title=node.name if node else None,
        dimensions=dimensions_list,
        color=color,
    )


@fn.NodeDecorator(
    "plotly.express.parallel_coordinates",
    name="Parallel Coordinates",
    description="Create a parallel coordinates plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def parallel_coordinates(
    data: pd.DataFrame,
    color: Optional[str] = None,
    dimensions: Optional[str] = None,
    color_continuous_scale: Optional[ContinousColorScales] = None,
    color_continuous_midpoint: Optional[float] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a parallel coordinates plot.
    """
    if dimensions is not None:
        dimensions_list = [s.strip() for s in dimensions.split(",")]
    else:
        dimensions_list = list(data.columns)

    if color_continuous_scale is not None:
        color_continuous_scale = ContinousColorScales.v(color_continuous_scale)

    return px.parallel_coordinates(
        data,
        title=node.name if node else None,
        color=color,
        dimensions=dimensions_list,
        color_continuous_scale=color_continuous_scale,
        color_continuous_midpoint=color_continuous_midpoint,
    )


@fn.NodeDecorator(
    "plotly.express.parallel_categories",
    name="Parallel Categories",
    description="Create a parallel categories plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def parallel_categories(
    data: pd.DataFrame,
    dimensions: Optional[str] = None,
    color: Optional[str] = None,
    color_continuous_scale: Optional[ContinousColorScales] = None,
    color_continuous_midpoint: Optional[float] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a parallel categories plot.
    """
    if dimensions is not None:
        dimensions_list = [s.strip() for s in dimensions.split(",")]
    else:
        dimensions_list = list(data.columns)

    if color_continuous_scale is not None:
        color_continuous_scale = ContinousColorScales.v(color_continuous_scale)

    return px.parallel_categories(
        data,
        title=node.name if node else None,
        dimensions=dimensions_list,
        color=color,
        color_continuous_scale=color_continuous_scale,
        color_continuous_midpoint=color_continuous_midpoint,
    )


@fn.NodeDecorator(
    "plotly.express.scatter_polar",
    name="Polar Scatter Plot",
    description="Create a polar scatter plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "r",
                        "theta",
                        "symbol",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def scatter_polar(
    data: pd.DataFrame,
    r: str,
    theta: str,
    color: Optional[str] = None,
    symbol: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a polar scatter plot.
    """
    return px.scatter_polar(
        data,
        title=node.name if node else None,
        r=r,
        theta=theta,
        color=color,
        symbol=symbol,
    )


@fn.NodeDecorator(
    "plotly.express.line_polar",
    name="Polar Line Plot",
    description="Create a polar line plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "r",
                        "theta",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def line_polar(
    data: pd.DataFrame,
    r: str,
    theta: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a polar line plot.
    """
    return px.line_polar(
        data,
        title=node.name if node else None,
        r=r,
        theta=theta,
        color=color,
    )


@fn.NodeDecorator(
    "plotly.express.bar_polar",
    name="Polar Bar Plot",
    description="Create a polar bar plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "r",
                        "theta",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def bar_polar(
    data: pd.DataFrame,
    r: str,
    theta: str,
    color: Optional[str] = None,
    color_discrete_sequence: Optional[DiscreteColorScales] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a polar bar plot.
    """
    if color_discrete_sequence is not None:
        color_discrete_sequence = ContinousColorScales.v(color_discrete_sequence)
    return px.bar_polar(
        data,
        title=node.name if node else None,
        r=r,
        theta=theta,
        color=color,
        color_discrete_sequence=color_discrete_sequence,
    )


@fn.NodeDecorator(
    "plotly.express.scatter_ternary",
    name="Ternary Scatter Plot",
    description="Create a ternary scatter plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "a",
                        "b",
                        "c",
                        "symbol",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def scatter_ternary(
    data: pd.DataFrame,
    a: str,
    b: str,
    c: str,
    color: Optional[str] = None,
    symbol: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a ternary scatter plot.
    """
    return px.scatter_ternary(
        data,
        title=node.name if node else None,
        a=a,
        b=b,
        c=c,
        color=color,
        symbol=symbol,
    )


@fn.NodeDecorator(
    "plotly.express.line_ternary",
    name="Ternary Line Plot",
    description="Create a ternary line plot.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "a",
                        "b",
                        "c",
                        "color",
                    ],
                    lambda x: [NoValue] + list(iter(x)),
                )
            }
        },
    },
)
def line_ternary(
    data: pd.DataFrame,
    a: str,
    b: str,
    c: str,
    color: Optional[str] = None,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a ternary line plot.
    """
    return px.line_ternary(
        data,
        title=node.name if node else None,
        a=a,
        b=b,
        c=c,
        color=color,
    )


@fn.NodeDecorator(
    "plotly.express.multidata",
    name="Plot Multiple Data",
    description="Create a stacked line plots from entries.",
    default_render_options={"data": {"src": "figure"}},
    outputs=[
        {"name": "figure"},
    ],
    default_io_options={
        "data": {
            "on": {
                "after_set_value": fn.decorator.update_other_io(
                    [
                        "x",
                    ],
                    lambda x: ["index"] + list(iter(x)),
                )
            }
        },
    },
)
def plot_multidata(
    data: pd.DataFrame,
    x: str,
    mode: Literal["lines", "markers", "lines+markers"] = "lines",
    stack: bool = False,
    node: Optional[fn.Node] = None,
) -> go.Figure:
    """
    Create a plot from a dictionary where one key is used as the x-axis and the remaining keys are used as
    separate y-axes.

    Args:
        data (dict): A dictionary where keys are trace names and values are lists of data points.
        x (str): The key in the dictionary to be used for the x-axis.
        mode (str): The mode of the plot. One of 'lines', 'markers', or 'lines+markers'.
        stack (bool): Whether to stack the traces on top of each other. this means that the y-axis will be shared.

    Returns:
        None
    """

    def is_plotable(value):
        return (
            isinstance(value, np.ndarray)
            and np.issubdtype(value.dtype, np.number)
            and value.ndim < 2
        )

    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if x == "index":
        x_values = data.index
    else:
        if x not in data:
            raise ValueError(f"The specified x '{x}' is not in the data.")

        # Extract the x values
        x_values = data[x]

    # Create figure
    fig = go.Figure()

    # Define colors for y-axes
    colors = pc.qualitative.Plotly

    # Add traces for each of the remaining keys
    if not stack:
        y_axes = {}
        for i, (key) in enumerate(data):
            values = data[key]
            if key == x:
                continue
            values = np.array(values)
            if is_plotable(values):
                y_axes[f"yaxis{i + 1}"] = {
                    "title": key,
                }

                fig.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=values,
                        name=key,
                        text=values,
                        yaxis=f"y{i + 1}",  # Different y-axis for each trace
                        mode=mode,
                    )
                )

        # Style all the traces
        fig.update_traces(
            hoverinfo="name+x+text",
            showlegend=True,
        )

        n_axes = len(y_axes)
        space = 1 / n_axes

        # Update layout with axes configurations
        fig.update_layout(
            title=node.name if node else None,
            xaxis=dict(
                autorange=True,
                title=x,
            ),
            **{
                axis: dict(
                    anchor="x",
                    autorange=True,
                    domain=[space * i, space * (i + 1)],
                    linecolor=colors[i % len(colors)],
                    side="left",
                    tickfont={"color": colors[i % len(colors)]},
                    title={
                        "text": details["title"],
                        "font": {"color": colors[i % len(colors)]},
                    },
                    zeroline=False,
                )
                for i, (axis, details) in enumerate(y_axes.items())
            },
        )
    else:
        n = 0
        for i, key in enumerate(data):
            values = data[key]
            if key == x:
                continue
            values = np.array(values)
            if is_plotable(values):
                fig.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=values,
                        name=key,
                        text=values,
                        mode=mode,
                        line=dict(color=colors[n % len(colors)]),
                        marker=dict(color=colors[n % len(colors)]),
                    )
                )
                n += 1

        fig.update_traces(
            hoverinfo="name+x+text",
            showlegend=True,
        )

        fig.update_layout(
            xaxis=dict(
                autorange=True,
                title=x,
            ),
            yaxis=dict(
                autorange=True,
                title="Value",
            ),
        )

    return fig


BASIC_SHELF = fn.Shelf(
    nodes=[scatter, line, bar, area, funnel, timeline, plot_multidata],
    name="Basic",
    description="Basic plot types.",
    subshelves=[],
)

PART_OF_WHOLE_SHELF = fn.Shelf(
    nodes=[
        pie,
        sunburst,
        treemap,
        icicle,
        funnel_area,
    ],
    name="Part-of-Whole",
    description="Part-of-whole plot types.",
    subshelves=[],
)

DISTRIBUTION_1D_SHELF = fn.Shelf(
    nodes=[
        histogram,
        box,
        violin,
        strip,
        ecdf,
    ],
    name="1D Distributions",
    description="1D distribution plot types.",
    subshelves=[],
)

DISTRIBUTION_2D_SHELF = fn.Shelf(
    nodes=[
        density_heatmap,
        density_contour,
    ],
    name="2D Distributions",
    description="2D distribution plot types.",
    subshelves=[],
)

MATRIX_IMAGE_SHELF = fn.Shelf(
    nodes=[
        imshow,
    ],
    name="Matrix or Image",
    description="Matrix or image input plot types.",
    subshelves=[],
)

THREE_DIMENSIONAL_SHELF = fn.Shelf(
    nodes=[
        scatter_3d,
        line_3d,
    ],
    name="3-Dimensional",
    description="3D plot types.",
    subshelves=[],
)

MULTIDIMENSIONAL_SHELF = fn.Shelf(
    nodes=[
        scatter_matrix,
        parallel_coordinates,
        parallel_categories,
    ],
    name="Multidimensional",
    description="Multidimensional plot types.",
    subshelves=[],
)

POLAR_SHELF = fn.Shelf(
    nodes=[
        scatter_polar,
        line_polar,
        bar_polar,
    ],
    name="Polar Charts",
    description="Polar plot types.",
    subshelves=[],
)

TERNARY_SHELF = fn.Shelf(
    nodes=[
        scatter_ternary,
        line_ternary,
    ],
    name="Ternary Charts",
    description="Ternary plot types.",
    subshelves=[],
)

NODE_SHELF = fn.Shelf(
    nodes=[],
    name="Plotly Express",
    description="A collection of functions for creating plotly express plots.",
    subshelves=[
        BASIC_SHELF,
        PART_OF_WHOLE_SHELF,
        DISTRIBUTION_1D_SHELF,
        DISTRIBUTION_2D_SHELF,
        MATRIX_IMAGE_SHELF,
        THREE_DIMENSIONAL_SHELF,
        MULTIDIMENSIONAL_SHELF,
        POLAR_SHELF,
        TERNARY_SHELF,
    ],
)

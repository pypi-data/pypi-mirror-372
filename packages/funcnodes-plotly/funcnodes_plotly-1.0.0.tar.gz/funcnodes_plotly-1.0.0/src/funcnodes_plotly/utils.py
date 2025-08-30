from copy import deepcopy
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType


def clone_figure(figure: go.Figure) -> go.Figure:
    """
    Clone a figure object.

    Parameters
    ----------
    figure : go.Figure
        The figure object to be cloned.

    Returns
    -------
    go.Figure
        The cloned figure object.
    """
    return go.Figure(figure)


def clone_trace(trace: BaseTraceType):
    """
    Clone a trace object.

    Parameters
    ----------
    trace : BaseTraceType
        The trace object to be cloned.

    Returns
    -------
    BaseTraceType
        The cloned trace object.
    """
    cloned_trace = deepcopy(trace)
    return cloned_trace

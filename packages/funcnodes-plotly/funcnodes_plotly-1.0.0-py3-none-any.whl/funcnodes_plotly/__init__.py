from typing import Tuple, Any
import plotly.graph_objects as go
from plotly.basedatatypes import BaseTraceType
import funcnodes as fn

from exposedfunctionality.function_parser.types import add_type
from . import plots, layout, figure, express
import os
import json

import funcnodes_pandas  # noqa: F401
import funcnodes_numpy  # noqa: F401

add_type(
    go.Figure,
    "plotly.Figure",
)
add_type(
    BaseTraceType,
    "plotly.Trace",
)

add_type(
    Tuple[int, int, int],
    "color",
)


FUNCNODES_RENDER_OPTIONS: fn.RenderOptions = {
    "typemap": {
        go.Figure: "plotly.Figure",
    },
}


def figureencoder(figure: go.Figure, preview: bool = False) -> Tuple[Any, bool]:
    if isinstance(figure, go.Figure):
        return fn.Encdata(
            data=figure.to_plotly_json(),
            handeled=True,
            done=False,
            continue_preview=False,
        )
    return fn.Encdata(
        data=figure,
        handeled=False,
    )


fn.JSONEncoder.add_encoder(figureencoder)


def figure_byte_encoder(figure: go.Figure, preview) -> fn.BytesEncdata:
    if isinstance(figure, go.Figure):
        return fn.BytesEncdata(
            data=json.dumps(
                fn.JSONEncoder.apply_custom_encoding(figure, preview=preview)
            ).encode("utf-8"),
            handeled=True,
            mime="application/json",
        )
    return fn.BytesEncdata(
        data=figure,
        handeled=False,
    )


fn.ByteEncoder.add_encoder(
    figure_byte_encoder,
    enc_cls=[go.Figure],
)


NODE_SHELF = fn.Shelf(
    nodes=[],
    name="Plotly",
    description="A collection of functions for creating plotly plots.",
    subshelves=[
        plots.NODE_SHELF,
        layout.NODE_SHELF,
        figure.NODE_SHELF,
        express.NODE_SHELF,
    ],
)

REACT_PLUGIN = {
    "module": os.path.join(os.path.dirname(__file__), "react_plugin", "index.iife.js"),
    "css": [os.path.join(os.path.dirname(__file__), "react_plugin", "plugin-custom-renders.css")],
}


__version__ = "1.0.0"

# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class Colorbar(Component):
    """A Colorbar component.
Colorbar Component

A component creating a colorbar with the d3 library.
It accepts a set of stops defining the color gradient, 
a title, and optional labels for specific positions.
It automatically adjusts to the width of its container
and uses a ResizeObserver to handle responsive resizing.
It also supports formatting of labels using d3-format
or native JavaScript formatting.

Dependencies:
- d3: For creating the SVG elements and handling the color gradient.
- Mantine: For styling and layout.

Keyword arguments:

- barHeight (number; default 24):
    Height of the colorbar.

- format (string; optional):
    Optional format function for labels.  If provided, it will be used
    to format the label text.

- labelHeight (number; default 24):
    Height of the labels.

- labels (dict; optional):
    Labels for specific positions on the colorbar.  Keys are positions
    (0 to 1) and values are label texts.

- stops (dict; required):
    The stops to infer the colorbar from.

- title (string; optional):
    The title of the colorbar.

- titleHeight (number; default 24):
    Height of the title."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_maplibre'
    _type = 'Colorbar'


    def __init__(
        self,
        stops: typing.Optional[dict] = None,
        title: typing.Optional[str] = None,
        labels: typing.Optional[dict] = None,
        barHeight: typing.Optional[NumberType] = None,
        titleHeight: typing.Optional[NumberType] = None,
        labelHeight: typing.Optional[NumberType] = None,
        format: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['barHeight', 'format', 'labelHeight', 'labels', 'stops', 'title', 'titleHeight']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['barHeight', 'format', 'labelHeight', 'labels', 'stops', 'title', 'titleHeight']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['stops']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Colorbar, self).__init__(**args)

setattr(Colorbar, "__init__", _explicitize_args(Colorbar.__init__))

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


class DashMaplibre(Component):
    """A DashMaplibre component.
DashMaplibre is a React component for displaying interactive maps using MapLibre GL JS.
It supports custom basemaps, layers, sources, and interactive features like hover popups and click events.
It is designed to be used within a Dash application, allowing for dynamic updates and interactivity.

Dependencies:
- maplibre-gl: For rendering maps and handling layers/sources.
- Colorbar: A custom component for displaying colorbars alongside the map.
- Mantine for styling and layout.

Keyword arguments:

- id (string; optional):
    The unique ID of this component.

- basemap (string | dict; default {  version: 8,  name: "Empty",  sources: {},  layers: []}):
    The basemap style, either as a URL string to a MapLibre style
    JSON,  or as a style JSON object.

- bearing (number; default 0):
    The bearing (rotation) of the map in degrees.

- center (list; default [0, 0]):
    The map center as a [longitude, latitude] array.

- colorbar_map (dict; optional):
    Configuration for the colorbar legend for the map.  Can be a
    single colorbar config object, or a dictionary where keys are zoom
    levels  (as numbers or strings) and values are colorbar config
    objects. The colorbar for the  highest zoom key less than or equal
    to the current zoom will be shown.

    `colorbar_map` is a dict | dict with keys:


- colorbar_risk (dict; optional):
    Configuration for the colorbar legend for risk visualization.

- layers (list; optional):
    The array of MapLibre layer definitions to display on the map.

- max_bounds (list; optional):
    The maximum bounds of the map as [[west, south], [east, north]].

- pitch (number; default 0):
    The pitch (tilt) of the map in degrees.

- sources (dict; optional):
    The sources definition for MapLibre, as an object mapping source
    IDs to source definitions.

- version (string; default ""):
    Optional version string to display in the lower right corner of
    the legend.

- zoom (number; default 2):
    The zoom level of the map."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_maplibre'
    _type = 'DashMaplibre'
    ColorbarMap = TypedDict(
        "ColorbarMap",
            {

        }
    )


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        basemap: typing.Optional[typing.Union[str, dict]] = None,
        center: typing.Optional[typing.Sequence] = None,
        zoom: typing.Optional[NumberType] = None,
        max_bounds: typing.Optional[typing.Sequence] = None,
        bearing: typing.Optional[NumberType] = None,
        pitch: typing.Optional[NumberType] = None,
        sources: typing.Optional[dict] = None,
        layers: typing.Optional[typing.Sequence] = None,
        style: typing.Optional[typing.Any] = None,
        colorbar_map: typing.Optional[typing.Union[dict, "ColorbarMap"]] = None,
        colorbar_risk: typing.Optional[dict] = None,
        version: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'basemap', 'bearing', 'center', 'colorbar_map', 'colorbar_risk', 'layers', 'max_bounds', 'pitch', 'sources', 'style', 'version', 'zoom']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'basemap', 'bearing', 'center', 'colorbar_map', 'colorbar_risk', 'layers', 'max_bounds', 'pitch', 'sources', 'style', 'version', 'zoom']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashMaplibre, self).__init__(**args)

setattr(DashMaplibre, "__init__", _explicitize_args(DashMaplibre.__init__))

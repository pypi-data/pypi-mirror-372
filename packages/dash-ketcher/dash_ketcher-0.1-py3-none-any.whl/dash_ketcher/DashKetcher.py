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


class DashKetcher(Component):
    """A DashKetcher component.
DashKetcher is a Function Component to use Ketcher drawer with Dash.
It outputs the current drawn structure as a SMILES string,
and can also draw the structure corresponding to a provided
SMILES string.

Keyword arguments:

- id (string; required):
    The ID used to identify this component in Dash callbacks.

- editor_height (string; optional):
    The height of the module. Unit is required (eg: %, px).

- editor_id (string; required):
    The title of the Ketch iframe.

- editor_url (string; required):
    The URL of sketcher html webpage.

- editor_width (string; optional):
    The width of the module. Unit is required (eg: %, px).

- input_SMILES (string; optional):
    The SMILES string for which Ketcher should draw the structure.

- output_SMILES (string; optional):
    The computed SMILES string by Ketcher - output only.

- trigger_getSmiles (number; optional):
    When this prop changes, the component runs getSmiles and updates
    output_SMILES."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_ketcher'
    _type = 'DashKetcher'


    def __init__(
        self,
        id: typing.Optional[typing.Union[str, dict]] = None,
        editor_url: typing.Optional[str] = None,
        editor_id: typing.Optional[str] = None,
        editor_height: typing.Optional[str] = None,
        editor_width: typing.Optional[str] = None,
        output_SMILES: typing.Optional[str] = None,
        trigger_getSmiles: typing.Optional[NumberType] = None,
        input_SMILES: typing.Optional[str] = None,
        **kwargs
    ):
        self._prop_names = ['id', 'editor_height', 'editor_id', 'editor_url', 'editor_width', 'input_SMILES', 'output_SMILES', 'trigger_getSmiles']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'editor_height', 'editor_id', 'editor_url', 'editor_width', 'input_SMILES', 'output_SMILES', 'trigger_getSmiles']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['id', 'editor_id', 'editor_url']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(DashKetcher, self).__init__(**args)

setattr(DashKetcher, "__init__", _explicitize_args(DashKetcher.__init__))

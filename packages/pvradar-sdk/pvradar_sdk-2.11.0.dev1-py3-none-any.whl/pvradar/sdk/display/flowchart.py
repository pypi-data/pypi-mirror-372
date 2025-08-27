from typing import Mapping, Optional
import pandas as pd
from pprint import pformat

from ..common.pandas_utils import is_series_or_frame
from ..modeling.profiling.profiling_types import ModelRunStats, ResourceOrigin

from .colors import (
    color_dark_secondary,
    color_light_blue,
    color_dark,
    color_black,
)

_default_theme = {
    # base
    'mainBkg': color_light_blue,  # node background color
    'nodeBorder': color_dark,  # node border color
    'lineColor': color_dark,  # arrow color
    'primaryTextColor': color_black,  # default text color
    'fontSize': '13px',
    #
    # additional theme variables
    'modelNameColor': color_dark_secondary,
    'useCountColor': '#cc5555',
    'executionTimeColor': '#5555cc',
}


def _make_mermaid_theme_mixin(theme_dict: dict = _default_theme) -> str:
    theme_variables = {
        'theme': 'base',
        'themeVariables': {
            'mainBkg': theme_dict.get('mainBkg', _default_theme['mainBkg']),  # node background color
            'nodeBorder': theme_dict.get('nodeBorder', _default_theme['nodeBorder']),  # node border color
            'lineColor': theme_dict.get('lineColor', _default_theme['lineColor']),  # arrow color
            'primaryTextColor': theme_dict.get('primaryTextColor', _default_theme['primaryTextColor']),  # default text color
            'fontSize': theme_dict.get('fontSize', _default_theme['fontSize']),
        },
    }

    # creating the theme like this allows working with dict and add comments
    indented = pformat(theme_variables, indent=2)
    indented = '\n'.join('    ' + line for line in indented.splitlines())
    theme = f'%%{{\n  init: {indented}\n}}%%\n'
    return theme


def origin_tree_to_flowchart(
    origin: ResourceOrigin | pd.Series | pd.DataFrame,
    *,
    model_stats_dict: Optional[dict[str, ModelRunStats]] = None,
    use_theme: bool | str | dict = True,
    show_model_name: bool = True,
    show_use_count: bool = False,
    carry_over_letters: int = 30,
    max_depth: Optional[int] = None,
    show_nested_databases: bool = False,
    orientation: str = 'RL',
) -> str:
    theme = use_theme if isinstance(use_theme, dict) else _default_theme
    if is_series_or_frame(origin):
        origin = origin.attrs['origin']
    assert isinstance(origin, dict)
    id_counter = 1

    nodemap = {}

    # nodes = []
    edges = []

    def add_node(id: str, origin: Mapping, depth=0, edge: Optional[str] = None) -> None:
        nonlocal id_counter

        if 'model_name' not in origin:
            raise ValueError(f"origin must have 'model_name' key: {origin}")
        name = origin.get('resource_type') or origin['model_name']
        if not name:
            raise ValueError(f'unexpected empty origin name: {origin}')
        if len(name) > carry_over_letters:
            name = name[:carry_over_letters] + '\n' + name[carry_over_letters:]
        model_name = origin['model_name']
        params = origin.get('params', {})

        shape = 'default'
        datasource = origin.get('datasource') or params.get('datasource')
        if datasource:
            # node_text += f'\n`datasource: {origin["datasource"]}`'
            shape = 'database'
            if not params.get('datasource'):
                params['datasource'] = datasource

        node_text = f'`**{name}**'
        deps = []
        for key, value in params.items():
            if isinstance(value, dict):
                if 'model_name' in value:
                    id_counter += 1
                    deps.append(value)
            else:
                if isinstance(value, (int, bool)):
                    node_text += f'\n{key}: {value}'
                elif isinstance(value, float):
                    node_text += f'\n{key}: {value:.5g}'
                else:
                    node_text += f'\n{key}: {value}'

        if model_name[:5] == 'hook:':
            shape = 'manual'

        if node_text in nodemap:
            id = nodemap[node_text]['id']
            nodemap[node_text]['times'] += 1
        else:
            # nodes.append(full_text)
            nodemap[node_text] = {
                'id': id,
                'text': node_text,
                'times': 1,
                'resource_type': name,
                'model_name': model_name,
                'shape': shape,
                'label': origin.get('label') or '',
            }

        if edge:
            edge_text = f'{id} --> {edge}'
            if edge_text not in edges:
                edges.append(edge_text)

        if not show_nested_databases and shape == 'database':
            return

        if not max_depth or depth < max_depth:
            for dep in deps:
                id_counter += 1
                new_id = f'node{id_counter}'
                add_node(new_id, dep, depth=depth + 1, edge=id)

    add_node('node1', origin)

    result = f'flowchart {orientation}\n\n'
    for mapping in nodemap.values():
        text = mapping['text']
        if show_model_name:
            displayed_model_name = mapping['model_name']
            if mapping['model_name'][:5] == 'hook:':
                displayed_model_name = mapping['model_name'][5:]
                if mapping['label'] and displayed_model_name == 'hook':
                    displayed_model_name += ': ' + mapping['label']
            model_name_color = theme.get('modelNameColor', _default_theme['modelNameColor'])
            text += f"\n<span style='color:{model_name_color}'>{displayed_model_name}</span>"
        if mapping['times'] > 1 and show_use_count:
            use_count_color = theme.get('useCountColor', _default_theme['useCountColor'])
            text += f"\n<span style='color:{use_count_color}'>used **{mapping['times']}** times</span>"
        if model_stats_dict and mapping['model_name'] in model_stats_dict:
            execution_time_color = theme.get('executionTimeColor', _default_theme['executionTimeColor'])
            text += (
                f"\n<span style='color:{execution_time_color}'>"
                + f'execution time: {model_stats_dict[mapping["model_name"]].sum_execution_time:.3f}s</'
                + '</span>'
            )

        if mapping['shape'] == 'database':
            full_text = f'{mapping["id"]}[("{text}`")]'
        else:
            full_text = f'{mapping["id"]}["{text}`"]'

        if mapping['shape'] == 'manual':
            full_text += '\n' + mapping['id'] + '@{ shape: sl-rect }'

        # result += f'\nclass {mapping["id"]} padded;'
        result += f'{full_text}\n\n'

    for edge in edges:
        result += f'{edge}\n'

    if use_theme:
        if isinstance(use_theme, str):
            theme_str = "%%{init: {'theme': '" + use_theme + "'}}%%"
        elif isinstance(use_theme, dict):
            theme_str = _make_mermaid_theme_mixin(use_theme)
        else:
            theme_str = _make_mermaid_theme_mixin()
        result = theme_str + result

    # result += 'classDef padded padding:100px'
    return result

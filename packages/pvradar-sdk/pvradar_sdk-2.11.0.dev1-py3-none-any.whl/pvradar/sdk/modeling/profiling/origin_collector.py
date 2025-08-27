from datetime import datetime
import numpy as np
from typing import Any
import pandas as pd

from ...common.pandas_utils import is_series_or_frame
from ..model_wrapper import ModelWrapper
from .profiling_types import ResourceOrigin


_ignored_params = ['location', 'interval', 'context']


def _make_recipe_params_from_bound(bound_params: dict[str, Any], resource: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in bound_params.items():
        translated = None
        if is_series_or_frame(value):
            if 'origin' in value.attrs:
                origin: ResourceOrigin = value.attrs['origin'].copy()
            else:
                origin = {'model_name': 'unknown'}
            if origin['model_name'] == 'read_cached_resource':
                translated = {
                    'model_name': 'cache',
                    'resource_type': value.attrs.get('resource_type') or origin.get('resource_type', 'unknown'),
                }
            else:
                origin['resource_type'] = value.attrs.get('resource_type')
                translated = origin
            if 'datasource' in value.attrs:
                translated['datasource'] = value.attrs['datasource']

        elif key in _ignored_params:
            continue
        elif isinstance(value, (int, float, str, bool, pd.Timestamp, datetime)):
            translated = value
        elif isinstance(value, (list, np.ndarray)):
            translated = {'data_type': 'array', 'length': len(value)}
        else:
            translated = {'data_type': 'unknown'}
        result[key] = translated

        if hasattr(resource, 'attrs') and 'datasource' in resource.attrs:
            result['datasource'] = resource.attrs['datasource']
    return result


def _make_resource_origin(model_wrapper: ModelWrapper, bound_params: Any, resource: Any) -> ResourceOrigin:
    clean_params = {}
    for k, v in bound_params.items():
        if k in model_wrapper.params:
            clean_params[k] = v
        elif is_series_or_frame(v) and v.attrs.get('is_nested_origin'):
            clean_params[k] = v

    result: ResourceOrigin = {
        'model_name': model_wrapper.name,
        'params': _make_recipe_params_from_bound(clean_params, resource),
    }
    if is_series_or_frame(resource):
        if 'resource_type' in resource.attrs:
            result['resource_type'] = resource.attrs['resource_type']
        if 'datasource' in resource.attrs:
            result['datasource'] = resource.attrs['datasource']
        if 'label' in resource.attrs:
            result['label'] = resource.attrs['label']
    return result


def origin_collector_output_filter(
    model_wrapper: ModelWrapper,
    bound_params: dict[str, Any],
    result: Any,
) -> Any:
    if is_series_or_frame(result):
        if 'nested_origins' in result.attrs:
            bound_params = bound_params.copy()
            bound_params.update(result.attrs['nested_origins'])
        result.attrs['origin'] = _make_resource_origin(model_wrapper, bound_params, result)
    return result

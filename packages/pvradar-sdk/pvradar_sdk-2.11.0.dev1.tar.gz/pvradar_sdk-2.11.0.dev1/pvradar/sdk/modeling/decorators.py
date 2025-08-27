from typing import Annotated, Any, Optional
import warnings
import pandas as pd
from functools import wraps

from .basics import Audience, Datasource, is_pvradar_resource_type, ParameterConstraint
from .resource_type_helpers import ResourceTypeDescriptor, ResourceTypeClass
from .utils import AggFunctionName, convert_series_unit, resample_series, safe_copy
from ..client.pvradar_resources import PvradarResourceType, unit_for_pvradar_resource_type
from ..common.pandas_utils import (
    SeriesOrFrame,
    is_series_or_frame,
    infer_freq_as_str,
    maybe_adjust_index_freq,
    TimestampAlignment,
    update_attrs_nested,
    freq_to_timedelta,
    infer_freq_and_validate,
)
from .utils import realign, shift_timestamps
from ..modeling.resource_types._list import default_datasources


def _apply_attr(data: Optional[SeriesOrFrame], attr_name: str, attr_value: Any) -> Optional[SeriesOrFrame]:
    if data is None:
        return None
    if not isinstance(data, (pd.Series, pd.DataFrame)):
        raise ValueError(f'Expected pd.Series or pd.DataFrame while applying {attr_name}, got: {type(data)}')
    current_attr = data.attrs.get(attr_name)
    if current_attr == attr_value:
        return data

    new_data = safe_copy(data)
    new_data.attrs[attr_name] = attr_value
    return new_data


def _apply_consistent_attr(
    data: Optional[SeriesOrFrame], attr_name: str, attr_value: Any, do_copy: bool = True
) -> Optional[SeriesOrFrame]:
    if data is None:
        return
    if not isinstance(data, (pd.Series, pd.DataFrame)):
        raise ValueError(
            f'Expected pd.Series or pd.DataFrame while applying {attr_name}, got: {type(data)}. '
            + 'Did you forget scalar=True?'
        )
    current_attr = data.attrs.get(attr_name)

    if current_attr is not None and current_attr != attr_value:
        raise ValueError(
            f'Conflicting attributes, trying to set {attr_name}="{attr_value}" but already set to "{current_attr}"'
        )

    if current_attr == attr_value:
        return data

    new_data = safe_copy(data) if do_copy else data
    new_data.attrs[attr_name] = attr_value
    return new_data


def label(label: str):
    def decorator(func):
        func.label = label

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result = _apply_attr(result, 'label', label)
            return result

        return wrapper

    return decorator


def resource_type(
    resource_type_param: str | ResourceTypeDescriptor | ResourceTypeClass,
    *,
    rename: Annotated[str | bool | None, 'rename series or use resource_type as name'] = None,
    validate: Annotated[bool, 'ensure that another resource_type is not overwritten'] = False,
    scalar: Annotated[bool, 'result will have no metadata, resource_type will only be used for binding'] = False,
):
    """Marks a function as PVRADAR model and adds metadata if applicable"""

    to_unit = None
    set_unit = None
    to_freq = None
    agg = None
    datasource = None

    def decorator(func):
        nonlocal resource_type_param, to_unit, set_unit, to_freq, agg, datasource
        if isinstance(resource_type_param, ResourceTypeClass):
            agg = resource_type_param.standard['agg']
            resource_type_param = resource_type_param.standard['resource_type']
        if isinstance(resource_type_param, ResourceTypeDescriptor):
            if 'to_freq' in resource_type_param:
                to_freq = resource_type_param['to_freq']
            if 'to_unit' in resource_type_param:
                to_unit = resource_type_param['to_unit']
                func.unit = to_unit
            if 'set_unit' in resource_type_param:
                set_unit = resource_type_param['set_unit']
                func.unit = set_unit

            if 'agg' in resource_type_param:
                agg = resource_type_param['agg']
                func.agg = agg
            elif 'agg' in resource_type_param.standard:
                agg = resource_type_param.standard['agg']
                func.agg = agg

            if 'datasource' in resource_type_param:
                datasource = resource_type_param['datasource']
                func.datasource = datasource
            resource_type_param = resource_type_param['resource_type']

        func.resource_type = resource_type_param

        can_have_datasource = (
            resource_type_param == 'any'
            or (datasource is not None)
            or (default_datasources.get(resource_type_param) is not None)  # pyright: ignore [reportArgumentType]
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if is_series_or_frame(result):
                if validate:
                    result = _apply_consistent_attr(result, 'resource_type', resource_type_param)
                else:
                    result = _apply_attr(result, 'resource_type', resource_type_param)

                assert result is not None

                if rename:
                    if not isinstance(result, pd.Series):
                        raise ValueError(
                            f'{resource_type_param}: rename is only supported for pd.Series values, got: {type(result)}'
                        )
                    new_name = result.name if isinstance(rename, str) else resource_type_param
                    if result.name != new_name:
                        result = result.copy()
                        result.name = new_name

                if isinstance(result, pd.Series):
                    if to_freq and ('freq' not in result.attrs or result.attrs['freq'] != to_freq):
                        result = resample_series(result, freq=to_freq)

                    if to_unit:
                        if 'unit' in result.attrs:
                            result = convert_series_unit(result, to_unit=to_unit)
                        else:
                            raise ValueError(
                                f'{resource_type_param}: No unit provided to convert. Did you mean to use set_unit instead?'
                            )

                    if set_unit:
                        result.attrs['unit'] = set_unit

                    if agg:
                        result.attrs['agg'] = agg
                elif isinstance(result, pd.DataFrame):
                    if agg:
                        raise ValueError(f'{resource_type_param}: agg is not supported for DataFrame')
                    if to_unit or set_unit:
                        raise ValueError(f'{resource_type_param}: units are not supported for DataFrame')
                    if to_freq:
                        raise NotImplementedError(f'{resource_type_param}: to_freq is not supported for DataFrame')

                if datasource:
                    result.attrs['datasource'] = datasource

                if 'freq' not in result.attrs and isinstance(result.index, pd.DatetimeIndex) and len(result) > 1:
                    result.attrs['freq'] = infer_freq_as_str(result)

                    # used only here (when freq is unset) to avoid repeated attempts to set freq on data with holes
                    if is_series_or_frame(result):
                        maybe_adjust_index_freq(result)

                if not can_have_datasource and 'datasource' in result.attrs:
                    del result.attrs['datasource']

            return result

        return wrapper

    return decorator


def pvradar_resource_type(
    resource_type_param: PvradarResourceType | ResourceTypeClass,
    *,
    use_std_unit: Annotated[bool, 'Convert to std PVRADAR units for given resource type'] = False,
    rename: Annotated[bool, 'rename series or use resource_type as name'] = False,
    validate: Annotated[bool, 'ensure that another resource_type is not overwritten'] = False,
):
    """DEPRECATED: use standard_resource_type instead"""
    warnings.warn(
        'pvradar_resource_type decorator is deprecated, use standard_resource_type instead', DeprecationWarning, stacklevel=2
    )
    if not isinstance(rename, bool):
        raise ValueError(
            'only bool is supported for rename parameter in pvradar_resource_type, for custom rename use @resource_type'
        )
    return standard_resource_type(
        resource_type_param,
        rename=rename,
        validate=validate,
        use_std_unit=use_std_unit,
    )


def standard_resource_type(
    resource_type_param: PvradarResourceType | ResourceTypeClass,
    *,
    rename: Annotated[bool, 'rename series or use resource_type as name'] = True,
    validate: Annotated[bool, 'ensure that another resource_type/unit is not overwritten'] = False,
    override_unit: Annotated[bool, 'override unit if already present without conversion'] = False,
    use_std_unit: Annotated[bool, 'Convert to std PVRADAR units for given resource type'] = True,
    use_default_freq: Annotated[bool, 'Use site.freq to resample the result'] = False,
):
    """Decorator for pd.Series models, that produce resource in standard PVRADAR unit"""
    agg = None
    unit = None
    if isinstance(resource_type_param, ResourceTypeDescriptor):
        raise ValueError(
            'standard_resource_type only supports standard resource type without any customization. '
            ' If you need it, use resource_type decorator instead'
        )
    if isinstance(resource_type_param, type(ResourceTypeDescriptor)):
        if 'to_unit' in resource_type_param.standard:
            unit = resource_type_param.standard['to_unit']
        if 'agg' in resource_type_param.standard:
            agg = resource_type_param.standard['agg']
        resource_type_param = resource_type_param.standard['resource_type']  # type: ignore
    else:
        if use_std_unit:
            unit = unit_for_pvradar_resource_type(resource_type_param)  # type: ignore

    assert is_pvradar_resource_type(resource_type_param)
    can_have_datasource = resource_type_param == 'any' or default_datasources.get(resource_type_param) is not None  # pyright: ignore [reportArgumentType]

    def decorator(func):
        func.resource_type = resource_type_param
        if unit:
            func.unit = unit

        if use_default_freq:
            func.to_freq = 'default'

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if validate:
                result = _apply_consistent_attr(result, 'resource_type', resource_type_param)
            else:
                result = _apply_attr(result, 'resource_type', resource_type_param)

            if unit:
                if not isinstance(result, pd.Series):
                    raise ValueError(f'automatic unit conversion is only supported for pd.Series values, got: {type(result)}')

                if 'unit' in result.attrs and not override_unit:
                    result = convert_series_unit(result, to_unit=unit)
                else:
                    result.attrs['unit'] = unit

                if agg:
                    result.attrs['agg'] = agg

            if is_series_or_frame(result):
                if 'freq' not in result.attrs and isinstance(result.index, pd.DatetimeIndex) and len(result) > 1:
                    result.attrs['freq'] = infer_freq_as_str(result)
                    # used only here (when freq is unset) to avoid repeated attempts to set freq on data with holes
                    maybe_adjust_index_freq(result)

            if rename and is_series_or_frame(result):
                result.name = resource_type_param

                if not can_have_datasource and 'datasource' in result.attrs:
                    del result.attrs['datasource']

            return result

        return wrapper

    return decorator


def datasource(datasource: Datasource):
    def decorator(func):
        func.datasource = datasource

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # adding datasource even to the origin (without cloning) is OK, as one datasource should never change to another
            result = _apply_consistent_attr(result, 'datasource', datasource, do_copy=False)
            return result

        return wrapper

    return decorator


def to_unit(unit: str):
    def decorator(func):
        func.unit = unit

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, pd.Series):
                if 'unit' in result.attrs:
                    return convert_series_unit(result, from_unit=result.attrs['unit'], to_unit=unit)
                else:
                    raise ValueError('No unit provided to convert from. Use set_unit decorator instead')
            else:
                raise ValueError(f'to_unit is only supported for pd.Series values, got: {type(result)}')

        return wrapper

    return decorator


def set_unit(unit: str):
    def decorator(func):
        func.unit = unit

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result = _apply_attr(result, 'unit', unit)
            return result

        return wrapper

    return decorator


def update_attrs(
    *,
    datasource: Optional[Datasource] = None,
    unit: Optional[str] = None,
    agg: Optional[AggFunctionName] = None,
    freq: Optional[str] = None,
    **kwargs,
):
    def decorator(func):
        if datasource is not None:
            func.datasource = datasource

        if unit is not None:
            func.unit = unit

        @wraps(func)
        def wrapper(*args, **nested_kwargs):
            result = func(*args, **nested_kwargs)

            if result is None:
                return None
            if not is_series_or_frame(result):
                raise ValueError(f'Expected pd.Series or pd.DataFrame while updating attrs, got: {type(result)}')

            attr_patch = kwargs

            # TODO: add validation of well-known attrs
            if datasource is not None:
                attr_patch['datasource'] = datasource
            if unit is not None:
                attr_patch['unit'] = unit
            if agg is not None:
                attr_patch['agg'] = agg
            if freq is not None:
                attr_patch['freq'] = freq

            result = safe_copy(result)
            result.attrs.update(attr_patch)  # type: ignore
            return result

        return wrapper

    return decorator


def audience(org_ids: list[str] | str = [], project_goals: list[str] | str = []):
    def decorator(func):
        nonlocal org_ids, project_goals
        if isinstance(org_ids, str):
            org_ids = [org_ids]
        any_org = '*' in org_ids
        if isinstance(project_goals, str):
            project_goals = [project_goals]
        func.audience = Audience(any_org=any_org, org_ids=org_ids, project_goals=project_goals)
        return func

    return decorator


def synchronize_freq(freq: str):
    def decorator(func):
        func.synchronize_freq = freq
        return func

    return decorator


def optimization_constraints(constraints: list[ParameterConstraint]):
    def decorator(func):
        func.optimization_constraints = constraints
        return func

    return decorator


def realign_and_shift_timestamps():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **nested_kwargs):
            result = func(*args, **nested_kwargs)

            if result is None:
                return None
            if not is_series_or_frame(result):
                raise ValueError(f'Expected pd.Series or pd.DataFrame, got: {type(result)}')

            from_alignment_map: dict[str, TimestampAlignment] = {
                'pvgis-sarah3': 'center',
                'pvgis-era5': 'center',
                'merra2': 'center',
                'era5-land': 'right',
                'era5-global': 'right',
            }

            if 'dataset' not in result.attrs and 'datasource' not in result.attrs:
                raise ValueError('No dataset or datasource attribute found in the result while auto-realigning timestamps')

            from_alignment = None
            if result.attrs.get('dataset') in from_alignment_map:
                from_alignment = from_alignment_map.get(result.attrs['dataset'])
            if not from_alignment and result.attrs.get('datasource'):
                from_alignment = from_alignment_map.get(result.attrs['datasource'])
            if not from_alignment:
                raise ValueError(
                    'Failed to determine from_alignment for '
                    f'datasource {result.attrs.get("datasource")}, '
                    f'dataset {result.attrs.get("dataset")}'
                )

            result = realign(result, to_alignment='center', from_alignment=from_alignment)
            freq = infer_freq_and_validate(result)
            period = freq_to_timedelta(freq)
            shift_map = {'left': -period / 2, 'center': pd.Timedelta(0), 'right': period / 2}
            shift = shift_map.get(from_alignment)
            result = shift_timestamps(result, timedelta=shift)
            result = shift_timestamps(result, to_phase=0)

            update_attrs_nested(result, {'from_alignment': from_alignment})
            return result

        return wrapper

    return decorator

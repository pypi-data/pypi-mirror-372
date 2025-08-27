import re
from typing import Annotated, Any, Literal, Mapping, Optional, TypeGuard, TypeVar, cast, get_args
import numpy as np
import pandas as pd
import pint
from datetime import datetime
from scipy.interpolate import PchipInterpolator

from ..common.pandas_utils import (
    TimestampAlignment,
    crop_by_interval,
    freq_to_timedelta,
    interval_from_series,
    is_series_or_frame,
    infer_freq_and_validate,
    update_attrs_nested,
)
from .basics import AggFunctionName, DataType, Attrs, ModelParamAttrs, SPECIAL_FREQS
from .introspection import attrs_from_annotation
from ..client.pvradar_resources import PvradarResourceType
from .resource_type_helpers import ResourceTypeClass, ResourceTypeDescriptor, attrs_as_descriptor_mapping
from .resource_types._list import standard_mapping
from ..common.pandas_utils import get_offset

ureg = pint.UnitRegistry()
ureg.define('fraction = 100 * percent = 1')


def to_series(values: pd.Series | list[float]) -> pd.Series:
    if isinstance(values, pd.Series):
        return values
    if isinstance(values, list):
        return pd.Series(values)
    raise ValueError(f'Unsupported type while converting to series: {type(values)}')


def convert_series_unit(
    series: pd.Series,
    *,
    to_unit: str,
    from_unit: Optional[str] = None,
) -> pd.Series:
    if from_unit is None:
        from_unit = series.attrs.get('unit', None)
        if from_unit is None:
            raise ValueError(f'from_unit must be provided or series must have a unit attribute on series {series.name}')
    if from_unit == to_unit:
        return series
    try:
        from_unit_object = ureg(from_unit)
        to_unit_object = ureg(to_unit)

        # TODO: we need more logic here
        # this is a workaround to speedup unit conversion
        # but it works bad for units requiring more complex conversion
        # we can built-in special case - as soon as we see suspicious unit (like degF), use the safe and slow way
        # new_series = series.apply(lambda x: (x * from_unit_object).to(to_unit_object).magnitude)
        magnitude = from_unit_object.to(to_unit_object).magnitude
        if from_unit == 'degK' or from_unit == 'degC':
            new_series = series + magnitude - 1
        else:
            new_series = series * magnitude

        new_series.attrs['unit'] = to_unit
        return new_series
    except Exception as e:
        raise ValueError(f'Failed to convert unit for {series.name}: {e}') from e


def get_time_basis(unit: str) -> str | None:
    match = re.search(r'\/(s|m|h|d|day|month|yr|year)$', unit)
    if not match:
        return None
    return match.group(1)


_resample_to_unit: dict[str, str] = {
    'min': 'minute',
    'h': 'hour',
    'H': 'hour',
    '1D': 'day',
    'd': 'day',
    '1d': 'day',
    'M': 'month',
    'ME': 'month',
    'MS': 'month',
    '1M': 'month',
}


def _downsample_resample(series: pd.Series, to_freq: str, agg: str) -> pd.Series:
    offset = pd.tseries.frequencies.to_offset(to_freq)

    # Case A: fixed-width (Tick subclass → safe to convert to Timedelta)
    if isinstance(offset, pd.tseries.offsets.Tick):
        period = pd.Timedelta(offset)  # type: ignore

        if period < pd.Timedelta('1D'):
            # must divide 24h cleanly # TODO: move assertion to resample_series (main function) ... applies to upsampling as well
            assert pd.Timedelta('1D') % period == pd.Timedelta(0), f'Frequency {to_freq} does not divide evenly into 24 hours.'

            # resample with half-period offset: assumes timestamps are center aligned ... does not handle other alignments
            resampler = series.resample(to_freq, origin='start_day', offset=period / 2, label='left', closed='left')
            result = getattr(resampler, agg)()

            # realign to center - shift labels back by half-period
            result = realign(result, from_alignment='left', to_alignment='center')

            # remove last timestamp
            if result.index[-1] > series.index[-1]:
                result = result[:-1]

            return result

        # daily or larger but still fixed (like "24H") → default

    # calendar-based (e.g. 1W, 1M, 1Y) → default resample, result is left aligned
    resampler = series.resample(to_freq)
    result = getattr(resampler, agg)()
    # FIXME: shouldn't be left for ME, YE and alike
    update_attrs_nested(result, {'alignment': 'left'})
    return result


InterpolationMethod = Literal['pchip', 'linear', 'do-not-interpolate']


def _pure_resample_series(
    series: pd.Series,
    scaling: Annotated[float, 'scaling factor of to/from freq, i.e. for day to hour it is 24'],
    to_freq: str,
    agg: AggFunctionName,
    from_period: pd.Timedelta,
    is_upsampling: bool,
    *,
    interval: Optional[pd.Interval] = None,
    interpolate: Annotated[bool, 'uses pchip interpolation by default when upsampling'] = True,
    interpolation_method: InterpolationMethod = 'pchip',
) -> pd.Series:
    inherited_attrs = series.attrs.copy()
    if is_upsampling:
        if interval and interval.right > series.index[-1]:
            adjusted_right = interval.right.floor(to_freq)
            if adjusted_right > series.index[-1]:
                series = pd.concat([series, pd.Series([series.iloc[-1]], index=[adjusted_right])])

        # get period and offset
        to_period = freq_to_timedelta(to_freq)
        to_offset = get_offset(series, period=to_period)

        # Extend series_for_resample to definitely include everything needed
        series_for_resample = pd.concat(
            [
                pd.Series(
                    [series.iloc[0]],  # type: ignore
                    index=[
                        series.index[0] - from_period  # type: ignore
                    ],
                ),
                series,
                pd.Series(
                    [series.iloc[-1]],
                    index=[
                        series.index[-1] + from_period  # type: ignore
                    ],
                ),
            ]
        )

        # upsampling with pandas resample
        if agg == 'sum':
            result = series_for_resample.resample(to_freq).asfreq().ffill()
            result = result / scaling

        elif agg == 'mean':
            if interpolate and interpolation_method != 'do-not-interpolate':
                if isinstance(series, pd.DataFrame):
                    raise ValueError('upsampling interpolation is not supported for DataFrame. Did you mean pd.Series here?')
                result = series_for_resample.resample(to_freq).interpolate(method=interpolation_method)
            else:
                result = series_for_resample.resample(to_freq).asfreq().ffill()
        else:
            raise ValueError(f'Unsupported aggregation for interpolated upsampling: {agg}')

        # realign back to center
        # result.attrs['freq'] = to_freq  # make sure realign function knows new frequency (attrs not yet updated)
        result = realign(result, to_alignment='center', from_alignment='left')

        # shift timestamps to match phase
        result = shift_timestamps(result, to_offset=to_offset)

        # crop by interval
        if not interval:
            interval = interval_from_series(series)
        result = crop_by_interval(result, interval)

    else:
        if agg in ['sum', 'mean', 'min', 'max']:
            result = _downsample_resample(series, to_freq, agg)
        else:
            raise ValueError(f'Unsupported aggregation: {agg}')
    result.attrs = inherited_attrs
    return result


def resample_series(
    series: pd.Series,
    *,
    freq: str,
    agg: Optional[AggFunctionName] = None,
    interval: Optional[pd.Interval] = None,
    adjust_unit: bool = False,
    interpolate: Annotated[Optional[bool], 'use linear interpolation when upsampling'] = None,
    validate: Annotated[bool, 'ensure rate and cumulative resources are not aggregated in a wrong way'] = False,
) -> pd.Series:
    if len(series) <= 1:
        return series
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError('resample_series() only supports series with datetime index')

    current_agg = series.attrs.get('agg', None)
    if agg is None:
        if current_agg is None and 'resource_type' in series.attrs:
            standard = standard_mapping.get(series.attrs['resource_type'])
            if standard and 'agg' in standard:
                current_agg = standard['agg']
        agg = current_agg or 'mean'
    assert agg is not None

    if validate:
        if current_agg == 'mean' and agg == 'sum':
            raise ValueError('Cannot resample from rate to cumulative (mean to sum), use rate_to_cumulative() instead')
        if current_agg == 'sum' and agg == 'mean':
            raise ValueError('Conversion of cumulative to rate (sum to mean) is not supported')

    from_freq = series.attrs.get('freq', None)
    if not from_freq:
        # infer freq from just 2 elements
        if len(series) > 1:
            from_freq = pd.to_timedelta(series.index[1] - series.index[0])
        else:
            raise ValueError('series must have a freq attribute or at least 2 elements to infer freq')
    # delta = step
    from_period = pd.tseries.frequencies.to_offset(from_freq)  # length of period
    if from_period is None:
        raise ValueError(f'Failed to infer as a valid freq {from_freq}')

    to_period = pd.tseries.frequencies.to_offset(freq)
    if to_period is None:
        raise ValueError(f'Target freq invalid {freq}')

    if series.index.freq and to_period == from_period:
        # no need to resample
        return series

    ## below we multiply by 12 to avoid getting 31 scaling because it happens to be a january
    reference_date = pd.Timestamp('1990-01-01')
    delta_from = (reference_date + 12 * from_period) - reference_date
    delta_to = (reference_date + 12 * to_period) - reference_date

    is_upsampling = delta_to < delta_from
    scaling = delta_from / delta_to
    if interpolate is None:
        interpolate = is_upsampling and agg == 'mean'

    result = _pure_resample_series(
        series,
        scaling,
        freq,
        agg,
        from_period,  # type: ignore
        is_upsampling,
        interpolate=interpolate,
        interval=interval,
    )

    if 'unit' in result.attrs and adjust_unit:
        if agg != 'sum':
            raise ValueError('adjust_unit is only supported for sum aggregation')
        denominator = get_time_basis(series.attrs['unit'])
        if denominator:
            replacement = _resample_to_unit.get(freq, freq)
            result.attrs['unit'] = re.sub(r'\/([^/]+)$', f'/{replacement}', result.attrs['unit'])

    result.attrs['agg'] = agg
    result.attrs['freq'] = freq

    return result


def convert_by_attrs(
    value: Any,
    param_attrs: Mapping[str, Any],
    *,
    interval: Optional[pd.Interval] = None,
) -> Any:
    if 'set_unit' in param_attrs and value is not None:
        if isinstance(value, pd.Series):
            value.attrs['unit'] = param_attrs['set_unit']
        else:
            raise ValueError(f'set_unit is only supported for pd.Series values, got: {type(value)}')
    if 'to_unit' in param_attrs and value is not None:
        if isinstance(value, pd.Series):
            if 'unit' in value.attrs:
                value = convert_series_unit(value, to_unit=param_attrs['to_unit'])
            else:
                value.attrs['unit'] = param_attrs['to_unit']
        else:
            raise ValueError(f'to_unit is only supported for pd.Series values, got: {type(value)}')
    if 'to_freq' in param_attrs and value is not None:
        if param_attrs['to_freq'] not in SPECIAL_FREQS:
            if isinstance(value, pd.Series):
                value = resample_series(
                    value,
                    freq=param_attrs['to_freq'],
                    agg=param_attrs['agg'] if 'agg' in param_attrs else None,
                    interval=interval,
                )
            else:
                raise ValueError(f'to_freq is only supported for pd.Series values, got: {type(value)}')
    if 'label' in param_attrs and is_series_or_frame(value):
        value.attrs['label'] = param_attrs['label']
    return value


def datetime_from_dict(d: dict[str, Any], field_name: str) -> datetime | None:
    value = d.get(field_name)
    if value:
        assert isinstance(value, str)
        return datetime.fromisoformat(value)


def auto_attr_series(
    series: pd.Series,
    *,
    series_name_mapping: Optional[dict[Any, str | Annotated[Any, Any]]] = None,
    resource_annotations: Optional[dict[Any, Any]] = None,
    as_name: Optional[str] = None,
    **kwargs,
) -> None:
    """check if series has a known name, and if yes then add attrs unless already present"""
    if series_name_mapping is None:
        series_name_mapping = {}
    if resource_annotations is None:
        resource_annotations = {}
    assert series_name_mapping is not None
    assert resource_annotations is not None

    name = series.name if as_name is None else as_name
    resource_type = name
    if name in series_name_mapping:
        annotation = series_name_mapping[name]
        if isinstance(annotation, str):
            resource_type = series_name_mapping[name]
            annotation = resource_annotations[series_name_mapping[name]]
        attrs = attrs_from_annotation(annotation)
        if attrs and 'param_names' in attrs and 'particle_name' in attrs['param_names']:
            attrs['particle_name'] = name  # type: ignore
    elif name in resource_annotations:
        attrs = attrs_from_annotation(resource_annotations[name])
    else:
        return
    if attrs is not None:
        if 'resource_type' not in series.attrs and 'resource_type' not in attrs:
            series.attrs['resource_type'] = resource_type
        for k, v in attrs.items():
            if k == 'param_names':
                continue
            if k not in series.attrs:
                series.attrs[k] = v
        if 'agg' not in series.attrs:
            series.attrs['agg'] = 'mean'
        for k, v in kwargs.items():
            if k not in series.attrs:
                series.attrs[k] = v


def auto_attr_table(
    series: pd.DataFrame,
    *,
    series_name_mapping: dict[Any, str | Annotated[Any, Any]] = {},
    resource_annotations: dict[Any, Any],
    **kwargs,
) -> None:
    for col in series.columns:
        auto_attr_series(
            series[col],
            series_name_mapping=series_name_mapping,
            resource_annotations=resource_annotations,
            **kwargs,
        )


_rate_to_cumulative: dict[PvradarResourceType, PvradarResourceType] = {
    'rainfall_mass_rate': 'rainfall',
    #
    # FIXME: do we need this?
    'particle_deposition_rate': 'particle_deposition_mass',  # type: ignore
}

_freq_to_unit = {
    'h': 'hour',
    '1h': 'hour',
    'D': 'day',
    '1D': 'day',
    'd': 'day',
    '1d': 'day',
    'M': 'month',
    'MS': 'month',
    'ME': 'month',
    '1M': 'month',
}


def rate_to_cumulative(series: pd.Series, *, freq: Optional[str] = None, resource_type: Optional[str] = None) -> pd.Series:
    to_freq = freq
    to_resource_type = resource_type

    from_resource = series.attrs.get('resource_type')
    if not from_resource:
        raise ValueError('series must have a resource_type attribute')

    from_freq = series.attrs.get('freq', None)
    if not from_freq:
        raise ValueError('series must have a freq attribute')

    from_unit = series.attrs.get('unit', None)
    if not from_unit:
        raise ValueError('series must have a unit attribute')

    if to_resource_type is None:
        to_resource_type = _rate_to_cumulative.get(from_resource)
        if to_resource_type is None:
            raise ValueError(f'No known conversion for resource type: {from_resource}')
    if to_freq is None:
        to_freq = from_freq
    assert to_freq is not None

    if 'agg' in series.attrs and series.attrs['agg'] != 'mean':
        raise ValueError("current agg attribute if {series.attrs['agg']} but only mean is supported")

    from_time_basis = get_time_basis(from_unit)
    if from_time_basis is None:
        raise ValueError(f'Unsupported time basis in unit {from_unit}')
    to_unit = re.sub(rf'\/{from_time_basis}$', '', from_unit)

    if len(series):
        from_quantity = ureg.Quantity(1, from_time_basis)

        from_freq_unit = _freq_to_unit.get(from_freq)
        if not from_freq_unit:
            raise ValueError(f'Unsupported freq {from_freq}')
        from_freq_quantity = ureg.Quantity(1, from_freq_unit)

        normalized_series = series * float(from_freq_quantity.to(from_quantity).magnitude)
        if normalized_series is None:
            raise ValueError('after normalization the series is empty')
        resampled = normalized_series.resample(to_freq).sum()
    else:
        resampled = series.copy()

    resampled.attrs['unit'] = to_unit
    resampled.attrs['resource_type'] = to_resource_type
    resampled.attrs['freq'] = to_freq
    resampled.attrs['agg'] = 'sum'
    return resampled


SeriesOrFrame = TypeVar('SeriesOrFrame', pd.Series, pd.DataFrame)


def copy_df_attrs(from_df: pd.DataFrame, to_df: pd.DataFrame) -> None:
    to_df.attrs = from_df.attrs.copy()
    for col in from_df.columns:
        to_df[col].attrs = from_df[col].attrs.copy()


def safe_copy(df: SeriesOrFrame) -> SeriesOrFrame:
    if isinstance(df, pd.Series):
        return df.copy()
    if isinstance(df, pd.DataFrame):
        result = pd.DataFrame()
        for col in df.columns:
            result[col] = df[col].copy()
        copy_df_attrs(df, result)
        return result  # type: ignore
    raise ValueError(f'Unsupported type for safe_copy: {type(df)}')


def dtype_to_data_type(dtype: Any) -> DataType:
    if str(dtype).startswith('datetime'):
        return 'datetime'
    if dtype == 'float64':
        return 'float'
    if dtype == 'int64':
        return 'int'
    return dtype  # type: ignore


def is_attrs_convertible(subject: Any) -> TypeGuard[Mapping[str, Any] | ResourceTypeClass | ResourceTypeDescriptor]:
    return isinstance(subject, (Mapping, ResourceTypeClass, ResourceTypeDescriptor))


def extract_model_param_attrs(attrs: Any) -> ModelParamAttrs:
    std_keys = [
        'resource_type',
        'datasource',
        'agg',
    ]
    params = {}
    result = {k: attrs[k] for k in std_keys if k in attrs}
    if 'dataset' in attrs:
        params['dataset'] = attrs['dataset']
    if params:
        result['params'] = params
    return cast(ModelParamAttrs, result)


def convert_to_resource(
    resource: SeriesOrFrame, attrs: dict | Attrs | ResourceTypeClass | ResourceTypeDescriptor
) -> SeriesOrFrame:
    new_attrs = attrs_as_descriptor_mapping(attrs)
    resource = convert_by_attrs(safe_copy(resource), new_attrs)
    inherited = ['resource_type', 'agg', 'datasource']
    for k in inherited:
        if k in new_attrs:
            resource.attrs[k] = new_attrs[k]
    return resource


def convert_power_to_energy_Wh(
    power: pd.Series,
    energy_resource_type: str,
) -> pd.Series:
    from_freq = power.attrs.get('freq', None)
    if not from_freq:
        assert isinstance(power.index, pd.DatetimeIndex)
        # infer freq from just 2 elements
        if len(power) > 1:
            from_freq = pd.to_timedelta(power.index[1] - power.index[0])
        else:
            raise ValueError('power must have a freq attribute or at least 2 elements to infer freq')
    if not from_freq:
        raise ValueError('power series must have a freq in series.attrs')

    from_offset = pd.tseries.frequencies.to_offset(from_freq)
    to_freq_offset = pd.tseries.frequencies.to_offset('h')

    assert from_offset is not None
    assert to_freq_offset is not None

    reference_date = pd.Timestamp('1990-01-01')
    delta_from = (reference_date + 12 * from_offset) - reference_date
    delta_to = (reference_date + 12 * to_freq_offset) - reference_date

    scaling = delta_from / delta_to

    energy_attrs = power.attrs.copy()
    energy = power * scaling

    energy_attrs['unit'] = power.attrs['unit'] + 'h'
    energy_attrs['agg'] = 'sum'
    energy_attrs['resource_type'] = energy_resource_type

    energy.attrs = energy_attrs
    return energy


def ensure_consistent_freq(
    series: pd.Series,
    freq: Optional[str] = None,
) -> pd.Series:
    assert isinstance(series.index, pd.DatetimeIndex), 'Series must have a DatetimeIndex'
    freq = infer_freq_and_validate(series) if freq is None else freq
    if series.index.freq == freq:
        return series

    series = resample_series(series, freq=freq, interpolate=True, validate=True)
    return series


def realign(
    resource: SeriesOrFrame,
    *,
    to_alignment: TimestampAlignment,
    from_alignment: Optional[TimestampAlignment] = None,
) -> SeriesOrFrame:
    """
    Realign timestamps between left/center/right by shifting the index only (no interpolation).
    - Period is taken from resource.attrs['freq'] (e.g., 'h' or '1h').
    - If from_alignment is not provided, it's read from resource.attrs['alignment'].
    - Writes the new alignment to result.attrs['alignment'].
    """
    if not isinstance(resource.index, pd.DatetimeIndex):
        raise TypeError('resource must have a DatetimeIndex')

    freq = infer_freq_and_validate(resource)
    period = freq_to_timedelta(freq)

    if from_alignment is None:
        from_alignment = resource.attrs.get('alignment')
        if from_alignment is None:
            raise ValueError("Missing resource.attrs['alignment'] while auto-detecting for realign()")
    assert from_alignment in get_args(TimestampAlignment), f'Invalid from_alignment: {from_alignment}'

    # Offsets relative to the period center
    offset_map: dict[TimestampAlignment, pd.Timedelta] = {
        'left': -period / 2,
        'center': pd.Timedelta(0),
        'right': period / 2,
    }
    delta = offset_map[to_alignment] - offset_map[from_alignment]
    if delta == pd.Timedelta(0):
        update_attrs_nested(resource, {'alignment': to_alignment})
        return resource  # already aligned

    new_index = resource.index + delta

    if isinstance(resource, pd.DataFrame):
        result = safe_copy(resource)
        result.set_index(new_index, inplace=True)
        copy_df_attrs(resource, result)
    elif isinstance(resource, pd.Series):
        result = pd.Series(resource.values, index=new_index, name=resource.name)
        result.attrs = resource.attrs.copy()
    else:
        raise TypeError(f'Unsupported resource type: {type(resource)}')

    update_attrs_nested(result, {'alignment': to_alignment})
    return result  # pyright: ignore[reportReturnType]


def interpolate_with_method(x_new, x, y, interpolation_method: InterpolationMethod = 'pchip'):
    match interpolation_method:
        case 'pchip':
            interpolator = PchipInterpolator(x, y)
            return interpolator(x_new)

        case 'linear':
            return np.interp(x_new, x, y)  # type: ignore

        case 'do-not-interpolate':
            return y
    raise ValueError(f'Unsupported interpolation method: {interpolation_method}')


def shift_timestamps(
    resource: SeriesOrFrame,
    to_offset: Optional[pd.Timedelta] = None,
    to_phase: Optional[float] = None,
    timedelta: Optional[pd.Timedelta] = None,
    interpolation_method: InterpolationMethod = 'pchip',
) -> SeriesOrFrame:
    """
    Shift timestamps in a series to a specific offset, phase, or by a fixed timedelta,
    interpolating values so the data meaning is preserved.

    Parameters
    ----------
    resource : pd.Series
        Time series with a DateTimeIndex and `freq` in attrs.
    to_offset : pd.Timedelta, optional
        Target offset relative to the center of the period.
    to_phase : float, optional
        Target phase (0 - 1) within the period (1 excluded).
    timedelta : pd.Timedelta, optional
        Fixed timedelta to shift timestamps by.
    interpolation_method : {"pchip", "linear"}, default "pchip"
        Interpolation method.

    Returns
    -------
    pd.Series
        New series with shifted timestamps and interpolated values.

    Notes
    -----
    - Exactly one of `to_offset`, `to_phase`, or `timedelta` must be provided.
    - If `to_phase` is given, it is converted internally to `to_offset`.
    - If `to_offset` is given, the necessary `timedelta` is calculated.
    - The resulting series inherits a *copy* of the original attrs.
    """
    assert isinstance(resource.index, pd.DatetimeIndex), 'Index must be a DateTimeIndex'
    assert sum(arg is not None for arg in (to_offset, to_phase, timedelta)) == 1, (
        'Exactly one of to_offset, to_phase, or timedelta must be provided'
    )
    assert len(resource.index) >= 2, 'Index must be at least of length 2'

    freq = infer_freq_and_validate(resource)
    period = freq_to_timedelta(freq)

    if to_phase is not None:
        assert 0 <= to_phase < 1, 'Phase must be in the range [0, 1)'
        to_offset = pd.Timedelta(seconds=to_phase * period.total_seconds())

    if to_offset is not None:
        current_offset = get_offset(resource, period=period)
        timedelta = to_offset - current_offset

    assert timedelta is not None, 'timedelta must be provided if to_offset or to_phase is not'

    new_index = resource.index + timedelta

    x_new = new_index.view(np.int64) / 1e9
    x = resource.index.view(np.int64) / 1e9  # seconds

    if isinstance(resource, pd.Series):
        y = resource.values
        new_values = interpolate_with_method(x_new, x, y, interpolation_method=interpolation_method)
        result = pd.Series(new_values, index=new_index, name=resource.name)
    elif isinstance(resource, pd.DataFrame):
        result = pd.DataFrame(index=new_index, columns=resource.columns)
        for col in resource.columns:
            y = resource[col].values
            new_values = interpolate_with_method(x_new, x, y, interpolation_method=interpolation_method)
            result[col] = new_values
        copy_df_attrs(resource, result)
    else:
        raise TypeError(f'Unsupported resource type: {type(resource)}')

    result.attrs = resource.attrs.copy()
    return result  # type: ignore

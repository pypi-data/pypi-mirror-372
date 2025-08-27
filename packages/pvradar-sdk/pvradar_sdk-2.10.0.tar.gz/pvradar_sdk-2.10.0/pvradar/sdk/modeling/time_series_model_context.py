from datetime import tzinfo
import math
from typing import Any, Mapping, Optional, override
import pandas as pd
from .model_context import ModelContext
from .model_wrapper import ModelWrapper
from ..common.pandas_utils import infer_freq_as_str, interval_to_index, period_str_to_interval
from ..common.exceptions import PvradarSdkError
from .utils import convert_by_attrs, is_series_or_frame, resample_series, attrs_as_descriptor_mapping
from .basics import SPECIAL_FREQS


def validate_timestamp_interval(value: pd.Interval) -> None:
    if (
        not isinstance(value, pd.Interval)
        or not isinstance(value.left, pd.Timestamp)
        or not isinstance(value.right, pd.Timestamp)
    ):
        raise ValueError('must be an Interval with pd.Timestamp endpoints')
    if value.left > value.right:
        raise ValueError('in interval the left endpoint must be less than or equal to right endpoint')


def assert_equal_timezones(
    timezone1: tzinfo | str | None, timezone2: tzinfo | str | None, complaint: str = 'timezone offsets are not equal'
):
    now = pd.Timestamp('now')
    tzinfo1 = now.tz_localize(timezone1).tzinfo
    assert tzinfo1 is not None, f'invalid timezone1 "{timezone1}"'
    tzinfo2 = now.tz_localize(timezone2).tzinfo
    assert tzinfo2 is not None, f'invalid timezone2 "{timezone2}"'
    offset1 = tzinfo1.utcoffset(now)
    offset2 = tzinfo2.utcoffset(now)
    assert offset1 == offset2, f'{complaint}: {offset1} != {offset2}'


def maybe_adjust_tz(value: pd.Interval, default_tz: Any) -> pd.Interval:
    if default_tz is None:
        return value
    if value.left.tzinfo is None:
        new_left = pd.Timestamp(value.left, tz=default_tz)
    else:
        try:
            assert_equal_timezones(value.left.tzinfo, default_tz)
            new_left = value.left
        except AssertionError:
            new_left = value.left.tz_convert(default_tz)
    if value.right.tzinfo is None:
        new_right = pd.Timestamp(value.right, tz=default_tz)
    else:
        try:
            assert_equal_timezones(value.right.tzinfo, default_tz)
            new_right = value.right
        except AssertionError:
            new_right = value.right.tz_convert(default_tz)
    return pd.Interval(new_left, new_right, closed=value.closed)


def interpret_interval(interval: Any) -> pd.Interval:
    """
    interpret incoming parameter as an interval for a context.
    Main conversions: str -> pd.Interval, closed=right -> closed=both
    """
    if isinstance(interval, (int, float)):
        if int(interval) != interval:
            raise ValueError('interval cannot be a float with a non-zero decimal part')
        if interval > 2100 or interval < 1950:
            raise ValueError(f'only years between 1950 and 2100 can be passed as interval, got {interval}')
        interval = str(int(interval))
    if isinstance(interval, str):
        interval = period_str_to_interval(interval)
    if isinstance(interval, pd.Interval) and interval.closed == 'right':
        interval = pd.Interval(interval.left, interval.right, closed='both')
    if not isinstance(interval, pd.Interval):
        raise ValueError(f'type cannot be interpreted as interval: {type(interval)}')
    return interval


def interval_to_str(interval: pd.Interval) -> str:
    return f'{interval.left.strftime("%Y-%m-%d")}..{interval.right.strftime("%Y-%m-%d")}'


class TimeSeriesModelContext(ModelContext):
    def __init__(
        self, *, interval: Optional[Any] = None, default_tz: Any = None, freq: Optional[str] = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._default_tz = default_tz
        if interval:
            self.interval = interval
        self.freq = freq or 'h'

    @property
    def default_tz(self) -> Any:
        return self._default_tz

    @default_tz.setter
    def default_tz(self, value: Any):
        self._default_tz = value
        if 'interval' in self._resources:
            self['interval'] = maybe_adjust_tz(self['interval'], value)

    @property
    def freq(self) -> str:
        return self.resource('freq')

    @freq.setter
    def freq(self, value: str) -> None:
        self['freq'] = value

    @property
    def interval(self) -> pd.Interval:
        return self.resource('interval')

    @interval.setter
    def interval(self, value: Any) -> None:
        self['interval'] = value

    @override
    def on_resource_set(self, key: str, value: Any) -> Any:
        if key == 'interval':
            value = interpret_interval(value)
            validate_timestamp_interval(value)
            value = maybe_adjust_tz(value, self._default_tz)
        if key == 'default_tz':
            raise ValueError(
                'default_tz is a reserved keyword. Did you mean context.default_tz=... instead of context["default_tz"] = ...?'
            )
        return value

    def timestamps(self, freq: str = '1h') -> pd.DatetimeIndex:
        # interval = self.interval
        # if interval.left.tz is None:
        #     interval = maybe_adjust_tz(interval, self.default_tz)
        return interval_to_index(self.interval, freq)

    @override
    def _convert_by_attrs(self, value: Any, param_attrs: Mapping[str, Any]) -> Any:
        to_freq = param_attrs.get('to_freq')
        if to_freq == 'default':
            param_attrs = dict(attrs_as_descriptor_mapping(param_attrs))
            param_attrs['to_freq'] = self.freq
        return convert_by_attrs(value, param_attrs, interval=self['interval'] if 'interval' in self else None)

    @override
    def _process_output(self, model: ModelWrapper, bound_params: dict[str, Any], result: Any) -> Any:
        result = super()._process_output(model, bound_params, result)
        if model.to_freq:
            freq = self.freq if model.to_freq == 'default' else model.to_freq
            result = resample_series(result, freq=freq, interval=self.interval)
        return result

    def _maybe_synchronize_freq(self, result: dict[str, Any], model: ModelWrapper, default_freq: str) -> dict[str, Any]:
        """
        Add-on functionality that alters dictionary of input parameters (result)
        by conditionally synchronizing freq
        """
        # short circuit (performance) if no special freqs are used
        has_special_freq = False
        for param in model.params.values():
            if param.attrs.get('to_freq') in SPECIAL_FREQS:
                has_special_freq = True
                break
        if not has_special_freq:
            return result

        highest_str = ''
        highest_seconds = math.inf
        lowest_str = ''
        lowest_seconds = 0

        all_highest_str = ''
        all_highest_seconds = math.inf
        all_lowest_str = ''
        all_lowest_seconds = 0

        for param in model.params.values():
            if result.get(param.name) is None or not is_series_or_frame(result[param.name]):
                continue
            to_freq = param.attrs.get('to_freq')
            if to_freq == 'default':
                result[param.name] = resample_series(result[param.name], freq=default_freq, interval=self.interval)

        for param in model.params.values():
            if param.name not in result:
                continue
            output = result[param.name]
            if is_series_or_frame(output) and len(output) >= 2:
                try:
                    assumed_freq = output.attrs['freq'] if 'freq' in output.attrs else infer_freq_as_str(output)
                except Exception as e:
                    raise PvradarSdkError(f'Failed to infer freq for pram {param.name} cased by...\n{e}') from e
                if not assumed_freq:
                    continue

                to_freq = param.attrs.get('to_freq')
                is_comparative = to_freq in ('highest', 'lowest')

                sample_range = pd.date_range('2000-01-01', periods=2, freq=assumed_freq)
                sample_seconds = (sample_range[1] - sample_range[0]).total_seconds()

                if sample_seconds > all_lowest_seconds:
                    all_lowest_seconds = sample_seconds
                    all_lowest_str = assumed_freq
                if sample_seconds < all_highest_seconds:
                    all_highest_seconds = sample_seconds
                    all_highest_str = assumed_freq

                if not is_comparative:
                    if sample_seconds > lowest_seconds:
                        lowest_seconds = sample_seconds
                        lowest_str = assumed_freq
                    if sample_seconds < highest_seconds:
                        highest_seconds = sample_seconds
                        highest_str = assumed_freq

        for param in model.params.values():
            if result.get(param.name) is None or not is_series_or_frame(result[param.name]):
                continue
            to_freq = param.attrs.get('to_freq')
            if not to_freq:
                continue
            if to_freq == 'lowest':
                new_freq = lowest_str or all_lowest_str or default_freq
                result[param.name] = resample_series(result[param.name], freq=new_freq, interval=self.interval)
            elif to_freq == 'highest':
                new_freq = highest_str or all_highest_str or default_freq
                result[param.name] = resample_series(result[param.name], freq=new_freq or default_freq, interval=self.interval)

        return result

    @override
    def _process_input(self, model: ModelWrapper, _depth: int = 0, **kwargs) -> dict[str, Any]:
        """additional processing for special freqs (lowest, highest, default)"""

        result = super()._process_input(model, _depth=_depth, **kwargs)
        default_freq = kwargs.get('freq') or result.get('freq', self.freq)
        try:
            return self._maybe_synchronize_freq(result, model, default_freq)
        except Exception as e:
            raise PvradarSdkError(f'Failed synchronizing freq for {model.name}: {e}') from e

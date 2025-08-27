from typing import Any, Optional, TypeVar, override
import pandas as pd
from pvlib.location import Location

from ..common.pandas_utils import interval_to_index
from ..common.pvradar_location import PvradarLocation
from .time_series_model_context import TimeSeriesModelContext

SelfType = TypeVar('SelfType', bound='GeoLocatedModelContext')


class GeoLocatedModelContext(TimeSeriesModelContext):
    def __init__(
        self,
        *,
        location: Optional[Location | tuple | str] = None,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        freq: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(interval=interval, default_tz=default_tz, freq=freq, **kwargs)
        if location:
            self.location = location

    @property
    def location(self) -> Location:
        return self.resource('location')

    @location.setter
    def location(self, value: Optional[Location | tuple | str]) -> None:
        self['location'] = value

    @TimeSeriesModelContext.default_tz.setter
    def default_tz(self, value: Any):
        if value and 'location' in self._resources:
            self.location.tz = value
        TimeSeriesModelContext.default_tz.fset(self, value)  # type: ignore

    @override
    def on_resource_set(self, key: str, value: Any) -> Any:
        value = super().on_resource_set(key, value)
        if key == 'location':
            if isinstance(value, str):
                chunks = value.split(',')
                if len(chunks) != 2:
                    raise ValueError('location string must have 2 elements (latitude, longitude) separated by a comma')
                value = (float(chunks[0]), float(chunks[1]))
            if isinstance(value, tuple):
                if len(value) != 2:
                    raise ValueError('location tuple must have 2 elements (latitude, longitude)')
                value = PvradarLocation(*value)
            if value and not isinstance(value, Location):
                raise ValueError('location must be a (lat, lon) tuple or a instance of pvlib.Location like PvradarLocation')
            if value and value.tz is not None:
                if self._default_tz and self._default_tz != value.tz:
                    value.tz = self._default_tz
                # this setter will already adjust the interval
                self.default_tz = value.tz
        return value

    def _copy_self(self: SelfType, other: SelfType) -> None:
        c = other
        c.models = self.models.copy()
        c.binders = self.binders.copy()
        c._resources = self._resources.copy()
        c.default_tz = self.default_tz
        if 'location' in self._resources:
            c.location = self.location
        if 'interval' in self._resources:
            c.interval = self.interval
        c.mapping_by_resource_types = self.mapping_by_resource_types.copy()
        c.registered_hooks = self.registered_hooks

    @override
    def copy(self: SelfType) -> SelfType:
        c = self.__class__()
        self._copy_self(c)
        return c

    @override
    def timestamps(self, freq: str = '1h') -> pd.DatetimeIndex:
        return interval_to_index(self.interval, freq)

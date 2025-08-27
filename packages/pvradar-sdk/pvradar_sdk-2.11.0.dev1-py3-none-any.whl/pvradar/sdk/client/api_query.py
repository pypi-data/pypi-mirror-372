import json
from typing import Literal, Optional, Self, Any, override
from json import JSONEncoder
from dataclasses import asdict
from httpx._types import QueryParamTypes
from pvlib.location import Location
import pandas as pd

from ..modeling.time_series_model_context import maybe_adjust_tz
from ..common.exceptions import ClientException
from ..common.dd_types import DDPeriod, DDLocation, DDPeriodLike


def _period_to_str(period: DDPeriod) -> str:
    chunks: list[str] = []
    if period.period_type == 'date-range':
        if period.values is None:
            raise ClientException('unexpected period type: date-range without values')
        if len(period.values) != 2:
            raise ClientException(f'unexpected number of values for date-range: {len(period.values)}')
        str0 = str(period.values[0])
        chunks.append(f'{str0[:4]}-{str0[4:6]}-{str0[6:]}')
        str1 = str(period.values[1])
        chunks.append(f'{str1[:4]}-{str1[4:6]}-{str1[6:]}')
    else:
        if period.start is not None:
            chunks.append(str(period.start))
        if period.end is not None:
            chunks.append(str(period.end))
    return '..'.join(chunks)


ProviderType = Literal['dock', 'outlet', 'platform']


class Query(JSONEncoder):
    def __init__(
        self,
        provider: Optional[ProviderType] = None,
        path: str = '',
        period: (int | str | DDPeriod | DDPeriodLike | dict | None) = None,
        location: (str | DDLocation | dict | None) = None,
        params: Optional[dict[str, Any]] = None,
        project_id: Optional[str] = None,
        variant_id: Optional[str] = None,
        tz: Optional[str] = None,
    ):
        self.provider: Optional[ProviderType] = provider
        self.set_path(path)
        self.set_period(period)
        self.set_location(location)
        self.project_id = project_id
        self.variant_id = variant_id
        self._additional_params = params
        self.tz = tz

    def as_dict(self):
        return {
            'path': self.path,
            'location': None if self._location is None else asdict(self._location),
            'period': None if self._period is None else asdict(self._period),
            'additional_params': self._additional_params,
        }

    @override
    def __str__(self):
        return json.dumps(self.as_dict())

    def set_path(self, path: str) -> Self:
        self._path = path
        return self

    @property
    def path(self) -> str:
        return self._path

    def set_location(self, location: str | DDLocation | dict | None) -> Self:
        if isinstance(location, str):
            chunks = location.split(',')
            if len(chunks) != 2:
                raise ClientException(f'unexpected location coordinates: {location}')
            else:
                self._location = DDLocation(lat=float(chunks[0].strip()), lon=float(chunks[1].strip()))
        elif isinstance(location, dict):
            self._location = DDLocation(lat=float(location['lat']), lon=float(location['lon']))
        elif isinstance(location, DDLocation) or location is None:
            self._location = location
        else:
            raise ClientException(f'unexpected type for location: {type(location)}')
        return self

    def set_period(self, period: int | str | DDPeriod | DDPeriodLike | dict | None) -> Self:
        if isinstance(period, int):
            self._period = DDPeriod(period_type='year-range', start=period, end=period)
        elif isinstance(period, str):
            chunks = period.split('..')
            if len(chunks) == 1:
                if len(chunks[0]) == 4:
                    self._period = DDPeriod(period_type='year-range', start=int(chunks[0]), end=int(chunks[0]))
                elif len(chunks[0]) == 10:
                    self._period = DDPeriod(
                        period_type='date-range', values=[int(chunks[0].replace('-', '')), int(chunks[0].replace('-', ''))]
                    )
            else:
                if len(chunks[0]) == 4:
                    self._period = DDPeriod(period_type='year-range', start=int(chunks[0]), end=int(chunks[1]))
                elif len(chunks[0]) == 10:
                    self._period = DDPeriod(
                        period_type='date-range', values=[int(chunks[0].replace('-', '')), int(chunks[1].replace('-', ''))]
                    )
        elif isinstance(period, dict):
            if 'year' in period:
                same_year = int(period['year'])
                self._period = DDPeriod(period_type='year-range', start=same_year, end=same_year)
            elif 'start' in period and 'end' in period:
                self._period = DDPeriod(
                    period_type='year-range',
                    start=int(period['start']),
                    end=int(period['end']),
                )
            else:
                raise ClientException(f'unexpected keys for period: {list(period.keys())}')
        elif isinstance(period, DDPeriod) or period is None:
            self._period = period
        elif isinstance(period, DDPeriodLike):
            self._period = period.to_DDPeriod()
        else:
            raise ClientException(f'unexpected type for period: {type(period)}')
        return self

    def make_query_params(self) -> QueryParamTypes:
        result = {}
        if self._location is not None:
            result['lat'] = str(self._location.lat)
            result['lon'] = str(self._location.lon)
        if self._period is not None:
            result['period'] = _period_to_str(self._period)
        if self._additional_params is not None:
            for key in self._additional_params.keys():
                if self._additional_params[key] is not None:
                    result[key] = self._additional_params[key]
        return result

    def __setitem__(self, key, value):
        if key == 'location':
            self.set_location(value)
        elif key == 'period':
            self.set_period(value)
        else:
            if not self._additional_params:
                self._additional_params = {}
            self._additional_params[key] = value

    def __getitem__(self, key):
        if key == 'location':
            return self._location
        elif key == 'period':
            return self._period
        elif not self._additional_params or key not in self._additional_params:
            return None
        else:
            return self._additional_params[key]

    def copy(self) -> Self:
        cloned = self.__class__(
            path=self._path,
            period=self._period,
            location=self._location,
            params=self._additional_params,
        )
        return cloned

    @classmethod
    def from_site_environment(
        cls,
        location: Location,
        interval: pd.Interval,
        *,
        right_tolerance: Optional[pd.Timedelta] = None,
    ) -> Self:
        interval = maybe_adjust_tz(interval, location.tz)
        if right_tolerance is not None:
            interval = pd.Interval(interval.left, interval.right + right_tolerance, closed=interval.closed)
        return cls(period=_to_period(interval), location=pvlib_location_to_dd_dict(location), tz=location.tz)


def _to_period(interval: pd.Interval) -> str:
    return f'{interval.left.tz_convert("utc").date()}..{interval.right.tz_convert("utc").date()}'


def pvlib_location_to_dd_dict(location: Location) -> dict[str, float]:
    return {
        'lat': location.latitude,
        'lon': location.longitude,
    }

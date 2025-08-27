import re
from typing import override
import warnings
import pandas as pd
from pvlib.location import Location as PvlibLocation
from timezonefinder import TimezoneFinder

from .singleton import Singleton


class TZFinder(TimezoneFinder, Singleton):
    pass


def get_tz_offset(tz) -> float:
    reference_date = pd.Timestamp('2024-01-01T00:00:00')
    zoneinfo = reference_date.tz_localize(tz).tzinfo
    if zoneinfo is None:
        raise ValueError(f'Could not find zoneinfo for TZ {tz}')
    offset = zoneinfo.utcoffset(reference_date)
    if offset is None:
        raise ValueError(f'Failed getting UTC offset for TZ {tz}')
    return offset.total_seconds() / 3600


def get_int_tz_offset(tz) -> int:
    tz_offset = get_tz_offset(tz)
    if int(tz_offset) != tz_offset:
        warnings.warn(f'tz_offset seems to be a float {tz_offset}. Fractional part will be ignored.')
    return int(tz_offset)


def _maybe_translate_tz(tz):
    if isinstance(tz, str):
        # avoid ambiguity of the same TZ
        if tz == 'UTC' or tz == 'Etc/UTC':
            return 'Etc/GMT'
        match = re.match(r'^UTC([+-])(\d\d):', tz)
        if match:
            sign = match.group(1)
            hours = int(match.group(2))
            if hours == 0:
                tz = 'Etc/GMT'
            elif sign == '+':
                tz = f'Etc/GMT-{hours}'
            else:
                tz = f'Etc/GMT+{hours}'
    return tz


class PvradarLocationReprMixin:
    @override
    def __str__(self):
        return (
            f'{self.__class__.__name__}({getattr(self, "latitude")}, {getattr(self, "longitude")}, tz="{getattr(self, "tz")}")'
        )

    @override
    def __repr__(self):
        return self.__str__()


if hasattr(PvlibLocation, 'tz') and isinstance(getattr(PvlibLocation, 'tz'), property):
    # implementation for pvlib >= 0.12.0
    class PvradarLocation(PvlibLocation, PvradarLocationReprMixin):  # pyright: ignore [reportRedeclaration]
        def __init__(self, latitude, longitude, tz=None, altitude=None, name=None):
            tz_offset = 0
            if tz is None:
                detected_tz = TZFinder().timezone_at(lng=longitude, lat=latitude)
                if detected_tz is None:
                    raise ValueError(f'Could not determine timezone for ({latitude}, {longitude})')
                tz_offset = get_int_tz_offset(detected_tz)
            else:
                tz = _maybe_translate_tz(tz)

            super().__init__(
                latitude,
                longitude,
                tz=tz or tz_offset,  # pyright: ignore [reportArgumentType]
                altitude=altitude,
                name=name,
            )

        @property
        @override
        def tz(self):
            return super().tz

        @tz.setter
        def tz(self, tz_):
            tz_ = _maybe_translate_tz(tz_)
            PvlibLocation.tz.fset(self, tz_)  # pyright: ignore
else:
    # implementation for pvlib <= 0.11.2
    class PvradarLocation(PvlibLocation, PvradarLocationReprMixin):  # pyright: ignore [reportRedeclaration]
        def __init__(self, latitude, longitude, tz=None, altitude=None, name=None):
            if tz is None:
                tz = TZFinder().timezone_at(lng=longitude, lat=latitude)
                if tz is None:
                    raise ValueError(f'Could not determine timezone for ({latitude}, {longitude})')
                hour_offset = get_int_tz_offset(tz)
                tz = f'UTC{hour_offset:+03.0f}:00'
            tz = _maybe_translate_tz(tz)

            # here we can't pass tz directly, because UTC+02:00 format was not supported
            super().__init__(latitude, longitude, tz='Etc/GMT', altitude=altitude, name=name)
            self.tz = tz

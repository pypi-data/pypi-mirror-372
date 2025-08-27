from datetime import datetime, timedelta
from typing import Any, Literal, NotRequired, Optional, TypeGuard, TypedDict

import pandas as pd

from ...common.pandas_utils import maybe_adjust_index_freq

VTableResolution = Literal['hour', 'day', 'month', 'year', 'irregular']


class IVTableColumn(TypedDict):
    name: str
    data: list[float]


class IVTable(TypedDict):
    meta: NotRequired[dict[str, Any]]
    columns: list[IVTableColumn]


class ITimedVTable(IVTable):
    timestamps: list[int]
    resolution: VTableResolution


def is_vtable(obj: Any) -> TypeGuard[IVTable]:
    return isinstance(obj, dict) and 'columns' in obj


def is_timed_vtable(obj: Any) -> TypeGuard[ITimedVTable]:
    return is_vtable(obj) and 'timestamps' in obj


def vtable_to_df(vtable: IVTable) -> pd.DataFrame:
    data = {col['name']: col['data'] for col in vtable['columns']}
    df = pd.DataFrame(data)
    if 'meta' in vtable:
        df.attrs = vtable['meta']  # type: ignore
    return df


def maybe_extend_df_with_dates(df: pd.DataFrame) -> pd.DataFrame:
    if 'year' in df and 'dayIndex' in df:
        dates: list[str] = []
        for i in range(len(df)):
            year = df['year'][i]
            start_date = datetime(year, 1, 1)
            target_date = start_date + timedelta(days=int(df['dayIndex'][i]))
            dates.append(target_date.strftime('%Y-%m-%d'))
        df['date'] = pd.to_datetime(dates)
        df.set_index('date', inplace=True)
    return df


def timed_vtable_to_df(timed_vtable: ITimedVTable, set_tz: Optional[str] = None) -> pd.DataFrame:
    df = vtable_to_df(timed_vtable)
    times = pd.to_datetime(timed_vtable['timestamps'], unit='s')
    if set_tz:
        times = times.tz_localize(set_tz)
        df.attrs['tz'] = set_tz
    df.index = times
    maybe_adjust_index_freq(df)
    return df

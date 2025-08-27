from typing import Any, Annotated as A

import pandas as pd
from pvlib.location import Location

from ..api_query import Query
from ..client import PvradarClient
from ..pvradar_resources import SeriesConfigAttrs as S
from ...modeling.decorators import datasource, standard_resource_type
from ...modeling.resource_types._list import standard_mapping
from ...modeling.utils import auto_attr_table
from ...modeling import R
from ...modeling.utils import resample_series

aemet_grid_series_name_mapping: dict[str, str | A[Any, Any]] = {
    # originally the unit is kg/m^2 but assuming water density of 1000 kg/m^3 it's equivalent to mm
    'prec': A[pd.Series, S(resource_type='rainfall', unit='mm', agg='sum', freq='D')],
}


def _remove_hours_inplace(df: pd.DataFrame) -> None:
    if not len(df):
        return
    sample: pd.Timestamp = df.index[0]
    if sample.hour != 0:
        df.index = df.index - pd.Timedelta(hours=sample.hour)


def _auto_attr_table(df: pd.DataFrame, **kwargs) -> None:
    if df is None:
        return
    auto_attr_table(
        df,
        series_name_mapping=aemet_grid_series_name_mapping,
        resource_annotations=standard_mapping,
        **kwargs,
    )
    for name in df:
        df[name].attrs['datasource'] = 'aemet-grid'


@standard_resource_type(R.aemet_grid_table)
@datasource('aemet-grid')
def aemet_grid_table(
    *,
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path('datasources/aemet-grid/raw/daily/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    _remove_hours_inplace(result)
    _auto_attr_table(result)
    return result


@standard_resource_type(R.total_precipitation, use_default_freq=True)
@datasource('aemet-grid')
def aemet_total_precipitation(
    *,
    aemet_grid_table: A[pd.DataFrame, R.aemet_grid_table],
) -> pd.Series:
    result = aemet_grid_table['prec']
    return result


@standard_resource_type(R.rainfall, use_default_freq=True)
@datasource('aemet-grid')
def aemet_grid_rainfall(
    *,
    aemet_total_precipitation: A[pd.Series, R.total_precipitation(datasource='aemet-grid')],
) -> pd.Series:
    return aemet_total_precipitation


@standard_resource_type(R.rainfall_rate, use_default_freq=True)
@datasource('aemet-grid')
def aemet_grid_rainfall_rate(
    *,
    aemet_rainfall: A[pd.Series, R.rainfall(datasource='aemet-grid')],
) -> pd.Series:
    result = resample_series(aemet_rainfall, freq='h', adjust_unit=False)
    result.attrs['unit'] = 'mm/h'
    result.attrs['agg'] = 'mean'
    return result

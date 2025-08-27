from typing import Any, Annotated as A, Optional
import pandas as pd
from pydantic import Field

from ...common.exceptions import DataUnavailableError
from .pvgis_client import PvgisClient, PvgisSeriescalcParams, PvgisDatabase, pvgis_csv_to_pandas
from ...common.pandas_utils import crop_by_interval
from pvlib.location import Location
from ...modeling.decorators import datasource, realign_and_shift_timestamps, standard_resource_type
from ...modeling.utils import auto_attr_table
from ...modeling import R
from ..pvradar_resources import SeriesAttrs, SeriesConfigAttrs as S
from ...modeling.resource_types._list import standard_mapping


pvgis_series_name_mapping: dict[str, str | A[Any, SeriesAttrs]] = {
    'G(i)': A[pd.Series, S(resource_type='global_horizontal_irradiance', unit='W/m^2', agg='mean', freq='1h')],
    'T2m': A[pd.Series, S(resource_type='air_temperature', unit='degC', agg='mean', freq='1h')],
    'WS10m': A[pd.Series, S(resource_type='wind_speed', unit='m/s', agg='mean', freq='1h')],
}


def _auto_attr_table(df: pd.DataFrame, **kwargs) -> None:
    if df is None:
        return
    auto_attr_table(
        df,
        series_name_mapping=pvgis_series_name_mapping,
        resource_annotations=standard_mapping,
        **kwargs,
    )
    for name in df:
        df[name].attrs['datasource'] = 'pvgis'


# ----------------------------------------------------
# PVGIS tables


@realign_and_shift_timestamps()
@standard_resource_type(R.pvgis_seriescalc_table)
@datasource('pvgis')
def pvgis_seriescalc_table(
    *,
    location: A[Location, Field()],
    interval: A[pd.Interval, Field()],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
    tz: Optional[str] = None,
) -> pd.DataFrame:
    do_bfill = False
    query: PvgisSeriescalcParams = {
        'lon': location.longitude,
        'lat': location.latitude,
        'startyear': interval.left.tz_convert('utc').year,
        'endyear': interval.right.tz_convert('utc').year,
    }

    if query['startyear'] < 2005:
        if interval.left > pd.Timestamp('2005-01-01T00:00:00+05:00'):
            do_bfill = True
            query['startyear'] = 2005
        else:
            raise ValueError('PVRADAR does not provide PVGIS data prior to 2004-12-31 20:00:00 UTC')
    if dataset is not None:
        query['raddatabase'] = dataset.upper()  # pyright: ignore [reportGeneralTypeIssues]
    response = PvgisClient.instance().get_seriescalc(query)
    result = pvgis_csv_to_pandas(response, tz=tz if tz is not None else location.tz)
    returned_pvgis_database = result.attrs.get('dataset')
    result = crop_by_interval(result, interval)
    if not len(result):
        where = 'PVGIS seriescalc tool'
        if 'raddatabase' in query:
            where += f' (raddatabase: {query["raddatabase"]})'
        raise DataUnavailableError(interval=interval, where=where)

    # this is a workaround making year 2005 available in European time zones
    # by backfilling a few hours prior to 2005-01-01 00:00:00 UTC
    if do_bfill and len(result):
        index = pd.date_range(interval.left, result.index[-1], freq='h')
        original = result
        result = result.reindex(index)
        result = result.bfill()
        # workaround for bug in pandas overwriting attrs
        for column in result.columns:
            result[column].attrs = original[column].attrs

    _auto_attr_table(result)
    if returned_pvgis_database is not None:
        returned_dataset = returned_pvgis_database.lower()
        result.attrs['dataset'] = returned_dataset
        for name in result:
            result[name].attrs['dataset'] = returned_dataset
    return result


# ----------------------------------------------------
# PVGIS series (alphabetical order)
# here and below the unused 'dataset' parameter is used for automatic validation


@standard_resource_type(R.air_temperature, use_default_freq=True)
@datasource('pvgis')
def pvgis_air_temperature(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    return pvgis_seriescalc_table['T2m']


@standard_resource_type(R.global_horizontal_irradiance, use_default_freq=True)
@datasource('pvgis')
def pvgis_global_horizontal_irradiance(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    result = pvgis_seriescalc_table['G(i)']
    # result = resample_series(result, freq=freq, interval=interval)
    return result


@standard_resource_type(R.wind_speed, use_default_freq=True)
@datasource('pvgis')
def pvgis_wind_speed(
    *,
    pvgis_seriescalc_table: A[pd.DataFrame, R.pvgis_seriescalc_table],
    dataset: A[Optional[PvgisDatabase], Field()] = None,
) -> pd.Series:
    return pvgis_seriescalc_table['WS10m']

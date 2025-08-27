from typing import Annotated as A

import pandas as pd
from pvlib.location import Location
from pydantic import Field as F

from ..api_query import Query
from ..client import PvradarClient
from ...common.exceptions import DataUnavailableError
from ...common.pandas_utils import crop_by_interval
from ...common.settings import SdkSettings
from ...modeling import R
from ...modeling.base_model_context import BaseModelContext
from ...modeling.decorators import datasource, standard_resource_type


@standard_resource_type(R.meteo_station_table)
@datasource('inmet')
def inmet_meteo_station_table(
    *,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    # resource_type: A[Optional[PvradarResourceType], F()] = None,
) -> pd.DataFrame:
    query = Query.from_site_environment(location=location, interval=interval)
    query['sensor'] = 'rainfall'
    query.set_path('datasources/inmet/stations')
    df = PvradarClient.instance().get_df(query)
    df.set_index('station_id', inplace=True)
    return df


@standard_resource_type(R.rainfall)
@datasource('inmet')
def inmet_rainfall(
    *,
    context: BaseModelContext,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    station_id: A[str | None, F()] = None,
) -> pd.Series:
    station_table = None
    if station_id is None:
        station_table = context.resource(R.meteo_station_table(datasource='inmet'))
        if not len(station_table):
            raise DataUnavailableError(interval=interval, where='INMET station table')
        station_id = station_table.index[0]
    assert station_id is not None

    query = Query.from_site_environment(location, interval)
    query['sensor'] = 'rainfall'
    query['station_id'] = station_id
    query.set_path('datasources/inmet/data')

    table = PvradarClient.instance().get_df(query)
    if not len(table):
        raise DataUnavailableError(interval=interval, where='INMET station ' + station_id)
    if location.tz != 'Etc/GMT':
        assert isinstance(table.index, pd.DatetimeIndex)
        table.index = table.index.tz_convert(None).tz_localize(location.tz)
    table = crop_by_interval(table, interval)
    series = table['rainfall']

    series.attrs = {  # type: ignore
        'unit': 'mm',
        'agg': 'sum',
        'station_id': station_id,
        'freq': 'h',
        'datasource': 'inmet',
    }
    settings = SdkSettings.instance()
    if settings.collect_api_metadata:
        series.attrs['api_call'] = table.attrs.get('api_call') if isinstance(table, pd.DataFrame) else {}  # pyright: ignore [reportArgumentType]

    if station_table is not None and 'origin' in station_table.attrs:
        station_table.attrs['is_nested_origin'] = True
        series.attrs['nested_origins'] = {'meteo_table': station_table}

    return series

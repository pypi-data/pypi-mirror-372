from typing import Annotated as A, Optional
import pandas as pd
from pydantic import Field as F
from pvlib.location import Location

from ...common.exceptions import DataUnavailableError
from ...common.pandas_utils import crop_by_interval
from ..api_query import Query, pvlib_location_to_dd_dict
from ..client import PvradarClient
from ...modeling.basics import PvradarResourceType
from ...modeling.base_model_context import BaseModelContext
from ...modeling.decorators import datasource, standard_resource_type
from ...modeling import R
from ...modeling.utils import rate_to_cumulative
from ...common.settings import SdkSettings


def _dd_query_from_site_environment(*, location: Location, interval: pd.Interval) -> Query:
    location_dict = pvlib_location_to_dd_dict(location)
    period = f'{interval.left.year}..{interval.right.year}'
    query = Query(location=location_dict, period=period, tz=location.tz)
    return query


@standard_resource_type(R.meteo_station_table)
@datasource('noaa')
def noaa_meteo_station_table(
    *,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    resource_types: A[Optional[list[PvradarResourceType]], F()] = None,
    noaa_database: A[str, F()] = 'GHCND',
) -> pd.DataFrame:
    if resource_types is None:
        resource_types = ['rainfall']
    for resource_type in resource_types:
        if resource_type not in ['rainfall']:
            raise ValueError('NOAA datasource for now supports only rainfall for meteo stations')

    query = _dd_query_from_site_environment(location=location, interval=interval)
    query['signal_names'] = 'precip_rate_total'
    query.set_path('dd-proxy/signals/available/csv')

    raw = PvradarClient.instance().get_df(query)

    if len(raw):
        processed = pd.DataFrame(
            {
                'datasource': 'noaa',
                'station_id': raw['station_id'],
                'latitude': raw['lat'],
                'longitude': raw['lon'],
                'start_date': pd.to_datetime(raw['start']),
                'end_date': pd.to_datetime(raw['end']),
                'coverage': raw['coverage'],
                'completeness': raw['completeness'],
                'distance': raw['distance'],
                'score': raw['score'],
            }
        )
    else:
        processed = pd.DataFrame(
            {
                'datasource': [],
                'station_id': [],
                'latitude': [],
                'longitude': [],
                'start_date': [],
                'end_date': [],
                'coverage': [],
                'completeness': [],
                'distance': [],
                'score': [],
            }
        )
    processed.attrs = raw.attrs

    return processed


@standard_resource_type(R.rainfall_rate, use_default_freq=True)
@datasource('noaa')
def noaa_rainfall_rate(
    *,
    context: BaseModelContext,
    location: A[Location, F()],
    interval: A[pd.Interval, F()],
    station_location: A[Optional[Location], F()] = None,
    station_id: A[str, F()] = '',
) -> pd.Series:
    table = None
    try:
        if station_location is None:
            table = context.resource('meteo_station_table', datasource='noaa', location=location, interval=interval)
            if not len(table):
                raise DataUnavailableError(interval=interval, where='NOAA station table')
            if station_id == '':
                station_id = table.iloc[0]['station_id']
            try:
                index = list(table['station_id']).index(station_id)
            except ValueError:
                raise ValueError(f'NOAA station {station_id} not found')
            station_location = Location(
                latitude=table['latitude'].iloc[index],
                longitude=table['longitude'].iloc[index],
            )
            station_location.tz = location.tz

        query = _dd_query_from_site_environment(location=station_location, interval=interval)
        query['signal_names'] = 'precip_rate_total'
        query.set_path('dd-proxy/signals/table/csv')
        query.tz = 'UTC'

        table = PvradarClient.instance().get_df(query)
        if not len(table):
            raise DataUnavailableError(interval=interval, where='NOAA station ' + station_id)
        if location.tz != 'Etc/GMT':
            assert isinstance(table.index, pd.DatetimeIndex)
            table.index = table.index.tz_convert(None).tz_localize(location.tz)
        table = crop_by_interval(table, interval)
        series = table['precip']
        series = series / 24  # unit conversion: mm/day -> mm/h
    except ValueError:
        series = pd.Series([])
    series.attrs = {  # type: ignore
        'unit': 'mm/h',
        'agg': 'mean',
        'station_id': station_id,
        'freq': 'D',
        'datasource': 'noaa',
    }
    settings = SdkSettings.instance()
    if settings.collect_api_metadata:
        series.attrs['api_call'] = table.attrs.get('api_call') if isinstance(table, pd.DataFrame) else {}  # pyright: ignore [reportArgumentType]
    return series


@standard_resource_type(R.rainfall, use_default_freq=True)
@datasource('noaa')
def noaa_rainfall(
    *,
    rainfall_rate: A[pd.Series, R.rainfall_rate(datasource='noaa')],
    #
    # present here as a reminder for possible params
    station_location: A[Optional[Location], F()] = None,
    station_id: A[str, F()] = '',
) -> pd.Series:
    return rate_to_cumulative(rainfall_rate, resource_type='rainfall')


@standard_resource_type(R.total_precipitation, use_default_freq=True)
@datasource('noaa')
def noaa_total_precipitation(
    *,
    noaa_total_precipitation: A[pd.Series, R.rainfall(datasource='noaa')],
    #
    # present here as a reminder for possible params
    station_location: A[Optional[Location], F()] = None,
    station_id: A[str, F()] = '',
) -> pd.Series:
    return noaa_total_precipitation

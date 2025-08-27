from typing import Optional, Any, override
import pandas as pd
from pvlib.location import Location

from ...modeling.base_model_context import BaseModelContext
from .caching_key_maker import CachingKeyMaker
from ...modeling.model_context import ModelContext
from ...client.pvradar_site import PvradarSite
from ...modeling.basics import ModelParam


def interval_to_key(interval: ModelContext | pd.Interval) -> str:
    if isinstance(interval, BaseModelContext):
        effective = interval.get('interval')
    else:
        effective = interval
    if not effective:
        return 'None'
    left_value = int(effective.left.value * 1e-9)
    right_value = int(effective.right.value * 1e-9)
    return f'{left_value}_{right_value}_{effective.closed}_{effective.left.tz}'


def location_to_key(location: ModelContext | Location) -> str:
    if isinstance(location, BaseModelContext):
        effective = location.get('location')
    else:
        effective = location
    if not effective:
        return 'None'
    tz = effective.tz
    return f'{effective.latitude}_{effective.longitude}_{tz}'


class CachingKeyMakerPvradarSite(CachingKeyMaker):
    @override
    def make_key(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> str | None:
        assert isinstance(context, PvradarSite)
        if as_param and as_param.attrs and 'resource_type' in as_param.attrs:
            key = interval_to_key(context) + '__' + location_to_key(context) + '__' + as_param.attrs['resource_type']
            key += self.get_source_suffix(as_param=as_param, defaults=defaults)
            if context.freq:
                key += '__' + context.freq
            return key
        return None

    def get_source_suffix(self, *, as_param: ModelParam, defaults: Optional[dict[str, Any]]) -> str:
        if defaults is None:
            defaults = {}
        resource_type = as_param.attrs.get('resource_type')
        assert resource_type, 'resource_type is not set'

        # merra2 has no selectable dataset and resource_type only belongs to MERRA2
        if resource_type[:7] == 'merra2_':
            return ''

        datasource = as_param.attrs.get('datasource')
        if not datasource:
            # cacheable PVGIS resource is the special PVGIS-table
            if resource_type[:6] == 'pvgis_':
                datasource = 'pvgis'

        suffix = '__' + str(datasource)
        dataset = as_param.attrs.get('params', {}).get('dataset')
        if not dataset and defaults:
            dataset = defaults.get('dataset')
        if dataset:
            suffix += '__' + dataset

        if datasource == 'noaa':
            station_id = as_param.attrs.get('station_id') or defaults.get('station_id')
            if station_id:
                suffix += '__s_' + station_id
        return suffix

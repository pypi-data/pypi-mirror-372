from typing import Optional, Any, override

from ...common.pandas_utils import is_series_or_frame
from .caching_advisor import CachingAdvisor
from ...modeling.base_model_context import BaseModelContext
from ...modeling.basics import ModelParam
from ...modeling.model_wrapper import ModelWrapper

cacheable_datasources = ['merra2', 'pvgis', 'era5', 'aemet-grid']
cacheable_prefixes = [ds.replace('-', '_') + '_' for ds in cacheable_datasources]
cacheable_era5_resource_types: dict[str, list[str]] = {
    'era5-land': [
        'total_precipitation',
        'air_temperature',
        'snow_density',
        'snow_depth_water_equivalent',
        'snow_depth',
        'snowfall_water_equivalent',
        'wind_speed',
    ],
    'era5-global': [
        'uv_horizontal_irradiance',
        'air_temperature',
        'snow_density',
        'snow_depth_water_equivalent',
        'snowfall_water_equivalent',
    ],
}
non_cacheable_era5_resource_types: dict[str, list[str]] = {
    'era5-land': ['rainfall', 'snowfall'],
    'era5-global': ['relative_humidity', 'snow_depth', 'snowfall'],
}


class RemoteOnlyAdvisor(CachingAdvisor):
    @override
    def should_save(
        self,
        *,
        model_wrapper: ModelWrapper,
        result: Any,
        context: Optional[BaseModelContext] = None,
    ) -> bool:
        if not context:
            return False
        if 'interval' not in context or 'location' not in context:
            return False
        if not is_series_or_frame(result):
            return False
        attrs = result.attrs
        rt = attrs.get('resource_type', '')
        datasource = attrs.get('datasource')
        if rt.endswith('_table') and datasource in cacheable_datasources:
            return True
        if datasource == 'noaa' and rt == 'rainfall_rate':
            return True

        if datasource == 'era5':
            dataset = attrs.get('dataset')
            if dataset in cacheable_era5_resource_types:
                if rt in cacheable_era5_resource_types[dataset]:
                    return True
        return False

    @override
    def should_lookup(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[BaseModelContext] = None,
    ) -> bool:
        if not context:
            return False
        if 'interval' not in context or 'location' not in context:
            return False
        if as_param and as_param.attrs and 'resource_type' in as_param.attrs:
            rt = as_param.attrs['resource_type']
            if rt.endswith('_table'):
                for prefix in cacheable_prefixes:
                    if rt.startswith(prefix):
                        return True
            elif as_param.attrs.get('datasource') == 'era5':
                # some ERA5 is stored on series level, so doesn't harm to check every time
                return True
            elif as_param.attrs.get('datasource') == 'noaa' and rt == 'rainfall_rate':
                return True

        return False

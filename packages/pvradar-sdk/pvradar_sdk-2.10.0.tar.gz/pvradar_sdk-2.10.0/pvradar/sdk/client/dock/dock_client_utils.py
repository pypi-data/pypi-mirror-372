from collections.abc import Iterable
from typing import Any, Optional
from pvlib.location import Location
from ...modeling.basics import ResourceTypeExtended
from ...display.map import GeoLocatedDataFrame
from ..client import PvradarClient
from ..api_query import Query


def measurement_table(
    *,
    location: Optional[Location] = None,
    max_distance_km: Optional[float] = 1000,
    private: Optional[bool] = None,
    resource_type: ResourceTypeExtended | Iterable[ResourceTypeExtended] | None = None,
    exclude_ids: Optional[Iterable[str]] = None,
    ids: Optional[Iterable[str]] = None,
    **kwargs,
) -> GeoLocatedDataFrame:
    """returns a table of all measurements in the vicinity of the location"""
    if ids is not None:
        if exclude_ids is not None:
            raise ValueError('Cannot specify both ids and exclude_ids')

        if max_distance_km is not None:
            raise ValueError('Please set max_distance_km to None when using ids to avoid ambiguity')

    if location is None and max_distance_km is not None:
        raise ValueError('Location must specified if max_distance_km is set')

    params: dict[str, Any] = dict(**kwargs)

    if location is not None:
        params['lat'] = (location.latitude,)
        params['lon'] = (location.longitude,)

    if max_distance_km is not None:
        params['max_distance_km'] = max_distance_km

    if private is not None:
        params['private'] = private

    if isinstance(resource_type, str):
        params['resource_type'] = resource_type
    elif isinstance(resource_type, Iterable):
        params['resource_type'] = ','.join([str(rt) for rt in resource_type])
    elif resource_type is not None:
        params['resource_type'] = str(resource_type)

    query = Query(
        path='/measurements/groups',
        params=params,
        provider='dock',
    )
    result = PvradarClient.instance().get_data_case(query)

    if ids is not None:
        result = result[result['id'].isin(list(ids))]

    if 'id' in result:
        result.set_index('id', inplace=True)

    if exclude_ids is not None:
        if 'id' in result:
            result = result[~result['id'].isin(list(exclude_ids))]
        else:
            result = result[~result.index.isin(list(exclude_ids))]

    result = GeoLocatedDataFrame(result)
    result.attrs['location'] = location
    return result

# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class meteo_station_table(ResourceTypeDescriptor):
    """A table with available meteo stations as candidates for providing the data for given """

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='meteo_station_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['noaa', 'inmet']], 'data source'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='meteo_station_table',
            datasource=datasource,
        )

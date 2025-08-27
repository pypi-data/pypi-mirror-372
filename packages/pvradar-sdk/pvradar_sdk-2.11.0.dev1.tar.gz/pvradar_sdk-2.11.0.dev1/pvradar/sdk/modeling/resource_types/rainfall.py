# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class rainfall(ResourceTypeDescriptor):
    """The amount of rain (liquid water volume) accumulated over a certain period."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='rainfall',
        to_unit='mm',
        agg='sum',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2', 'noaa', 'aemet-grid', 'era5', 'inmet']], 'data source'] = None,
        dataset: Optional[Literal['era5-global', 'era5-land']] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
        station_id: Optional[str] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='rainfall',
            datasource=datasource,
            dataset=dataset,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
            station_id=station_id,
        )

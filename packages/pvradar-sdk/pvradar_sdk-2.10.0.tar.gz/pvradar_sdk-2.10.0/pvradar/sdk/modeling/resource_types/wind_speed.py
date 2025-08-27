# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class wind_speed(ResourceTypeDescriptor):
    """The speed of wind close to the ground (usually in 2m height)."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='wind_speed',
        to_unit='m/s',
        agg='mean',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['pvgis', 'merra2', 'era5']], 'data source'] = None,
        dataset: Optional[Literal['era5-global', 'era5-land', 'pvgis-era5', 'pvgis-sarah3']] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='wind_speed',
            datasource=datasource,
            dataset=dataset,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class global_horizontal_irradiance(ResourceTypeDescriptor):
    """The total solar irradiance received by a horizontal up-facing surface. """

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='global_horizontal_irradiance',
        to_unit='W/m^2',
        agg='mean',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['pvgis', 'era5']], 'data source'] = None,
        dataset: Optional[Literal['era5-global', 'era5-land', 'pvgis-era5', 'pvgis-sarah3']] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='global_horizontal_irradiance',
            datasource=datasource,
            dataset=dataset,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

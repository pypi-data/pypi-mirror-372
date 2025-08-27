# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class relative_humidity(ResourceTypeDescriptor):
    """The relative humidity contained in the air."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='relative_humidity',
        to_unit='%',
        agg='mean',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2', 'era5']], 'data source'] = None,
        dataset: Optional[Literal['era5-global', 'era5-land']] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='relative_humidity',
            datasource=datasource,
            dataset=dataset,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

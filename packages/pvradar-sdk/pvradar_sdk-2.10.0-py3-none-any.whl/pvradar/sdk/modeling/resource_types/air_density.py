# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class air_density(ResourceTypeDescriptor):
    """The density of air."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='air_density',
        to_unit='kg/m^3',
        agg='mean',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2']], 'data source'] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='air_density',
            datasource=datasource,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

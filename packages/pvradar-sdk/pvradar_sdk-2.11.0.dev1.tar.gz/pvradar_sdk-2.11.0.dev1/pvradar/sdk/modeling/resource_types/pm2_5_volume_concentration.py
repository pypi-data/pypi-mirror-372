# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class pm2_5_volume_concentration(ResourceTypeDescriptor):
    """The total particulate matter concentration including all contaminants with a diameter below 2.5 µm (PM2.5)."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='pm2_5_volume_concentration',
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
            resource_type='pm2_5_volume_concentration',
            datasource=datasource,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

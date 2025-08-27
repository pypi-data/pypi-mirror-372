# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class merra2_land_surface_table(ResourceTypeDescriptor):
    """Subset of the original MERRA2 collection M2T1NXLND as a Data Frame"""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='merra2_land_surface_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2']], 'data source'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='merra2_land_surface_table',
            datasource=datasource,
        )

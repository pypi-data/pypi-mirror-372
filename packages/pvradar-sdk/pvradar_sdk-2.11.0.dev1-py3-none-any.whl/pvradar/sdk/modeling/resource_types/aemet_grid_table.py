# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class aemet_grid_table(ResourceTypeDescriptor):
    """Table with single column: precipitation"""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='aemet_grid_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['aemet-grid']], 'data source'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='aemet_grid_table',
            datasource=datasource,
        )

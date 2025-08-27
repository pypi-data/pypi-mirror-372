# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class era5_single_level_table(ResourceTypeDescriptor):
    """Subset of ERA5 data, originally created for snow modeling"""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='era5_single_level_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['era5']], 'data source'] = None,
        dataset: Optional[Literal['era5-global', 'era5-land']] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='era5_single_level_table',
            datasource=datasource,
            dataset=dataset,
        )

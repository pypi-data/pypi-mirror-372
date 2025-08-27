# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class pvgis_seriescalc_table(ResourceTypeDescriptor):
    
    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='pvgis_seriescalc_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['pvgis']], 'data source'] = None,
        dataset: Optional[Literal['pvgis-era5', 'pvgis-sarah3']] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='pvgis_seriescalc_table',
            datasource=datasource,
            dataset=dataset,
        )

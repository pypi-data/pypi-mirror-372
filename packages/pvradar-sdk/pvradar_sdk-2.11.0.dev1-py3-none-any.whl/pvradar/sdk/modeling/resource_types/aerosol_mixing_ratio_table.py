# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class aerosol_mixing_ratio_table(ResourceTypeDescriptor):
    """Table with each column representing mixing ratio of certain type of aerosol in the air. """

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='aerosol_mixing_ratio_table',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2']], 'data source'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='aerosol_mixing_ratio_table',
            datasource=datasource,
        )

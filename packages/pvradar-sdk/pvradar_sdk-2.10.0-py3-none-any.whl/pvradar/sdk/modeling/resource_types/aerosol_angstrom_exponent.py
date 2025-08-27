# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class aerosol_angstrom_exponent(ResourceTypeDescriptor):
    """A dimensionless indicator of aerosol particle size distribution based on how aerosol optical depth varies with particle size."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='aerosol_angstrom_exponent',
        to_unit='dimensionless',
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
            resource_type='aerosol_angstrom_exponent',
            datasource=datasource,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

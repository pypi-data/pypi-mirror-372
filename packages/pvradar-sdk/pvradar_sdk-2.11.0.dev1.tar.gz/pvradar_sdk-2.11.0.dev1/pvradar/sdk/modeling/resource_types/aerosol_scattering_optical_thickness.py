# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional, Literal


class aerosol_scattering_optical_thickness(ResourceTypeDescriptor):
    """A dimensionless measure of how aerosols scatter incoming solar radiation excluding absorption effects. """

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='aerosol_scattering_optical_thickness',
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
            resource_type='aerosol_scattering_optical_thickness',
            datasource=datasource,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

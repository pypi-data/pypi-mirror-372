# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from ...client.models.merra2_types import Merra2ParticleName
from typing import Annotated, Optional, Literal


class particle_mixing_ratio(ResourceTypeDescriptor):
    """The mass of suspended particles in the air per unit mass of air"""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='particle_mixing_ratio',
        to_unit='kg/kg',
        agg='mean',
    )

    def __init__(
        self,
        *,
        datasource: Annotated[Optional[Literal['merra2']], 'data source'] = None,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
        particle_name: Optional[Merra2ParticleName] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='particle_mixing_ratio',
            datasource=datasource,
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
            particle_name=particle_name,
        )

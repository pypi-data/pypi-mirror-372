# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class cell_temperature(ResourceTypeDescriptor):
    """The actual temperature of a photovoltaic (PV) cell within a solar module. It directly affects the electrical performance of the cell and is typically higher than the ambient temperature due to solar radiation and electrical resistance."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='cell_temperature',
        to_unit='degC',
        agg='mean',
    )

    def __init__(
        self,
        *,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='cell_temperature',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

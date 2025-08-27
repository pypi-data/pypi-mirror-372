# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class air_pressure(ResourceTypeDescriptor):
    """The force exerted by the weight of the air column above a given point."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='air_pressure',
        to_unit='hPa',
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
            resource_type='air_pressure',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

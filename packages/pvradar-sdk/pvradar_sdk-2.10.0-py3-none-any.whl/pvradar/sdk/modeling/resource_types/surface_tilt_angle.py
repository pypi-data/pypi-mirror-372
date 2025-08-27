# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class surface_tilt_angle(ResourceTypeDescriptor):
    """The angle between the PV module’s surface and the horizontal plane. """

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='surface_tilt_angle',
        to_unit='deg',
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
            resource_type='surface_tilt_angle',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
        )

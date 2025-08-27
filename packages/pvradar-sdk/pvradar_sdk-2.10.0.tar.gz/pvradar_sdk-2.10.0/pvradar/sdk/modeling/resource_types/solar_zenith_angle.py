# This is an auto-generated file. Do not change it manually
#
# fmt: off
from ..resource_type_helpers import ResourceTypeDescriptor
from typing import Annotated, Optional


class solar_zenith_angle(ResourceTypeDescriptor):
    """The apparent angle between the sun and the vertical (or the zenith point directly above an observer). A value of 0° means the sun is directly overhead, 90° means the sun is on the horizon line."""

    standard = ResourceTypeDescriptor.make_attrs(
        resource_type='solar_zenith_angle',
        to_unit='deg',
        agg='mean',
    )

    def __init__(
        self,
        *,
        to_unit: Annotated[Optional[str], 'convert to unit'] = None,
        set_unit: Annotated[Optional[str], 'override unit'] = None,
        to_freq: Annotated[Optional[str], 'resample result using new freq'] = None,
        apparent: bool = True,
    ):
        self._instance_attrs = ResourceTypeDescriptor.make_attrs(
            resource_type='solar_zenith_angle',
            to_unit=to_unit,
            set_unit=set_unit,
            to_freq=to_freq,
            apparent=apparent,
        )

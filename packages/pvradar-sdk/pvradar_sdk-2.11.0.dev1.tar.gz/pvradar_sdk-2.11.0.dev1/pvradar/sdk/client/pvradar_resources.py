from typing import Any, NotRequired, Optional, TypeGuard, get_args
from typing_extensions import Annotated as A

from ..modeling.basics import SeriesAttrs, PvradarResourceType
from ..modeling.resource_types._list import standard_mapping


class SeriesConfigAttrs(SeriesAttrs):
    param_names: NotRequired[list[str]]


class PvradarSeriesConfigAttrs(SeriesConfigAttrs):
    resource_type: NotRequired[PvradarResourceType]  # type: ignore


S = PvradarSeriesConfigAttrs

_possible_pvradar_resource_types = get_args(PvradarResourceType.__value__)


def check_is_pvradar_resource_type(name: Any) -> TypeGuard[PvradarResourceType]:
    return name in _possible_pvradar_resource_types


def extract_unit_from_annotation(v: Any) -> Optional[str]:
    if isinstance(v, type(A[Any, Any])):  # type: ignore
        if hasattr(v, '__metadata__'):
            for maybe_attrs in v.__metadata__:  # type: ignore
                if isinstance(maybe_attrs, dict):
                    if 'unit' in maybe_attrs:
                        return maybe_attrs['unit']
                    if 'to_unit' in maybe_attrs:
                        return maybe_attrs['to_unit']
                    if 'set_unit' in maybe_attrs:
                        return maybe_attrs['set_unit']


def unit_for_pvradar_resource_type(resource_type: PvradarResourceType) -> Optional[str]:
    if resource_type not in standard_mapping:
        raise ValueError(f'No standard pvradar annotation for {resource_type}')
    attrs = standard_mapping[resource_type]
    return attrs.get('to_unit')

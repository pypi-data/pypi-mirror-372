from typing import Mapping, NotRequired
from pydantic import ConfigDict, TypeAdapter, ValidationError
from ..modeling.basics import Attrs
from ..modeling.resource_type_helpers import ResourceTypeDescriptor


def validate_typed_dict(data: dict | Mapping, typed_dict_class: type) -> None:
    class AdjustedDict(typed_dict_class):
        __pydantic_config__ = ConfigDict(extra='forbid')

    ta = TypeAdapter(AdjustedDict)
    try:
        ta.validate_python(data)
    except ValidationError as e:
        f = e.errors()[0]
        raise ValueError(f'Validation failed for {typed_dict_class.__name__}: {f["type"]}, for {f["loc"]}: {f["msg"]}')


class NoExtrasAttrs(Attrs):
    resource_type: NotRequired[str]  # type: ignore
    __pydantic_config__ = ConfigDict(extra='forbid')  # type: ignore


ta_NoExtrasAttrs = TypeAdapter(NoExtrasAttrs)


def validate_pvradar_attrs(data: Mapping) -> None:
    if isinstance(data, (type(ResourceTypeDescriptor), ResourceTypeDescriptor)):
        # validation is skipped, because it was already performed in the corresponding constructor
        return
    if len(data.keys()) == 0:
        return
    try:
        ta_NoExtrasAttrs.validate_python(data)
    except ValidationError as e:
        f = e.errors()[0]
        raise ValueError(f'Bad PVRADAR Attrs: {f["msg"]} {f["loc"]} in {data}')

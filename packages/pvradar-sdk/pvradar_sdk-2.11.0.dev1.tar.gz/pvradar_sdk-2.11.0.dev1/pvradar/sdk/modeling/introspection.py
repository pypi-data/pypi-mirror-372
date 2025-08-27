import inspect
from pydantic.fields import FieldInfo
from typing import Annotated, Any, get_args
from .basics import Attrs, LambdaArgument
from .resource_type_helpers import ResourceTypeDescriptor, ResourceTypeClass


def attrs_from_annotation(annotation: Any) -> Attrs | None:
    if isinstance(annotation, dict):
        return Attrs(**annotation)
    if isinstance(annotation, type(Annotated[Any, Any])):  # type: ignore
        if hasattr(annotation, '__metadata__'):
            for m in annotation.__metadata__:  # type: ignore
                if isinstance(m, (dict, ResourceTypeDescriptor)):
                    return m  # type: ignore
                if isinstance(m, ResourceTypeClass):
                    return {'resource_type': m.standard['resource_type']}  # type: ignore
    return None


def lambda_argument_from_annotation(annotation: Any) -> LambdaArgument | None:
    if isinstance(annotation, type(Annotated[Any, Any])):  # type: ignore
        if hasattr(annotation, '__metadata__'):
            for m in annotation.__metadata__:  # type: ignore
                if isinstance(m, LambdaArgument):
                    return m
    return None


def field_info_from_annotation(annotation: Any) -> FieldInfo | None:
    if isinstance(annotation, type(Annotated[Any, Any])):  # type: ignore
        if hasattr(annotation, '__metadata__'):
            maybe_field = annotation.__metadata__[0]  # type: ignore
            if isinstance(maybe_field, FieldInfo):
                return maybe_field
    return None


def type_from_annotation(annotation: Any) -> Any:
    if isinstance(annotation, type(Annotated[Any, Any])):  # type: ignore
        return get_args(annotation)[0]  # type: ignore
    if annotation is inspect._empty:
        return Any
    return annotation

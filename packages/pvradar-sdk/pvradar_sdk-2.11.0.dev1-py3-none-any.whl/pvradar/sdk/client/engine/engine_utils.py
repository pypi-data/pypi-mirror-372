import inspect
from typing import Any
from pydantic import BaseModel

from .engine_types import ModelDefinition, ModelParamSpec, PydanticFieldSpec
from ...modeling.model_context import ModelWrapper
from ...modeling.basics import DataType, ModelParam
from ...modeling.introspection import attrs_from_annotation


def model_to_definition(model: ModelWrapper) -> ModelDefinition:
    params: list[ModelParamSpec] = []
    result: ModelDefinition = {
        'name': model.name,
        'params': params,
        'resource_type': model.resource_type or 'any',  # type: ignore
    }
    return result


def infer_data_type_from_annotation(annotation: Any) -> DataType: ...


def annotation_to_pydantic_field_spec(model: BaseModel | None) -> PydanticFieldSpec | None: ...


def model_param_to_spec(param: ModelParam) -> ModelParamSpec:
    result: ModelParamSpec = {
        'name': param.name,
        'data_type': infer_data_type_from_annotation(param.annotation),
        'default': param.default,
    }

    attrs = attrs_from_annotation(param.annotation)
    if attrs:
        result['attrs'] = attrs

    pydantic_spec = annotation_to_pydantic_field_spec(param.annotation)
    if pydantic_spec:
        result['pydantic_field'] = pydantic_spec

    if param.default != inspect.Parameter.empty:
        result['default'] = param.default
    return result

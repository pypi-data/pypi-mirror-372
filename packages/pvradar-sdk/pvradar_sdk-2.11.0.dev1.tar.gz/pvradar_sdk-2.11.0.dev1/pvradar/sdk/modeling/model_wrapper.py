import inspect
from dataclasses import dataclass, field
from typing import Annotated, Any, Optional, Self, Tuple, override

import pandas as pd
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from ..common.exceptions import PvradarSdkError
from .introspection import attrs_from_annotation, lambda_argument_from_annotation, type_from_annotation
from .basics import Datasource, ModelConfig, ModelParam
from .resource_type_helpers import attrs_as_descriptor_mapping


class ModelWrapper:
    """
    Wraps a function (model) with additional metadata and validation.
    The wrapper can be used as drop-in replacement for the original function, as it implements the __call__ method.
    The ModelContext automatically wraps all functions with this class upon registration
    """

    def __init__(
        self,
        func: Any,
        defaults: Optional[dict[str, Any]] = None,
        __config__: Optional[ModelConfig] = None,
    ):
        self.config: ModelConfig = __config__ or {}
        self._func = func
        self.defaults: dict[str, Any] = defaults or {}
        (self.params, self.return_param) = self._introspect_func()
        self.validation_model = None

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)

    @override
    def __repr__(self):
        return f'<model:{self.name:}({self._param_summary()})>'

    @property
    def __annotations__(self):  # type: ignore
        return self._func.__annotations__

    def _param_summary(self):
        return ','.join([f'{p.name}' for p in self.params.values()])

    def _make_pydantic_model(self) -> None:
        f = self._func
        fields: dict = {}
        for k in f.__annotations__:
            v = f.__annotations__[k]
            if isinstance(v, type(Annotated[Any, Any])):  # type: ignore
                if hasattr(v, '__metadata__'):
                    for maybe_field in v.__metadata__:  # type: ignore
                        if isinstance(maybe_field, FieldInfo):
                            fields[k] = (v, maybe_field)
        if fields:
            self.validation_model = create_model(
                self.name,
                __config__={'arbitrary_types_allowed': True},
                **fields,
            )
        else:
            self.validation_model = None

    @property
    def resource_type(self) -> str | None:
        return self._func.resource_type if hasattr(self._func, 'resource_type') else None

    @property
    def name(self) -> str:
        return self._func.name if hasattr(self._func, 'name') else self._func.__name__

    @property
    def datasource(self) -> Datasource | None:
        return self._func.datasource if hasattr(self._func, 'datasource') else None

    @property
    def synchronize_freq(self) -> str | None:
        return self._func.synchronize_freq if hasattr(self._func, 'synchronize_freq') else None

    @property
    def to_freq(self) -> str | None:
        return self._func.to_freq if hasattr(self._func, 'to_freq') else None

    @property
    def label(self) -> str:
        return self._func.label if hasattr(self._func, 'label') else self.name

    def _introspect_func(self) -> Tuple[dict[str, ModelParam], ModelParam]:
        """tuple of a dictionary of arguments as ModelParam objects, and the return type as a ModelParam object"""
        synchronize_freq = self._func.synchronize_freq if hasattr(self._func, 'synchronize_freq') else None
        params: dict[str, ModelParam] = {}
        signature = inspect.signature(self._func)
        for k in signature.parameters:
            default = signature.parameters[k].default
            if k in self.defaults:
                default = self.defaults.get(k)
            annotation = signature.parameters[k].annotation
            param = ModelParam(
                name=k,
                annotation=annotation,
                default=default,
                attrs=attrs_from_annotation(annotation) or {},
                type=type_from_annotation(annotation),
                lambda_argument=lambda_argument_from_annotation(annotation),
                is_var_keyword=(signature.parameters[k].kind == inspect.Parameter.VAR_KEYWORD),
            )
            if synchronize_freq and param.type in (pd.Series, pd.DataFrame):
                if not param.attrs.get('to_freq'):
                    new_attrs = dict(attrs_as_descriptor_mapping(param.attrs)).copy()
                    new_attrs['to_freq'] = synchronize_freq
                    param.attrs = new_attrs
            params[k] = param

        return_param = ModelParam(
            name='return',
            annotation=signature.return_annotation,
            attrs=attrs_from_annotation(signature.return_annotation) or {},
            type=type_from_annotation(signature.return_annotation),
        )
        return (params, return_param)

    @property
    def pydantic_model(self) -> type[BaseModel] | None:
        if not self.validation_model:
            self._make_pydantic_model()
        return self.validation_model

    def validate(self, **kwargs):
        pm = self.pydantic_model
        if pm:
            pm(**kwargs)

    def make_start_vector(self, param_names: list[str], bounds: list[tuple[float, float]] | None = None) -> list[float]:
        raise PvradarSdkError('make_start_vector() is obsolete, use context.optimize directly')

    def make_optimization_bounds(self, param_names: list[str]) -> list[tuple[float, float]]:
        raise PvradarSdkError('make_optimization_bounds() is obsolete, use context.optimize directly')

    @classmethod
    def wrap(cls, model) -> Self:
        if isinstance(model, type(cls)):
            return model
        return cls(model)


@dataclass
class ModelBinding:
    model: ModelWrapper
    defaults: dict[str, Any] = field(default_factory=dict)

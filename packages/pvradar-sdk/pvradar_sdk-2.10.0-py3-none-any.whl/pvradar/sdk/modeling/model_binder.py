from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Annotated, override

from .basics import BindingNotFound, ModelParam
from .model_context import ModelContext
from .model_wrapper import ModelWrapper, ModelBinding


class AbstractBinder(ABC):
    @abstractmethod
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any: ...

    def __call__(self, *args, **kwargs):
        if len(args):
            raise ValueError(f'Unexpected positional arguments, {args}')
        return self.bind(**kwargs)


class KnownModelsBinder(AbstractBinder):
    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        if not context:
            return BindingNotFound
        name = resource_name
        if name in context.models and not context.models[name].config.get('disable_auto_resolve', False):
            return ModelBinding(model=context.models[name], defaults=defaults or {})
        return BindingNotFound


class FirstMatchingTypeBinder(AbstractBinder):
    def __init__(
        self,
        models: list[ModelWrapper],
        *,
        name: str = '',
        only_for_context: Annotated[Optional[Type], 'class the context must be (or inherited from) for binder to work'] = None,
    ):
        self.models = models
        self.name = name
        self.only_for_context = only_for_context

    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        defaults = defaults or {}
        if self.only_for_context and not isinstance(context, self.only_for_context):
            return BindingNotFound
        for model in self.models:
            if model.resource_type:
                if model.resource_type == resource_name or (
                    as_param and as_param.attrs and as_param.attrs.get('resource_type') == model.resource_type
                ):
                    return ModelBinding(model=model, defaults=defaults)
        return BindingNotFound

from typing import Any, Optional

from .model_wrapper import ModelBinding
from .basics import BindingNotFound, LambdaArgument, ModelParam
from .base_model_context import BaseModelContext


def known_model_binder(
    *,
    resource_name: str,
    as_param: Optional[ModelParam] = None,
    defaults: Optional[dict[str, Any]] = None,
    context: Optional[Any] = None,
) -> Any:
    if context is None:
        return BindingNotFound
    name = resource_name
    if name in context.models and not context.models[name].config.get('disable_auto_resolve', False):
        return ModelBinding(model=context.models[name], defaults=defaults or {})
    return BindingNotFound


def lambda_argument_binder(
    *,
    resource_name: str,
    as_param: Optional[ModelParam] = None,
    defaults: Optional[dict[str, Any]] = None,
    context: Optional[Any] = None,
) -> Any:
    if context is None:
        return BindingNotFound
    assert isinstance(context, BaseModelContext)
    if as_param and isinstance(as_param.lambda_argument, LambdaArgument):
        return ModelBinding(
            model=context.wrap_model(context._lambda_argument_reader(as_param)),  # type: ignore
            defaults=defaults or {},
        )
    return BindingNotFound

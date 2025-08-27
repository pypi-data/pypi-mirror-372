from typing import Any, Callable, Mapping, Optional, TypeGuard, override
from pandas import DatetimeIndex
import pandas as pd

from ..display.flowchart import is_series_or_frame
from ..modeling.decorators import update_attrs
from .resource_type_helpers import ResourceTypeClass, ResourceTypeDescriptor, match_attrs
from .resource_types._list import Datasource, PvradarResourceType
from .utils import attrs_as_descriptor_mapping, safe_copy
from .base_model_context import BaseModelContext, Hook
from .basics import BindingNotFound, ModelParam
from .model_wrapper import ModelBinding, ModelWrapper
from ..common.pandas_utils import crop_by_interval


class HookSubject:
    pass


_allowed_attrs_fields = ['resource_type', 'agg', 'datasource']


def _validate_attrs_matcher(attrs: Optional[Mapping[str, Any] | ResourceTypeDescriptor | ResourceTypeClass] = None):
    if not attrs:
        return
    attrs = attrs_as_descriptor_mapping(attrs)
    for key in attrs.keys():
        if key == 'params':
            continue
        if key not in _allowed_attrs_fields:
            raise ValueError(f'unexpected key in attrs mask for argument hook: {key}')


class BindingAction:
    def make_binding(
        self,
        *,
        context: BaseModelContext,
        defaults: Optional[dict[str, Any]] = None,
    ):
        raise NotImplementedError()


class BindingHook:
    action: BindingAction


def _validate_hook_binds(hook: Hook) -> TypeGuard[BindingHook]:
    if not hasattr(hook, 'action'):
        raise ValueError('hook must have an action: {hook}')
    action = getattr(hook, 'action')
    if not action:
        raise ValueError('hook action is None: {hook}')
    if not hasattr(action, 'make_binding'):
        raise ValueError('hook action must have make_binding method: {hook}')
    return True


class ActionUseValue(BindingAction):
    def __init__(self, value: Any, *, label: str = ''):
        self.value = value

    @override
    def make_binding(
        self,
        *,
        context: BaseModelContext,
        defaults: Optional[dict[str, Any]] = None,
    ):
        if is_series_or_frame(self.value) and isinstance(self.value.index, DatetimeIndex) and hasattr(context, 'interval'):
            interval = getattr(context, 'interval')
            return crop_by_interval(self.value, interval)
        return self.value

    @override
    def __repr__(self):
        if isinstance(self.value, (int, float)):
            return str(self.value)
        if isinstance(self.value, (pd.Series)):
            return f'series with {len(self.value)} rows'
        if isinstance(self.value, (pd.DataFrame)):
            return f'DataFrame with {len(self.value)} rows'
        return super().__repr__()


class ActionUseModel(BindingAction):
    def __init__(
        self,
        model: Any,
        *,
        defaults: Optional[dict[str, Any]] = None,
        label: str = '',
    ):
        if label:
            model = update_attrs(label=label)(model)
        self.model = model
        self.defaults = defaults or {}

    @override
    def make_binding(
        self,
        *,
        context: BaseModelContext,
        defaults: Optional[dict[str, Any]] = None,
    ):
        model = self.model
        if isinstance(model, str):
            if model not in context.models:
                raise LookupError(f'model {model} not registered in context')
            model = context.models[model]

        effective_defaults = self.defaults
        if defaults:
            effective_defaults = effective_defaults.copy()
            effective_defaults.update(defaults)
        return ModelBinding(model=model, defaults=effective_defaults)

    @override
    def __repr__(self):
        if isinstance(self.model, ModelWrapper):
            return f'<model {self.model.name}>'
        if isinstance(self.model, str):
            return f'<model {self.model}>'
        return super().__repr__()


class DescriptorAction:
    def apply_to_attrs(
        self,
        *,
        attrs: Any,
    ):
        raise NotImplementedError()


class UpdateAttrsAction(DescriptorAction):
    def __init__(self, attrs: Any):
        self.descriptor = attrs_as_descriptor_mapping(attrs)

    @override
    def apply_to_attrs(
        self,
        *,
        attrs: Any,
    ):
        if self.descriptor:
            attrs = dict(attrs_as_descriptor_mapping(attrs)).copy()
            attrs.update(self.descriptor)
        return attrs


class PreferAttrsAction(DescriptorAction):
    def __init__(self, attrs: Any):
        self.descriptor = attrs_as_descriptor_mapping(attrs)

    @override
    def apply_to_attrs(
        self,
        *,
        attrs: Any,
    ):
        if self.descriptor:
            attrs = dict(attrs_as_descriptor_mapping(attrs)).copy()
            for key in self.descriptor.keys():
                if key in attrs:
                    continue
                attrs[key] = self.descriptor[key]
        return attrs


class BinderHook(Hook):
    def __init__(self, subject: HookSubject, action: BindingAction, *, label: str = ''):
        self.subject = subject
        self.action = action
        self.label = None

    @override
    def __repr__(self):
        result = f'hook: for {self.subject} use {self.action}'
        if self.label:
            result += f', label it "{self.label}"'
        return result


class DescriptorHook(Hook):
    def __init__(self, subject: HookSubject, action: DescriptorAction):
        self.subject = subject
        self.action = action


class ChainedHookSubject(HookSubject):
    def use(self, what: Any, *, label: str = '') -> BinderHook:
        return BinderHook(
            subject=self,
            action=ActionUseValue(what, label=label),
        )

    def use_model(self, model: Any, label: str = '', **kwargs) -> BinderHook:
        return BinderHook(subject=self, action=ActionUseModel(model, defaults=kwargs, label=label))

    def use_datasource(self, datasource: Datasource) -> DescriptorHook:
        return DescriptorHook(subject=self, action=UpdateAttrsAction(attrs={'datasource': datasource}))

    def prefer_datasource(self, datasource: Datasource) -> DescriptorHook:
        return DescriptorHook(subject=self, action=PreferAttrsAction(attrs={'datasource': datasource}))


class ArgumentHookSubject(ChainedHookSubject):
    def __init__(
        self,
        argument_name: Optional[str] = None,
        attrs: Optional[dict] = None,
    ):
        self.argument_name = argument_name
        _validate_attrs_matcher(attrs)
        self.attrs = attrs

    def match_param(self, param: ModelParam):
        if param.name == '_anonymous':
            return False
        if self.argument_name and self.argument_name != param.name:
            return False
        if self.attrs:
            if not match_attrs(param.attrs, self.attrs):
                return False
        return True

    @override
    def __repr__(self):
        return f'<arg {self.argument_name}>'


class ResourceHookSubject(ChainedHookSubject):
    def __init__(
        self,
        attrs: Any,
    ):
        _validate_attrs_matcher(attrs)
        self.attrs = attrs

    def match_param(self, param: ModelParam):
        result = match_attrs(param.attrs, self.attrs)
        return result

    @override
    def use(self, what: Any, *, label: str = '', origin_name: str = 'hook') -> BinderHook:
        if is_series_or_frame(what):
            attrs_dict = attrs_as_descriptor_mapping(self.attrs)
            what = safe_copy(what)

            what.attrs['origin'] = {'model_name': f'hook:{origin_name}'}
            if label:
                what.attrs['label'] = label
                what.attrs['origin']['label'] = label

            for key, value in attrs_dict.items():
                if key not in what.attrs:
                    what.attrs[key] = value

        return BinderHook(subject=self, action=ActionUseValue(what))

    @override
    def __repr__(self):
        return '<... certain resource>'


def for_argument(argument_descriptor: Any) -> ArgumentHookSubject:
    if isinstance(argument_descriptor, str):
        return ArgumentHookSubject(argument_name=argument_descriptor)
    elif isinstance(argument_descriptor, dict):
        return ArgumentHookSubject(attrs=argument_descriptor)
    else:
        raise ValueError(f'unexpected argument descriptor type: {type(argument_descriptor)}')


def use_arguments(argument_dict: Mapping[str, Any]) -> list[Hook]:
    return [for_argument(key).use(value) for key, value in argument_dict.items()]


def for_resource(attrs: Mapping[str, Any] | ResourceTypeDescriptor | ResourceTypeClass) -> ResourceHookSubject:
    _validate_attrs_matcher(attrs)
    return ResourceHookSubject(attrs=attrs)


def hook_binder(
    *,
    resource_name: str,
    as_param: Optional[ModelParam] = None,
    defaults: Optional[dict[str, Any]] = None,
    context: Optional[BaseModelContext] = None,
) -> Any:
    if context is None or not context.registered_hooks or not as_param:
        return BindingNotFound
    for hook in context.registered_hooks:
        if isinstance(hook, BinderHook) and isinstance(hook.subject, (ArgumentHookSubject, ResourceHookSubject)):
            if hook.subject.match_param(as_param):
                if _validate_hook_binds(hook):
                    return hook.action.make_binding(context=context, defaults=defaults)
    return BindingNotFound


def preprocess_bind_resource_input(
    *,
    context: BaseModelContext,
    as_param: Optional[ModelParam] = None,
    defaults: Optional[dict[str, Any]] = None,
) -> tuple[Optional[ModelParam], Optional[dict[str, Any]]]:
    """apply hooks to inputs for binding, e.g. changing defaults or changing attrs of the ModelParam"""
    if not as_param or not as_param.attrs:
        return as_param, defaults

    for hook in context.registered_hooks:
        if isinstance(hook, DescriptorHook) and isinstance(hook.subject, (ArgumentHookSubject, ResourceHookSubject)):
            if hook.subject.match_param(as_param):
                as_param = as_param.copy()
                as_param.attrs = hook.action.apply_to_attrs(attrs=as_param.attrs)

    return as_param, defaults


class PostprocessInputHook(Hook):
    def __init__(self, processor: Callable[[BaseModelContext, ModelWrapper, dict[str, Any]], dict[str, Any]]): ...


class HookSelection:
    """a context manager for 'with context.hooks(...)' syntax, see PEP 343"""

    def __init__(self, context: BaseModelContext, hooks: list[Hook]):
        self.original_hooks = context.registered_hooks
        self.additional_hooks = hooks
        context.registered_hooks = list(reversed(hooks)) + context.registered_hooks
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.context.registered_hooks = self.original_hooks


def precalculate_resource(
    context: BaseModelContext,
    resource_type: Mapping[str, Any] | PvradarResourceType | ResourceTypeClass,
) -> Hook:
    descriptor_attrs = attrs_as_descriptor_mapping(resource_type)
    return for_resource(descriptor_attrs['resource_type']).use(
        context.resource(descriptor_attrs),
        origin_name='pre-calculated',
    )

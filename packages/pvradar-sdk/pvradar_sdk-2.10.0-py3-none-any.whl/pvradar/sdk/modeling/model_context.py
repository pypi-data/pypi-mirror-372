import inspect
from typing import Any, Callable, Mapping, Optional, override
import warnings
from scipy.optimize import minimize
import pandas as pd

from .profiling.profiler import PvradarProfiler
from .utils import convert_by_attrs
from .model_wrapper import ModelBinding, ModelWrapper
from .optimization import OptimizationSeriesTarget, OptimizationTarget
from .basics import BindingNotFound, EmptyBinding, ModelConfig, ModelParam, ParameterConstraint
from .resource_type_helpers import ResourceTypeDescriptor, ResourceTypeClass
from .base_model_context import BaseModelContext, Hook
from .sweeps.sweep_types import SweepRange
from .sweeps.sync_sweep_iterator import SyncSweepIterator
from ..common.exceptions import PvradarSdkError
from .hooks import attrs_as_descriptor_mapping, hook_binder, HookSelection, preprocess_bind_resource_input
from ..common.pandas_utils import is_series_or_frame
from .binders import lambda_argument_binder, known_model_binder

MAX_DEPTH = 50
MAX_OPTIMIZATION_PARAMETERS = 10


class ModelContext(BaseModelContext):
    def __init__(self, id: Optional[str] = None, **kwargs) -> None:
        super().__init__()
        self.models: dict[str, ModelWrapper] = {}
        self._resources: dict[str, Any] = dict(kwargs)
        self.binders: list[Callable] = [hook_binder, lambda_argument_binder, known_model_binder]
        self.config: ModelConfig = {}
        self.mapping_by_resource_types: dict[str, ModelWrapper] = {}
        self.id = id
        self._locks = {}
        self.all_kwargs = {}

    def hooks(self, *args: Hook) -> HookSelection:
        return HookSelection(self, list(args))

    @override
    def register_model(
        self,
        model: Callable,
        *,
        defaults: Optional[dict[str, Any]] = None,
        for_resource_type: Optional[str | bool] = None,
    ) -> ModelWrapper:
        if not isinstance(model, ModelWrapper):
            model = ModelWrapper(model, defaults)
        if defaults is None:
            defaults = {}
        self.models[model.name] = model
        if for_resource_type:
            if for_resource_type is True:
                for_resource_type = getattr(model, 'resource_type', None)
                if not for_resource_type:
                    raise ValueError(
                        'Model {mode.name} not have resource_type set. '
                        + 'Use @resource_type decorator or explicit for_resource_type="..."'
                    )
            assert isinstance(for_resource_type, str)
            self.mapping_by_resource_types[for_resource_type] = model
        return model

    @override
    def wrap_model(self, model: Callable | str) -> ModelWrapper:
        if isinstance(model, str):
            if model not in self.models:
                raise LookupError(f'Model {model} not found')
            model = self.models[model]
        if not isinstance(model, ModelWrapper):
            model = ModelWrapper(model)
        return model

    def bind_params_with_defaults(
        self,
        model: ModelWrapper,
        __config__: Optional[ModelConfig] = None,
        **kwargs,
    ) -> dict[str, Any]:
        defaults = model.defaults.copy()
        defaults.update(kwargs)
        return self.bind_params(params=model.params, defaults=defaults, for_model=model.name, __config__=__config__)

    def _convert_by_attrs(self, value: Any, param_attrs: Mapping[str, Any]) -> Any:
        """wrapper around convert_by_attrs to allow for context level overrides (e.g. validation for PvradarSite)"""
        return convert_by_attrs(value, param_attrs)

    def _process_output(self, model: ModelWrapper, bound_params: dict[str, Any], result: Any) -> Any:
        if model.return_param.attrs:
            result = self._convert_by_attrs(result, model.return_param.attrs)
            if isinstance(result, pd.Series) or isinstance(result, pd.DataFrame):
                if 'resource_type' in model.return_param.attrs:
                    result.attrs['resource_type'] = model.return_param.attrs['resource_type']
        for output_filter in self.output_filters:
            result = output_filter(model, bound_params, result)
        return result

    def _process_input_param(self, model: ModelWrapper, param: ModelParam, value: Any) -> Any:
        try:
            if param.attrs is not None:
                value = self._convert_by_attrs(value, param.attrs)
                if param.attrs.get('keep', False):
                    if param.name == '_anonymous':
                        raise ValueError('Cannot keep anonymous parameter')
                    self._resources[param.name] = value
            return value
        except Exception as e:
            raise PvradarSdkError(
                f'Error while processing input param {param.name} for {model.name}: caused by ...\n{e.__class__.__name__} {e}'
            ) from e

    def _process_input(self, model: ModelWrapper, _depth: int = 0, **kwargs) -> dict[str, Any]:
        bound_params = self.bind_params_with_defaults(model, **kwargs)
        result = bound_params.copy()

        """Process input parameters before passing them to the model"""
        for k, v in result.items():
            if isinstance(v, ModelBinding):
                combined_defaults = v.defaults.copy()
                combined_defaults.update(result)
                bound_wrapper = self.wrap_model(v.model)
                try:
                    result[k] = self.run(bound_wrapper, _depth=_depth, **combined_defaults)
                except Exception as e:
                    # raise e
                    raise PvradarSdkError(
                        f'Error calculating argument {k} by running {bound_wrapper.name} caused by ...\n{e.__class__.__name__} {e}'
                    ) from e

        for k, v in result.items():
            if k in model.params:
                result[k] = self._process_input_param(model, model.params[k], v)

        return result

    @override
    def run(
        self,
        model: Callable | str,
        label: Optional[str] = None,
        _depth: int = 0,
        **kwargs,
    ):
        if (_depth := _depth + 1) > MAX_DEPTH:
            raise RecursionError(f'ModelContext.run max recursions reached: {MAX_DEPTH}')

        model = self.wrap_model(model)
        bound_params = self._process_input(model, _depth=_depth, **kwargs)

        if not self.config.get('disable_validation'):
            model.validate(**bound_params)

        old_all_kwargs = self.all_kwargs
        try:
            new_all_kwargs = kwargs.copy()
            new_all_kwargs.update(bound_params)
            if 'context' in new_all_kwargs:
                new_all_kwargs.pop('context')
            self.all_kwargs = new_all_kwargs
            result = model(**bound_params)
        except Exception as e:
            raise PvradarSdkError(f'Error while executing {model.name}: {e.__class__.__name__} {e}') from e
        finally:
            self.all_kwargs = old_all_kwargs

        result = self._process_output(model, bound_params, result)
        if label and is_series_or_frame(result):
            result.attrs['label'] = label
        return result

    def merge_config(self, config: Optional[ModelConfig]):
        if not config:
            return self.config
        result = self.config.copy()
        result.update(config)
        return result

    @override
    def resource(
        self,
        name: Any,
        *,
        attrs: Optional[Mapping[str, Any]] = None,
        label: Optional[str] = None,
        **kwargs,
    ) -> Any:
        if attrs is None:
            attrs = {}
        if isinstance(name, (dict, ResourceTypeClass, ResourceTypeDescriptor)):
            if attrs:
                raise ValueError(
                    'two attrs arguments provided, either use .resource(name, attrs={...atr}) or .resource({...attr})'
                )
            attrs = attrs_as_descriptor_mapping(name)
            name = '_anonymous'

        if label is not None:
            attrs = dict(attrs)
            attrs['label'] = label

        # if resource was requested as dict, then it was converted to _anonymous
        # so from here on name is only str
        assert isinstance(name, str), 'resource name must be a string'

        if name in self._resources:
            result = self._resources[name]
            if attrs:
                result = self._convert_by_attrs(result, attrs)
            return result
        v, new_as_param = self._bind_resource(name, as_param=ModelParam(name=name, annotation=None, attrs=attrs))

        if BindingNotFound.check(v):
            reported_attrs = attrs
            if new_as_param and new_as_param.attrs:
                reported_attrs = new_as_param.attrs
            if name == '_anonymous':
                raise LookupError(f'Unknown method to calculate resource for: {reported_attrs}')
            raise LookupError(f'Unknown method to calculate "{name}" with: {reported_attrs}')
        if isinstance(v, ModelBinding):
            combined_defaults = v.defaults.copy()
            if 'params' in attrs:
                combined_defaults.update(attrs['params'])
            combined_defaults.update(kwargs)
            v = self.run(v.model, **combined_defaults)

        if attrs:
            v = self._convert_by_attrs(v, attrs)
        return v

    def _bind_resource(
        self,
        name: str,
        as_param: Optional[ModelParam] = None,
        __config__: Optional[ModelConfig] = None,
        defaults: Optional[dict[str, Any]] = None,
    ) -> tuple[Any, Optional[ModelParam]]:
        if defaults is None:
            defaults = {}
        me = self
        if __config__:
            me = self.copy()
            me.config = self.merge_config(__config__)

        if as_param and as_param.attrs and 'params' in as_param.attrs:
            defaults = defaults.copy()
            defaults.update(as_param.attrs['params'])

        if name == 'context':
            return me, as_param
        elif name in me._resources:
            return me._resources[name], as_param

        if as_param and as_param.attrs:
            as_param, defaults = preprocess_bind_resource_input(context=self, as_param=as_param, defaults=defaults)

        for b in self.binders:
            result = b(resource_name=name, as_param=as_param, defaults=defaults, context=me)
            if BindingNotFound.check(result) or (result is None):
                continue
            if result is EmptyBinding:
                return None, as_param
            return result, as_param
        if self.mapping_by_resource_types and as_param and as_param.attrs and 'resource_type' in as_param.attrs:
            if as_param.attrs['resource_type'] in self.mapping_by_resource_types:
                return (
                    ModelBinding(
                        model=self.mapping_by_resource_types[as_param.attrs['resource_type']], defaults=defaults or {}
                    ),
                    as_param,
                )
        if as_param and as_param.default != inspect.Parameter.empty:
            return as_param.default, as_param
        return BindingNotFound, as_param

    def bind_params(
        self,
        *,
        params: dict[str, ModelParam],
        defaults: dict[str, Any],
        for_model: Optional[str] = None,
        __config__: Optional[ModelConfig] = None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        kwargs_applied = False
        for k in params.keys():
            if kwargs_applied:
                raise PvradarSdkError('kwargs must be the last parameter in the model signature')
            if k == 'return':
                continue
            elif params[k].is_var_keyword:
                kwargs_applied = True
                for key in defaults:
                    if key not in params and not isinstance(defaults[key], ModelBinding):
                        result[key] = defaults[key]  # there is no validation or any processing needed for kwargs
                continue
            elif k in defaults:
                result[k] = defaults[k]
            else:
                result[k], new_as_param = self._bind_resource(
                    name=k,
                    as_param=params[k],
                    defaults=defaults,
                    __config__=__config__,
                )

            if BindingNotFound.check(result[k]):
                config = self.merge_config(__config__)
                if 'ignore_missing_params' in config:
                    result.pop(k)
                    continue
                raise ValueError(
                    f'No default value for argument {k} in model {for_model}, known arguments with values: {list(defaults.keys())}'
                )
        return result

    # override this method to handle special resource types like location and interval
    def on_resource_set(self, key: str, value: Any) -> Any:
        if key in self._locks:
            raise PvradarSdkError(f'Cannot set "{key}", it is locked')
        return value

    def lock(self, key: str) -> None:
        if key in self._locks:
            self._locks[key] += 1
        else:
            self._locks[key] = 1

    def unlock(self, key: str) -> None:
        if key in self._locks:
            level = self._locks[key] - 1
            if level <= 0:
                del self._locks[key]
            else:
                self._locks[key] = level

    def check_locked(self, key: str) -> bool:
        return key in self._locks

    @override
    def __setitem__(self, key, value):
        if key == 'context':
            raise ValueError('Cannot set context, it always refers to self')
        elif key == 'return':
            raise ValueError('Cannot set "return". It is a reserved keyword')
        elif key == 'kwargs':
            raise ValueError('Cannot set "kwargs". It is a reserved keyword')
        value = self.on_resource_set(key, value)
        self._resources[key] = value

    @override
    def __getitem__(self, key):
        return self._resources[key]

    @override
    def __delitem__(self, key):
        del self._resources[key]

    @override
    def __contains__(self, key):
        return key in self._resources

    @override
    def __iter__(self):
        return iter(self._resources)

    @override
    def __len__(self):
        return len(self._resources)

    def copy(self) -> 'ModelContext':
        c = ModelContext()
        c.models = self.models.copy()
        c.binders = self.binders.copy()
        c._resources = self._resources.copy()
        c.mapping_by_resource_types = self.mapping_by_resource_types.copy()
        c.registered_hooks = self.registered_hooks
        return c

    def update(self, other: Mapping) -> None:
        self._resources.update(other)

    def make_objective_function(
        self,
        model: Callable | str,
        *,
        target: OptimizationTarget,
        param_names: list[str],
        _verbosity: int = 0,
        **kwargs,
    ) -> Callable:
        model = self.wrap_model(model)
        context = self.copy()

        def objective_function(params):
            param_dict = dict(zip(param_names, params))
            result = context.run(model, **kwargs, **param_dict)
            deviation = target.deviation(result)
            if pd.isna(deviation):
                raise ValueError(f'Optimization failed, got NaN as deviation, params: {param_dict}')
            if _verbosity > 0:
                print(f'params: {params}, deviation: {deviation}')
            return deviation

        return objective_function

    def _lambda_argument_reader(
        self,
        model_param: ModelParam,
    ):
        def reader():
            """Callback for ModelBinding of a LambdaArgument"""
            la = model_param.lambda_argument
            assert la is not None
            new_model_param = ModelParam(
                name='_anonymous',
                type=la.type,
            )
            subject = self._get_resource_by_param(new_model_param)
            result = la.callable(subject)
            if model_param.attrs:
                result = self._convert_by_attrs(result, model_param.attrs)
            return result

        return reader

    def _get_resource_by_param(self, param: ModelParam) -> Any:
        """For now only used for LambdaArgument"""
        v, new_as_param = self._bind_resource('_anonymous', as_param=param)

        if BindingNotFound.check(v):
            raise LookupError(f'Unknown method to calculate parameter {param}')
        if isinstance(v, ModelBinding):
            result = self.run(v.model, **v.defaults)
            return result
        else:
            return v

    def sweep(self, target: Callable | str | dict, dimensions: SweepRange | list[SweepRange], **kwargs) -> SyncSweepIterator:
        resolved_targets = []
        if isinstance(target, dict):
            resolved_targets.append(target)
        elif callable(target) or isinstance(target, str):
            resolved_targets.append(self.wrap_model(target))
        else:
            raise ValueError(f'Invalid sweep target {target}')

        if isinstance(dimensions, dict):
            dimensions = [dimensions]

        return SyncSweepIterator(
            context=self,
            _targets=resolved_targets,
            _ranges=dimensions,
            **kwargs,
        )

    def optimize(
        self,
        subject: Any,
        *,
        target: OptimizationTarget | pd.Series,
        parameters: Optional[list[str | ParameterConstraint]] = None,
        _verbosity: int = 0,
        _min_overlap_ratio: float = 0.1,  # at least 10% of target series must overlap with prediction
        **kwargs,
    ) -> dict[str, Any]:
        if 'param_names' in kwargs:
            warnings.warn('param_names is deprecated, use parameters instead', DeprecationWarning)
            if parameters:
                raise ValueError('Cannot provide both param_names and parameters. param_names is a deprecated alias')
            parameters = kwargs.pop('param_names')

        constraint_dict = {}
        str_parameters = []

        for_profiler_run = kwargs.copy()

        if parameters is not None:
            for p in parameters:
                if isinstance(p, dict):
                    if 'default' not in p:
                        p = p.copy()
                        p['default'] = ModelParam.get_default_from_bounds(p['bounds'])
                    constraint_dict[p['name']] = p
                    for_profiler_run[p['name']] = p['default']
                else:
                    str_parameters.append(p)

        if str_parameters or parameters is None:
            profiler = self.profile(subject, **for_profiler_run)
            parameter_dict = profiler.aggregate_parameters().as_parameter_dict()
            for parameter_name in parameter_dict.keys():
                if str_parameters and parameter_name not in str_parameters:
                    continue
                if parameters is None and parameter_name in kwargs:
                    # those parameters passed directly to our call are definitely not missing
                    continue
                constraint_dict[parameter_name] = parameter_dict[parameter_name].as_parameter_constraint()

        param_names = list(constraint_dict.keys())

        if not self.config.get('disable_validation'):
            unused_str_parameters = [x for x in str_parameters if x not in param_names]
            if unused_str_parameters:
                raise PvradarSdkError(f'the following parameters are not being used. Probably a typo? {unused_str_parameters}')

        if isinstance(target, pd.Series):
            target = OptimizationSeriesTarget(target)

        if isinstance(subject, (dict, ResourceTypeClass, ResourceTypeDescriptor)):
            attrs = attrs_as_descriptor_mapping(subject)
            v, x = self._bind_resource('_anonymous', as_param=ModelParam(name='_anonymous', annotation=None, attrs=attrs))
            if BindingNotFound.check(v):
                raise LookupError(f'Failed to find model for optimization subject: {subject}')
            if not isinstance(v, ModelBinding):
                raise ValueError(
                    f'For given subject {subject} a value was returned making model choice ambiguous.'
                    ' Please provide an explicit model as optimization target instead.'
                )

            model = v.model
        else:
            model = subject

        objective_function = self.make_objective_function(
            model,
            target=target,
            param_names=param_names,
            _verbosity=_verbosity,
            **kwargs,
        )

        opt_bounds = []
        start_vector = []
        for param_name in param_names:
            bounds = constraint_dict[param_name]['bounds']
            opt_bounds.append(bounds)
            default = 0
            if 'default' in constraint_dict[param_name]:
                default = constraint_dict[param_name]['default']
            else:
                default = ModelParam.get_default_from_bounds(bounds)
            start_vector.append(default)

        if not self.config.get('disable_validation'):
            validation_call_params = dict(for_profiler_run)
            validation_call_params.update(dict(zip(param_names, start_vector)))

            with self.use_profiler() as profiler:
                sample_prediction = self._run_or_get_resource(subject, **validation_call_params)
                if is_series_or_frame(sample_prediction):
                    overlapping_ratio = target.get_overlap_ratio(sample_prediction)
                    if overlapping_ratio < _min_overlap_ratio:
                        raise PvradarSdkError(
                            f'Not enough overlap between target and prediction: {overlapping_ratio:.2%} < {_min_overlap_ratio:.2%}'
                        )

            used_parameters = profiler.aggregate_parameters().as_parameter_dict()
            unused_parameters = []
            for param_name in param_names:
                if param_name not in used_parameters:
                    unused_parameters.append(param_name)
            if unused_parameters:
                raise PvradarSdkError(f'the following parameters are not being used. Probably a typo? {unused_parameters}')

        minimize_output = minimize(objective_function, start_vector, method='nelder-mead', bounds=opt_bounds)
        auto_result = dict(zip(param_names, minimize_output.x))
        return auto_result

    def use_profiler(self) -> PvradarProfiler:
        return PvradarProfiler(self)

    def _run_or_get_resource(self, subject: Any, **kwargs) -> Any:
        if isinstance(subject, (dict, ResourceTypeClass, ResourceTypeDescriptor)):
            return self.resource(subject, **kwargs)
        elif callable(subject) or isinstance(subject, str):
            return self.run(subject, **kwargs)
        else:
            raise ValueError(f'Unsupported subject type {type(subject)}')

    def profile(self, subject: Any, **kwargs) -> PvradarProfiler:
        with self.use_profiler() as profiler:
            self._run_or_get_resource(subject, **kwargs)
            return profiler

    @override
    def with_dependencies(
        self,
        resource: Any,
        dependencies: Any,
    ) -> Any:
        if is_series_or_frame(resource) and 'origin' in resource.attrs:
            dependency_dict = {}
            if isinstance(dependencies, dict):
                dependency_dict = dependencies
            elif isinstance(dependencies, list):
                for i in range(len(dependencies)):
                    dependency_dict[f'dependency_{i + 1}'] = dependencies[i]
            else:
                dependency_dict = {'single_dependency': dependencies}
            for value in dependency_dict.values():
                if is_series_or_frame(value):
                    value.attrs['is_nested_origin'] = True
            resource.attrs['nested_origins'] = dependency_dict
        return resource

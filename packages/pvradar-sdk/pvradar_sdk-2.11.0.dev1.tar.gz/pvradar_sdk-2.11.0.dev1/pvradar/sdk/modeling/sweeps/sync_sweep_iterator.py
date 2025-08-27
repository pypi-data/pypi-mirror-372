import pandas as pd
from typing import Any, Tuple, override

from pandas.api.types import is_dict_like
from ..model_wrapper import ModelWrapper
from ..base_model_context import BaseModelContext
from .sweep_types import SweepRange
from .range_iterator import PredictiveIterator, SweepMultiRangeIterator


class SyncSweepIterator(PredictiveIterator):
    def __init__(
        self,
        *,
        context: BaseModelContext,
        _targets: list[ModelWrapper],
        _ranges: list[SweepRange],
        **kwargs,
    ):
        self.context = context
        self.targets = _targets
        self.ranges = _ranges
        self.multi_iterator = SweepMultiRangeIterator(_ranges)
        self.extra_defaults = kwargs

    @override
    def __iter__(self):
        return self

    @override
    def __next__(self) -> Tuple[list[Any], list[Any]]:
        vector = next(self.multi_iterator)
        kwargs = {}
        for i, value in enumerate(vector):
            kwargs[self.ranges[i]['param_name']] = value
        model_result = []
        for target in self.targets:
            if isinstance(target, ModelWrapper):
                run_result = self.context.run(target, **self.extra_defaults, **kwargs)
            elif is_dict_like(target):
                run_result = self.context.resource(target, **self.extra_defaults, **kwargs)
            else:
                raise ValueError(f'Invalid sweep target: {target}')
            model_result.append(run_result)
        return (vector, model_result)

    @override
    def has_next(self) -> bool:
        return self.multi_iterator.has_next()

    def to_df(self) -> pd.DataFrame:
        param_names = [r['param_name'] for r in self.ranges]
        tuples = []

        target_names = []
        for t in self.targets:
            if isinstance(t, ModelWrapper):
                target_names.append(t.name)
            elif is_dict_like(t):
                if 'name' in t:
                    target_names.append(t['name'])
                elif 'resource_type' in t:
                    target_names.append(t['resource_type'])
                else:
                    if '_anonymous' in target_names:
                        raise ValueError(
                            'Cannot distinguish anonymous targets in sweep. '
                            + 'Please use "name" or "resource_type" in attributes describing the resource'
                        )
                    else:
                        target_names.append('_anonymous')
            else:
                raise ValueError(f'Invalid sweep target: {t}')

        result_dict = {}
        for model_name in target_names:
            result_dict[model_name] = []
        for vector, model_result in self:
            tuples.append(tuple(vector))
            for i, value in enumerate(model_result):
                result_dict[target_names[i]].append(value)
        index = pd.MultiIndex.from_tuples(tuples, names=param_names)
        df = pd.DataFrame(result_dict, index=index)
        return df

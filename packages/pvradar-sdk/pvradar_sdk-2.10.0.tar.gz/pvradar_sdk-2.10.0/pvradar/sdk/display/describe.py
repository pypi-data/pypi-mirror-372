from numbers import Number
from typing import Mapping, override
import pandas as pd


class ObjectDescription:
    def __init__(self, str_description):
        self.str_description = str_description

    @override
    def __str__(self):
        return self.str_description

    @override
    def __repr__(self):
        return self.str_description

    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return other + str(self)
        return NotImplemented


freq_dict = {
    's': 'secondly',
    't': 'minutely',
    'min': 'minutely',
    '1min': 'minutely',
    'h': 'hourly',
    '1h': 'hourly',
    'd': 'daily',
    'D': 'daily',
    '1D': 'daily',
    'w': 'weekly',
    'm': 'monthly',
    'M': 'monthly',
    'me': 'monthly',
    'ms': 'monthly',
    'q': 'quarterly',
    'a': 'yearly',
}

agg_dict = {
    'sum': 'total',
    'mean': 'mean',
    'p50': 'P50',
    'p90': 'P90',
    'min': 'minimum',
    'max': 'maximum',
}


def get_attrs_description(attrs: Mapping, *, quantity_placeholder: str = 'quantity') -> str:
    assert isinstance(attrs, Mapping), f'attrs should be a Mapping (e.g. a dict), got {type(attrs)}'
    chunks = []
    if attrs.get('measurement_group_id'):
        chunks.append('measured')

    if 'agg' in attrs and attrs['agg']:
        agg: str = attrs['agg']
        agg_str = agg_dict.get(agg, agg)
        chunks.append(agg_str)
    if 'freq' in attrs and attrs['freq']:
        freq: str = attrs['freq']
        freq_str = freq_dict.get(freq.lower(), freq)
        chunks.append(freq_str)

    quantity_name = quantity_placeholder

    if 'resource_type' in attrs:
        quantity_name = attrs['resource_type'].replace('_', ' ')
    if quantity_name:
        chunks.append(quantity_name)

    if 'unit' in attrs:
        unit: str = str(attrs['unit'])
        if unit == '1' or unit == 'dimensionless':
            chunks.insert(0, 'dimensionless')
        else:
            chunks.append(f'in {unit}')

    if attrs.get('measurement_group_id'):
        mg_id: str = attrs['measurement_group_id']
        chunks.append(f'({mg_id})')
    elif attrs.get('dataset'):
        dataset: str = attrs['dataset']
        if len(chunks) > 0:
            chunks.append(f'from {dataset}')
        else:
            chunks.append(dataset)
    elif attrs.get('datasource'):
        datasource: str = attrs['datasource']
        if len(chunks) > 0:
            chunks.append('from')
        chunks.append(datasource)

    return ' '.join(chunks)


def describe(resource, add_data_insights: bool = True):
    if isinstance(resource, (pd.Series, pd.DataFrame)):
        result = []
        if isinstance(resource, pd.DataFrame):
            result.append('DataFrame')
        if hasattr(resource, 'name') and resource.name:
            result.append(f'{resource.name}:')
        attrs = resource.attrs
        # aggregation
        if 'agg' in attrs:
            agg: str = attrs['agg']
            agg_str = agg_dict.get(agg, agg)
            result.append(agg_str)

        # frequency
        if 'freq' in attrs and attrs['freq']:
            freq: str = attrs['freq']
        else:
            try:
                freq: str = pd.infer_freq(resource.index) or ''  # type: ignore
            except Exception:
                # mute "cannot infer freq for index type ..." error
                freq = ''
            if not freq:
                freq = ''
        # should also be able to deal with '10T' which should result in '10 min'
        freq_str = freq_dict.get(freq.lower(), freq)
        result.append(freq_str)

        # resource type
        resource_type: str = attrs['resource_type'] if 'resource_type' in attrs else 'unknown resource'
        result.append(resource_type.replace('_', ' '))

        # unit
        if 'unit' in attrs:
            unit: str = str(attrs['unit'])
            if unit == '1':
                result.append('(dimensionless)')
            else:
                result.append(f'in {unit}')

        # source
        if 'datasource' in attrs:
            datasource: str = attrs['datasource']
            result.append(f'from {datasource}')
            if 'dataset' in attrs:
                result.append(f'({attrs["dataset"]})')

        if attrs.get('label'):
            result.append(f'labeled "{attrs["label"]}"')

        lines = [' '.join(result)]

        if isinstance(resource, pd.DataFrame):
            for col in resource.columns:
                column_line = str(describe(resource[col], add_data_insights=False))
                lines.append(f'- {column_line}')

        if add_data_insights:
            if len(resource):
                data_insights: list[str] = []
                data_insights.append(f'{len(resource)} data points')
                data_insights.append(f'({resource.index[0]} to {resource.index[-1]})')
                if isinstance(resource, pd.DataFrame):
                    data_insights.append(f'in {len(resource.columns)} columns')
                lines.append(' '.join(data_insights))
            else:
                lines.append('empty (has no data points)')

        return ObjectDescription('\n'.join(lines))

    elif isinstance(resource, str) or isinstance(resource, Number):
        return ObjectDescription(f'{repr(type(resource))}: {resource}')
    else:
        return ObjectDescription(repr(resource))

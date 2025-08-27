import json
from typing import Any, Mapping, override, Optional

from ..common.exceptions import PvradarSdkException


class ResourceTypeClass(type):
    standard = {'resource_type': 'any'}

    @override
    def __repr__(self) -> str:
        return f'<R.{self.standard["resource_type"]}>'

    @override
    def __str__(self) -> str:
        return str(self.standard['resource_type'])


class ResourceTypeDescriptor(metaclass=ResourceTypeClass):
    standard = {'resource_type': 'any'}

    def __init__(self):
        self._instance_attrs = {}
        raise PvradarSdkException(
            'ResourceTypeDescriptor should not be instantiated directly. Use R.<resource_type>(...) instead'
        )

    def __getitem__(self, key):
        return self._instance_attrs[key]

    def __contains__(self, key):
        return key in self._instance_attrs

    def __iter__(self):
        return iter(self._instance_attrs)

    def as_dict(self) -> dict:
        return self._instance_attrs

    def get(self, key: str, default=None):
        if isinstance(self, str):
            raise PvradarSdkException(
                'self in ResourceTypeDescriptor is str. Probably .get() called on ResourceTypeDescriptor class, instead of an instance'
            )
        return self._instance_attrs.get(key, default)

    @override
    def __str__(self) -> str:
        return self.__class__.__name__

    @override
    def __repr__(self) -> str:
        cloned = self._instance_attrs.copy()
        del cloned['resource_type']
        return f'<R.{self._instance_attrs["resource_type"]}:' + json.dumps(cloned, sort_keys=True) + '>'

    @staticmethod
    def make_attrs(
        *,
        resource_type: str,
        to_unit: Optional[str] = None,
        set_unit: Optional[str] = None,
        to_freq: Optional[str] = None,
        agg: Optional[str] = None,  # not using AggFunctionName to avoid circular dep.
        datasource: Optional[str] = None,
        **kwargs,
    ) -> dict:  # not using Attrs to avoid circular dep.
        """removes None, performs basic validation"""

        def _remove_none_values(d: dict[str, Any]) -> dict[str, Any]:
            return {k: v for k, v in d.items() if v is not None}

        result = _remove_none_values(
            dict(
                resource_type=resource_type,
                to_unit=to_unit,
                set_unit=set_unit,
                to_freq=to_freq,
                agg=agg,
                datasource=datasource,
            )
        )

        kwargs_dict = dict(kwargs)
        if kwargs_dict:
            result['params'] = _remove_none_values(kwargs_dict)

        if 'to_unit' in result and 'set_unit' in result:
            raise ValueError('to_unit and set_unit cannot be used together')
        return result


def attrs_as_descriptor_mapping(attrs: Any) -> Mapping[str, Any]:
    if isinstance(attrs, ResourceTypeDescriptor):
        return attrs.as_dict()
    elif isinstance(attrs, ResourceTypeClass):
        return {'resource_type': attrs.standard['resource_type']}
    elif isinstance(attrs, str):
        return {'resource_type': attrs}
    elif isinstance(attrs, Mapping):
        return attrs
    else:
        raise ValueError(f'Unsupported type for attrs: {type(attrs)}')


def match_attrs(subject_attrs: Any, against_attrs: Any) -> bool:
    subject_attrs = attrs_as_descriptor_mapping(subject_attrs)
    against_attrs = attrs_as_descriptor_mapping(against_attrs)
    fields = ['resource_type', 'agg', 'datasource']
    for field in fields:
        if field in against_attrs:
            if subject_attrs.get(field) != against_attrs[field]:
                return False
    return True

from typing import Mapping, TypeGuard, Union, TypedDict, Any, NotRequired

from pandas.api.types import is_dict_like
from ..modeling.basics import DataType


class ResourceSeriesMeta(TypedDict):
    resource_type: NotRequired[str]
    agg: NotRequired[str]
    unit: NotRequired[str]
    freq: NotRequired[str]
    label: NotRequired[str]


class DataCase(TypedDict):
    case_type: DataType


class DataCaseSeries(DataCase):
    data_type: DataType
    data: list[Union[int, float, str, None]]
    name: str
    meta: NotRequired[Mapping[str, Any]]
    index: NotRequired[list[Union[int, float, str, None]]]


class DataCaseTable(DataCase):
    columns: list[DataCaseSeries]
    meta: NotRequired[Mapping[str, Any]]


class DataCaseScalar(DataCase):
    data: Union[int, float, str, dict, None]
    meta: NotRequired[Mapping[str, Any]]


class JsonApiErrorSource(TypedDict):
    pointer: str


class JsonApiError(TypedDict):
    status: int
    source: JsonApiErrorSource
    code: NotRequired[str]
    detail: NotRequired[str]


def is_data_case(val: Any) -> TypeGuard[DataCase]:
    return is_dict_like(val) and 'case_type' in val


def is_data_case_series(val: Any) -> TypeGuard[DataCaseSeries]:
    return is_data_case(val) and val['case_type'] == 'series'


def is_data_case_table(val: Any) -> TypeGuard[DataCaseTable]:
    return is_data_case(val) and val['case_type'] == 'table'

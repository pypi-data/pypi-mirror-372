import numpy as np
from pydantic.fields import FieldInfo
from annotated_types import Gt, Ge, Lt, Le
import math
import copy
import inspect
from dataclasses import dataclass, field
from types import NoneType
from typing import (
    Any,
    Callable,
    Literal,
    Mapping,
    NotRequired,
    Optional,
    Self,
    Type,
    TypeGuard,
    TypeVar,
    TypedDict,
    get_args,
    override,
)

from .resource_types._list import PvradarResourceType, Datasource
from .resource_type_helpers import ResourceTypeClass

SPECIAL_FREQS = (
    'lowest',
    'highest',
    'default',
)

Confidentiality = Literal[
    'public',
    'private',
    'internal',
]

AggFunctionName = Literal[
    'sum',
    'mean',
    'std',
    'min',
    'max',
    'count',
    'first',
    'last',
    'median',
]

DataType = Literal[
    'any',
    'float',
    'int',
    'string',
    'datetime',  # normally pd.Timestamp
    'unix_timestamp',
    'sweep_range',
    'table',
    'series',
    'array',
    'dict',
]


def is_pvradar_resource_type(value: Any) -> TypeGuard[PvradarResourceType]:
    return value in get_args(PvradarResourceType.__value__)


type ResourceTypeExtended = PvradarResourceType | ResourceTypeClass


class BaseResourceAttrs(TypedDict):
    resource_type: NotRequired[str]
    datasource: NotRequired[str]


class ModelParamAttrs(BaseResourceAttrs):
    """Parameter attrs, also used in .resource() call"""

    to_unit: NotRequired[str]
    set_unit: NotRequired[str]
    to_freq: NotRequired[str]
    agg: NotRequired[AggFunctionName]

    source_id: NotRequired[str]

    label: NotRequired[str]
    keep: NotRequired[bool]

    params: NotRequired[Mapping[str, Any]]


class Attrs(ModelParamAttrs):
    """PVRADAR-specific attrs that use pvradar_resource_type unlike a generic resource_type"""

    resource_type: NotRequired[PvradarResourceType]  # pyright: ignore [reportIncompatibleVariableOverride]
    datasource: NotRequired[Datasource]  # pyright: ignore [reportIncompatibleVariableOverride]


def attrs(
    *,
    to_unit: Optional[str] = None,
    set_unit: Optional[str] = None,
    to_freq: Optional[str] = None,
    agg: Optional[AggFunctionName] = None,
    source_id: Optional[str] = None,
    label: Optional[str] = None,
    keep: Optional[bool] = None,
    params: Optional[Mapping[str, Any]] = None,
    resource_type: Optional[PvradarResourceType] = None,
    datasource: Optional[Datasource] = None,
) -> Attrs:
    result: Attrs = {}
    if to_unit is not None:
        result['to_unit'] = to_unit
    if set_unit is not None:
        result['set_unit'] = set_unit
    if to_freq is not None:
        result['to_freq'] = to_freq
    if agg is not None:
        result['agg'] = agg
    if source_id is not None:
        result['source_id'] = source_id
    if label is not None:
        result['label'] = label
    if keep is not None:
        result['keep'] = keep
    if params is not None:
        result['params'] = params
    if resource_type is not None:
        result['resource_type'] = resource_type
    if datasource is not None:
        result['datasource'] = datasource
    return result  # type: ignore


class SeriesAttrs(BaseResourceAttrs):
    freq: NotRequired[str]
    unit: NotRequired[str]
    agg: NotRequired[AggFunctionName]
    dataset: NotRequired[str]
    measurement_id: NotRequired[str]


class FrameAttrs(BaseResourceAttrs):
    freq: NotRequired[str]
    dataset: NotRequired[str]
    measurement_id: NotRequired[str]


class ModelConfig(TypedDict):
    disable_validation: NotRequired[bool]  # e.g. validation of attrs in model params
    disable_auto_resolve: NotRequired[bool]  # if true then context['model_name'] will NOT be resolved as ModelBinding
    ignore_missing_params: NotRequired[bool]  # model will be executed (run) even if some params are missing


class ModelRecipe(TypedDict):
    model_name: str
    params: NotRequired[Mapping[str, Any]]
    label: NotRequired[str]


class BindingNotFound:
    def __init__(self, reason: str = '') -> None:
        self.reason = reason

    @classmethod
    def check(cls, subject: Any) -> bool:
        return subject is BindingNotFound or isinstance(subject, cls)


class EmptyBinding:
    """marker object for binding returning None"""


LambdaSubject = TypeVar('LambdaSubject')


class LambdaArgument:
    def __init__(self, type: Type[LambdaSubject], callable: Callable[[LambdaSubject], Any]):
        self.type = type
        self.callable = callable


class ParameterConstraint(TypedDict):
    name: str
    bounds: tuple[float, float]
    type: NotRequired[Type]
    default: NotRequired[float]


@dataclass
class ModelParam:
    name: str = '_anonymous'
    annotation: Any = None
    attrs: Mapping[str, Any] = field(default_factory=dict)
    default: Optional[Any] = inspect.Parameter.empty
    type: Type = NoneType
    lambda_argument: Optional[LambdaArgument] = None
    is_var_keyword: bool = False

    @override
    def __repr__(self) -> str:
        result = self.name + ':' + self.type.__name__
        if self.default != inspect.Parameter.empty:
            if result.endswith('>'):
                result = result[:-1]
            result += f' = {self.default}'
        if result.startswith('<') and not result.endswith('>'):
            result += '>'
        return result

    def copy(self) -> Self:
        return copy.copy(self)

    def as_parameter_constraint(self) -> ParameterConstraint:
        bounds = self.make_bounds()
        return ParameterConstraint(
            name=self.name,
            type=self.type,
            bounds=bounds,
            default=self.get_optimization_default(bounds=bounds),
        )

    def make_bounds(self) -> tuple[float, float]:
        left_bound = -np.inf
        right_bound = np.inf
        if not self.annotation or not hasattr(self.annotation, '__metadata__'):
            return (left_bound, right_bound)
        for metadata in self.annotation.__metadata__:
            if isinstance(metadata, FieldInfo):
                for rule in metadata.metadata:
                    if isinstance(rule, Gt):
                        left_bound = math.nextafter(rule.gt, np.inf)  # type: ignore
                    elif isinstance(rule, Ge):
                        left_bound = rule.ge
                    elif isinstance(rule, Lt):
                        right_bound = math.nextafter(rule.lt, -np.inf)  # type: ignore
                    elif isinstance(rule, Le):
                        right_bound = rule.le
        return (left_bound, right_bound)  # type: ignore

    def get_optimization_default(self, *, bounds: Optional[tuple[float, float]] = None) -> float:
        if self.default is not inspect.Parameter.empty:
            if self.default is None:
                return 0.0
            return float(self.default)
        if bounds is None:
            bounds = self.make_bounds()

        return self.get_default_from_bounds(bounds)

    @classmethod
    def get_default_from_bounds(
        cls,
        bounds: tuple[float, float],
    ) -> float:
        if bounds[0] != -np.inf and bounds[1] != np.inf:
            return (bounds[0] + bounds[1]) / 2
        if bounds[0] != -np.inf:
            return bounds[0]
        if bounds[1] != np.inf:
            return bounds[1]

        return 0.0


def is_parameter_type(the_type: Type) -> bool:
    return the_type in (int, float)


@dataclass
class Audience:
    any_org: bool = False
    org_ids: list[str] = field(default_factory=list)
    project_goals: list[str] = field(default_factory=list)


class ResourceRecord(TypedDict):
    resource_type: PvradarResourceType
    attrs: NotRequired[dict[str, Any]]

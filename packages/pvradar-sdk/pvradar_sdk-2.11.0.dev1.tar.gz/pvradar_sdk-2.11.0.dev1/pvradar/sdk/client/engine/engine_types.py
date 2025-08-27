from typing import Mapping, Optional, Union, Literal, TypedDict, Dict, Any, NotRequired

from ...modeling.sweeps.sweep_types import SweepRange
from ...data_case.types import DataCase, JsonApiError
from ...modeling.basics import DataType, Attrs, PvradarResourceType, ModelRecipe


class LabeledEntity(TypedDict):
    name: str
    label: NotRequired[str]


class PydanticFieldSpec(TypedDict):
    description: NotRequired[str]
    lt: NotRequired[float]
    le: NotRequired[float]
    gt: NotRequired[float]
    ge: NotRequired[float]


class ModelParamSpec(LabeledEntity):
    data_type: DataType | list[DataType]
    attrs: NotRequired[Attrs]
    pydantic_field: NotRequired[PydanticFieldSpec]
    default: NotRequired[Any]


class ModelDefinition(LabeledEntity):
    resource_type: PvradarResourceType
    params: list[ModelParamSpec]


class ModelScenarioListRequest(TypedDict):
    scenario_name: NotRequired[str]
    project_id: NotRequired[str]
    tags: NotRequired[list[str]]


class ModelScenarioForm(TypedDict):
    scenario_name: str
    values: Mapping[str, Any]


class ScenarioEvaluationRequest(TypedDict):
    project_id: str
    scenario_form: ModelScenarioForm


EngineControlType = Literal[
    'subtitle',
    'text',
    'select',
    'radiogroup',
    'sweep_range',
]

EngineControlScope = Literal['project', 'model']


class ModelControl(LabeledEntity):
    param_name: NotRequired[str]
    param: NotRequired[ModelParamSpec]
    control_type: EngineControlType
    help: NotRequired[str]
    required: NotRequired[bool]
    default: NotRequired[Any]
    options: NotRequired[list[LabeledEntity]]
    scope: NotRequired[EngineControlScope]


class ModelScenario(LabeledEntity):
    definition: ModelDefinition
    controls: list[ModelControl]
    overrides: NotRequired[Dict[str, Any]]
    tags: NotRequired[list[str]]


class ModelContextLocator(TypedDict):
    id: Optional[str]
    project_id: NotRequired[str]
    variant_id: NotRequired[str]
    default_tz: NotRequired[str]
    interval: NotRequired[str]
    latitude: NotRequired[float]
    longitude: NotRequired[float]
    fixed_design_spec: NotRequired[dict[str, Any]]
    tracker_design_spec: NotRequired[dict[str, Any]]
    freq: NotRequired[str]


EngineResourceLinkType = Literal['hub_project_resource', 'assembly', 'model_run']


class AssemblyResourceLink(TypedDict):
    resource_link_type: Literal['assembly']
    assembly_request: Any


class HubProjectResourceLink(TypedDict):
    resource_link_type: Literal['hub_project_resource']
    resource_request: Any


class ModelRunResourceLink(TypedDict):
    resource_link_type: Literal['model_run']
    model_context_locator: ModelContextLocator
    model_recipe: ModelRecipe
    model_run_id: NotRequired[str]
    sweep_ranges: NotRequired[list[SweepRange]]


type ResourceLink = Union[AssemblyResourceLink, HubProjectResourceLink, ModelRunResourceLink]


class ModelRunMeta(TypedDict):
    model_run_id: NotRequired[str]
    model_context_locator: NotRequired[ModelContextLocator]
    filename: NotRequired[str]


class ModelRunResponse(TypedDict):
    data: NotRequired[DataCase]
    meta: NotRequired[ModelRunMeta]
    errors: NotRequired[list[JsonApiError]]


class ModelEvaluation(TypedDict):
    resource_links: list[ResourceLink]
    model_context_locator: NotRequired[ModelContextLocator]
    errors: NotRequired[list[JsonApiError]]

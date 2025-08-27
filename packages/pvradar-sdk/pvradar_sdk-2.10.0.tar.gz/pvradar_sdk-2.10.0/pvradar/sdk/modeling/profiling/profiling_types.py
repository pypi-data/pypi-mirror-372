from dataclasses import dataclass
from typing import NotRequired
from ..basics import ModelRecipe
from ..resource_types._list import Datasource


@dataclass
class ModelRunStats:
    model_name: str
    sum_execution_time: float = 0
    min_execution_time: float | None = None
    max_execution_time: float | None = None
    call_count: int = 0


class ResourceOrigin(ModelRecipe):
    resource_type: NotRequired[str]
    datasource: NotRequired[Datasource]
    label: NotRequired[str]

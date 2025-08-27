from typing import TypedDict, NotRequired, Any, Optional
from dataclasses import dataclass
import pandas as pd
from ..modeling.basics import SeriesAttrs


class MeasurementGroupRecord(TypedDict):
    id: str
    latitude: float
    longitude: float
    start_date: NotRequired[pd.Timestamp]
    end_date: NotRequired[pd.Timestamp]
    distance_km: NotRequired[float]
    freq: NotRequired[str]


class MeasurementRecipe(TypedDict):
    measurement_group_id: NotRequired[str]
    label: NotRequired[str]
    resource_type: str
    attrs: NotRequired[SeriesAttrs]  # if value is Series or DataFrame, the attrs will be applied on top of existing
    ops: list[dict[str, Any]]  # see op_pipeline.py for details


@dataclass(kw_only=True)
class MeasurementManifest:
    recipes: list[MeasurementRecipe]
    vars: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None
